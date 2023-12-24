from os.path import abspath, exists
from typing import List
import time
import pytz
import datetime

from selenium.webdriver.common.by import By

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

from tiktok_uploader.browsers import get_browser
from tiktok_uploader.auth import AuthBackend
from tiktok_uploader import config, logger
from tiktok_uploader.utils import bold, green, red
from tiktok_uploader.proxy_auth_extension.proxy_auth_extension import proxy_is_working


def upload_video(filename=None, description='', cookies='', schedule: datetime.datetime = None, username='',
                 password='', sessionid=None, cookies_list=None, cookies_str=None, proxy=None, *args, **kwargs):

    auth = AuthBackend(username=username, password=password, cookies=cookies,
                       cookies_list=cookies_list, cookies_str=cookies_str, sessionid=sessionid)

    return upload_videos(
            videos=[ { 'path': filename, 'description': description, 'schedule': schedule } ],
            auth=auth,
            proxy=proxy,
            *args, **kwargs
        )


def upload_videos(videos: list = None, auth: AuthBackend = None, proxy: dict = None, browser='',
                  browser_agent=None, on_complete=None, headless=False, num_retries : int = 1, *args, **kwargs):

    videos = _convert_videos_dict(videos)

    if videos and len(videos) > 1:
        logger.debug("Uploading %d videos", len(videos))

    if not browser_agent:  # user-specified browser agent
        logger.debug('Create a %s browser instance %s', browser, 'in headless mode' if headless else '')
        driver = get_browser(name=browser, headless=headless, proxy=proxy, *args, **kwargs)
    else:
        logger.debug('Using user-defined browser agent')
        driver = browser_agent
    if proxy:
        if proxy_is_working(driver, proxy['host']):
            logger.debug(green('Proxy is working'))
        else:
            logger.error('Proxy is not working')
            driver.quit()
            raise Exception('Proxy is not working')
    driver = auth.authenticate_agent(driver)

    failed = []

    for video in videos:
        try:
            path = abspath(video.get('path'))
            description = video.get('description', '')
            schedule = video.get('schedule', None)

            logger.debug('Posting %s%s', bold(video.get('path')), f'\n{" " * 15}with description: {bold(description)}' if description else '')

            if not _check_valid_path(path):
                print(f'{path} is invalid, skipping')
                failed.append(video)
                continue

            if schedule:
                timezone = pytz.UTC
                if schedule.tzinfo is None:
                    schedule = schedule.astimezone(timezone)
                elif int(schedule.utcoffset().total_seconds()) == 0:  # Equivalent to UTC
                    schedule = timezone.localize(schedule)
                else:
                    print(f'{schedule} is invalid, the schedule datetime must be naive or aware with UTC timezone, skipping')
                    failed.append(video)
                    continue

                valid_tiktok_minute_multiple = 5
                schedule = _get_valid_schedule_minute(schedule, valid_tiktok_minute_multiple)
                if not _check_valid_schedule(schedule):
                    print(f'{schedule} is invalid, the schedule datetime must be as least 20 minutes in the future, and a maximum of 10 days, skipping')
                    failed.append(video)
                    continue

            complete_upload_form(driver, path, description, schedule,
                                 num_retries=num_retries, headless=headless,
                                 *args, **kwargs)
        except Exception as exception:
            logger.error('Failed to upload %s', path)
            logger.error(exception)
            failed.append(video)

        if on_complete is callable:  # calls the user-specified on-complete function
            on_complete(video)

    if config['quit_on_end']:
        driver.quit()

    return failed


def complete_upload_form(driver, path: str, description: str, schedule: datetime.datetime, headless=False, *args, **kwargs) -> None:
    _go_to_upload(driver)
    #  _remove_cookies_window(driver)
    _set_video(driver, path=path, **kwargs)
    _remove_split_window(driver)
    _set_interactivity(driver, **kwargs)
    _set_description(driver, description)
    if schedule:
        _set_schedule_video(driver, schedule)
    _post_video(driver)


def _go_to_upload(driver) -> None:
    logger.debug(green('Navigating to upload page'))

    if driver.current_url != config['paths']['upload']:
        driver.get(config['paths']['upload'])

    else:
        _refresh_with_alert(driver)

    _change_to_upload_iframe(driver)

    root_selector = EC.presence_of_element_located((By.ID, 'root'))
    WebDriverWait(driver, config['explicit_wait']).until(root_selector)

    driver.switch_to.default_content()


def _change_to_upload_iframe(driver) -> None:
    iframe_selector = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['upload']['iframe'])
        )
    iframe = WebDriverWait(driver, config['explicit_wait']).until(iframe_selector)
    driver.switch_to.frame(iframe)


def _set_description(driver, description: str) -> None:
    if description is None:
        return

    logger.debug(green('Setting description'))

    description = description.encode('utf-8', 'ignore').decode('utf-8')

    saved_description = description  # save the description in case it fails

    desc = driver.find_element(By.XPATH, config['selectors']['upload']['description'])

    WebDriverWait(driver, config['explicit_wait']).until(lambda driver: desc.text != '')

    _clear(desc)

    try:
        while description:
            nearest_mention = description.find('@')
            nearest_hash = description.find('#')

            if nearest_mention == 0 or nearest_hash == 0:
                desc.send_keys('@' if nearest_mention == 0 else '#')

                name = description[1:].split(' ')[0]
                if nearest_mention == 0:  # @ case
                    mention_xpath = config['selectors']['upload']['mention_box']
                    condition = EC.presence_of_element_located((By.XPATH, mention_xpath))
                    mention_box = WebDriverWait(driver, config['explicit_wait']).until(condition)
                    mention_box.send_keys(name)
                else:
                    desc.send_keys(name)

                time.sleep(config['implicit_wait'])

                if nearest_mention == 0:  # @ case
                    mention_xpath = config['selectors']['upload']['mentions'].format('@' + name)
                    condition = EC.presence_of_element_located((By.XPATH, mention_xpath))
                else:
                    hashtag_xpath = config['selectors']['upload']['hashtags'].format(name)
                    condition = EC.presence_of_element_located((By.XPATH, hashtag_xpath))

                try:
                    elem = WebDriverWait(driver, config['implicit_wait']).until(condition)
                except:
                    desc.send_keys(Keys.BACKSPACE * (len(name) + 1))
                    description = description[len(name) + 2:]
                    continue

                ActionChains(driver).move_to_element(elem).click(elem).perform()

                description = description[len(name) + 2:]
            else:
                min_index = _get_splice_index(nearest_mention, nearest_hash, description)

                desc.send_keys(description[:min_index])
                description = description[min_index:]
    except Exception as exception:
        print('Failed to set description: ', exception)
        _clear(desc)
        desc.send_keys(saved_description)  # if fail, use saved description


def _clear(element) -> None:
    element.send_keys(2 * len(element.text) * Keys.BACKSPACE)


def _set_video(driver, path: str = '', num_retries: int = 3, **kwargs) -> None:
    logger.debug(green('Uploading video file'))

    for _ in range(num_retries):
        try:
            _change_to_upload_iframe(driver)
            upload_box = driver.find_element(
                By.XPATH, config['selectors']['upload']['upload_video']
            )
            upload_box.send_keys(path)
            upload_finished = EC.presence_of_element_located(
                (By.XPATH, config['selectors']['upload']['upload_finished'])
                )

            WebDriverWait(driver, config['explicit_wait']).until(upload_finished)
            upload_confirmation = EC.presence_of_element_located(
                (By.XPATH, config['selectors']['upload']['upload_confirmation'])
                )

            # An exception throw here means the video failed to upload an a retry is needed
            WebDriverWait(driver, config['explicit_wait']).until(upload_confirmation)
            # wait until a non-draggable image is found
            # process_confirmation = EC.presence_of_element_located(
            #     (By.XPATH, config['selectors']['upload']['process_confirmation'])
            #     )
            # WebDriverWait(driver, config['explicit_wait']).until(process_confirmation)
            return
        except Exception as exception:
            print(exception)

    raise FailedToUpload()


def _remove_cookies_window(driver) -> None:
    logger.debug(green('Removing cookies window'))
    cookies_banner = WebDriverWait(driver, config['implicit_wait']).until(
        EC.presence_of_element_located((By.TAG_NAME, config['selectors']['upload']['cookies_banner']['banner'])))

    item = WebDriverWait(driver, config['implicit_wait']).until(
        EC.visibility_of(cookies_banner.shadow_root.find_element(By.CSS_SELECTOR, config['selectors']['upload']['cookies_banner']['button'])))

    # Wait that the Decline all button is clickable
    decline_button = WebDriverWait(driver, config['implicit_wait']).until(
        EC.element_to_be_clickable(item.find_elements(By.TAG_NAME, 'button')[0]))

    decline_button.click()


def _remove_split_window(driver) -> None:
    logger.debug(green('Removing split window'))
    window_xpath = config['selectors']['upload']['split_window']

    try:
        condition = EC.presence_of_element_located((By.XPATH, window_xpath))
        window = WebDriverWait(driver, config['implicit_wait']).until(condition)
        window.click()

    except TimeoutException:
        logger.debug(red("Split window not found or operation timed out"))
    except Exception as e:
        logger.debug(red("Failed to remove split window"))


def _set_interactivity(driver, comment=True, stitch=True, duet=True, *args, **kwargs) -> None:
    try:
        logger.debug(green('Setting interactivity settings'))

        comment_box = driver.find_element(By.XPATH, config['selectors']['upload']['comment'])
        stitch_box = driver.find_element(By.XPATH, config['selectors']['upload']['stitch'])
        duet_box = driver.find_element(By.XPATH, config['selectors']['upload']['duet'])

        # xor the current state with the desired state
        if comment ^ comment_box.is_selected():
            comment_box.click()

        if stitch ^ stitch_box.is_selected():
            stitch_box.click()

        if duet ^ duet_box.is_selected():
            duet_box.click()

    except Exception as _:
        logger.error('Failed to set interactivity settings')


def _set_schedule_video(driver, schedule: datetime.datetime) -> None:
    logger.debug(green('Setting schedule'))

    driver_timezone = __get_driver_timezone(driver)
    schedule = schedule.astimezone(driver_timezone)

    month = schedule.month
    day = schedule.day
    hour = schedule.hour
    minute = schedule.minute

    try:
        switch = driver.find_element(By.XPATH, config['selectors']['schedule']['switch'])
        switch.click()
        __date_picker(driver, month, day)
        __time_picker(driver, hour, minute)
    except Exception as e:
        msg = f'Failed to set schedule: {e}'
        print(msg)
        logger.error(msg)
        raise FailedToUpload()


def __date_picker(driver, month: int, day: int) -> None:
    logger.debug(green('Picking date'))

    condition = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['schedule']['date_picker'])
        )
    date_picker = WebDriverWait(driver, config['implicit_wait']).until(condition)
    date_picker.click()

    condition = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['schedule']['calendar'])
    )
    calendar = WebDriverWait(driver, config['implicit_wait']).until(condition)

    calendar_month = driver.find_element(By.XPATH, config['selectors']['schedule']['calendar_month']).text
    n_calendar_month = datetime.datetime.strptime(calendar_month, '%B').month
    if n_calendar_month != month:  # Max can be a month before or after
        if n_calendar_month < month:
            arrow = driver.find_elements(By.XPATH, config['selectors']['schedule']['calendar_arrows'])[-1]
        else:
            arrow = driver.find_elements(By.XPATH, config['selectors']['schedule']['calendar_arrows'])[0]
        arrow.click()
    valid_days = driver.find_elements(By.XPATH, config['selectors']['schedule']['calendar_valid_days'])

    day_to_click = None
    for day_option in valid_days:
        if int(day_option.text) == day:
            day_to_click = day_option
            break
    if day_to_click:
        day_to_click.click()
    else:
        raise Exception('Day not found in calendar')

    __verify_date_picked_is_correct(driver, month, day)


def __verify_date_picked_is_correct(driver, month: int, day: int):
    date_selected = driver.find_element(By.XPATH, config['selectors']['schedule']['date_picker']).text
    date_selected_month = int(date_selected.split('-')[1])
    date_selected_day = int(date_selected.split('-')[2])

    if date_selected_month == month and date_selected_day == day:
        logger.debug(green('Date picked correctly'))
    else:
        msg = f'Something went wrong with the date picker, expected {month}-{day} but got {date_selected_month}-{date_selected_day}'
        logger.error(msg)
        raise Exception(msg)


def __time_picker(driver, hour: int, minute: int) -> None:
    logger.debug(green('Picking time'))

    condition = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['schedule']['time_picker'])
        )
    time_picker = WebDriverWait(driver, config['implicit_wait']).until(condition)
    time_picker.click()

    condition = EC.presence_of_element_located(
        (By.XPATH, config['selectors']['schedule']['time_picker_container'])
    )
    time_picker_container = WebDriverWait(driver, config['implicit_wait']).until(condition)

    # 00 = 0, 01 = 1, 02 = 2, 03 = 3, 04 = 4, 05 = 5, 06 = 6, 07 = 7, 08 = 8, 09 = 9, 10 = 10, 11 = 11, 12 = 12,
    # 13 = 13, 14 = 14, 15 = 15, 16 = 16, 17 = 17, 18 = 18, 19 = 19, 20 = 20, 21 = 21, 22 = 22, 23 = 23
    hour_options = driver.find_elements(By.XPATH, config['selectors']['schedule']['timepicker_hours'])
    # 00 == 0, 05 == 1, 10 == 2, 15 == 3, 20 == 4, 25 == 5, 30 == 6, 35 == 7, 40 == 8, 45 == 9, 50 == 10, 55 == 11
    minute_options = driver.find_elements(By.XPATH, config['selectors']['schedule']['timepicker_minutes'])

    hour_to_click = hour_options[hour]
    minute_option_correct_index = int(minute / 5)
    minute_to_click = minute_options[minute_option_correct_index]

    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", hour_to_click)
    hour_to_click.click()
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", minute_to_click)
    minute_to_click.click()

    # click somewhere else to close the time picker
    time_picker.click()

    time.sleep(.5)  # wait for the DOM change
    __verify_time_picked_is_correct(driver, hour, minute)


def __verify_time_picked_is_correct(driver, hour: int, minute: int):
    time_selected = driver.find_element(By.XPATH, config['selectors']['schedule']['time_picker_text']).text
    time_selected_hour = int(time_selected.split(':')[0])
    time_selected_minute = int(time_selected.split(':')[1])

    if time_selected_hour == hour and time_selected_minute == minute:
        logger.debug(green('Time picked correctly'))
    else:
        msg = f'Something went wrong with the time picker, ' \
              f'expected {hour:02d}:{minute:02d} ' \
              f'but got {time_selected_hour:02d}:{time_selected_minute:02d}'
        logger.error(msg)
        raise Exception(msg)


def _post_video(driver) -> None:
    logger.debug(green('Clicking the post button'))

    try:
        post = WebDriverWait(driver, config['implicit_wait']).until(EC.element_to_be_clickable((By.XPATH, config['selectors']['upload']['post'])))
        post.click()
    except ElementClickInterceptedException:
        logger.debug(green("Trying to click on the button again"))
        driver.execute_script('document.querySelector(".btn-post > button").click()')

    try:
        manage_your_post = WebDriverWait(driver, config['implicit_wait']).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div[2]/div[1]/div[9]/div/div[2]/div[2]')))
        manage_your_post.click()
    except ElementClickInterceptedException:
        logger.debug(green("Trying to click on the button again"))
        driver.execute_script('document.querySelector(".btn-post > button").click()')

    post_confirmation = EC.presence_of_element_located(
        (By.XPATH, '//*[@id="root"]/div[2]/div[2]/div/div/div[1]/span/span')
        )
    WebDriverWait(driver, config['explicit_wait']).until(post_confirmation)

    logger.debug(green('Video posted successfully'))


def _check_valid_path(path: str) -> bool:
    """
    Returns whether or not the filetype is supported by TikTok
    """
    return exists(path) and path.split('.')[-1] in config['supported_file_types']


def _get_valid_schedule_minute(schedule, valid_multiple) -> datetime.datetime:
    """
    Returns a datetime.datetime with valid minute for TikTok
    """
    if _is_valid_schedule_minute(schedule.minute, valid_multiple):
        return schedule
    else:
        return _set_valid_schedule_minute(schedule, valid_multiple)


def _is_valid_schedule_minute(minute, valid_multiple) -> bool:
    if minute % valid_multiple != 0:
        return False
    else:
        return True


def _set_valid_schedule_minute(schedule, valid_multiple) -> datetime.datetime:
    minute = schedule.minute

    remainder = minute % valid_multiple
    integers_to_valid_multiple = 5 - remainder
    schedule += datetime.timedelta(minutes=integers_to_valid_multiple)

    return schedule


def _check_valid_schedule(schedule: datetime.datetime) -> bool:
    valid_tiktok_minute_multiple = 5
    margin_to_complete_upload_form = 5

    datetime_utc_now = pytz.UTC.localize(datetime.datetime.utcnow())
    min_datetime_tiktok_valid = datetime_utc_now + datetime.timedelta(minutes=15)
    min_datetime_tiktok_valid += datetime.timedelta(minutes=margin_to_complete_upload_form)
    max_datetime_tiktok_valid = datetime_utc_now + datetime.timedelta(days=10)
    if schedule < min_datetime_tiktok_valid \
            or schedule > max_datetime_tiktok_valid:
        return False
    elif not _is_valid_schedule_minute(schedule.minute, valid_tiktok_minute_multiple):
        return False
    else:
        return True


def _get_splice_index(nearest_mention: int, nearest_hashtag: int, description: str) -> int:
    if nearest_mention == -1 and nearest_hashtag == -1:
        return len(description)
    elif nearest_hashtag == -1:
        return nearest_mention
    elif nearest_mention == -1:
        return nearest_hashtag
    else:
        return min(nearest_mention, nearest_hashtag)


def _convert_videos_dict(videos_list_of_dictionaries) -> List:
    if not videos_list_of_dictionaries:
        raise RuntimeError("No videos to upload")

    valid_path = config['valid_path_names']
    valid_description = config['valid_descriptions']

    correct_path = valid_path[0]
    correct_description = valid_description[0]

    def intersection(lst1, lst2):
        return list(set(lst1) & set(lst2))

    return_list = []
    for elem in videos_list_of_dictionaries:
        elem = {k.strip().lower(): v for k, v in elem.items()}

        keys = elem.keys()
        path_intersection = intersection(valid_path, keys)
        description_intersection = intersection(valid_description, keys)

        if path_intersection:
            path = elem[path_intersection.pop()]

            if not _check_valid_path(path):
                raise RuntimeError("Invalid path: " + path)

            elem[correct_path] = path
        else:
            for _, value in elem.items():
                if _check_valid_path(value):
                    elem[correct_path] = value
                    break
            else:
                raise RuntimeError("Path not found in dictionary: " + str(elem))

        if description_intersection:
            elem[correct_description] = elem[description_intersection.pop()]
        else:
            for _, value in elem.items():
                if not _check_valid_path(value):
                    elem[correct_description] = value
                    break
            else:
                elem[correct_description] = ''  # null description is fine

        return_list.append(elem)

    return return_list


def __get_driver_timezone(driver) -> pytz.timezone:
    """
    Returns the timezone of the driver
    """
    timezone_str = driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
    return pytz.timezone(timezone_str)


def _refresh_with_alert(driver) -> None:
    try:
        driver.refresh()

        # wait for the alert to appear
        WebDriverWait(driver, config['explicit_wait']).until(EC.alert_is_present())

        # accept the alert
        driver.switch_to.alert.accept()
    except:
        pass


class DescriptionTooLong(Exception):
    def __init__(self, message=None):
        super().__init__(message or self.__doc__)


class FailedToUpload(Exception):
    def __init__(self, message=None):
        super().__init__(message or self.__doc__)
