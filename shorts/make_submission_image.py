import datetime
import os

from PIL import Image, ImageFont, ImageDraw

from shorts.config import _resources, _temp_path


def _split_string(text: str, index: int) -> int:
    while index >= 0 and text[index] != ' ':
        index -= 1
    return index


def _abbr_number(number: str) -> str:
    number = int(number)
    if number >= 10**10:
        return '{:.0f}B'.format(number / 10**9)
    elif number >= 10**9:
        return '{:.1f}B'.format(number / 10**9)
    elif number >= 10**7:
        return '{:.0f}M'.format(number / 10**6)
    elif number >= 10**6:
        return '{:.1f}M'.format(number / 10**6)
    elif number >= 10**4:
        return '{:.0f}k'.format(number / 10**3)
    elif number >= 10**3:
        return '{:.1f}k'.format(number / 10**3)
    else:
        return str(number)


def _relative_time(post_time: datetime.datetime) -> str:
    current_time = datetime.datetime.now()
    time_difference = current_time - post_time

    minutes = time_difference.total_seconds() / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = days / 365

    if years >= 1:
        return f"{int(years)} year{'s' if int(years) > 1 else ''} ago"
    elif months >= 1:
        return f"{int(months)} month{'s' if int(months) > 1 else ''} ago"
    elif weeks >= 1:
        return f"{int(weeks)} week{'s' if int(weeks) > 1 else ''} ago"
    elif days >= 1:
        return f"{int(days)} day{'s' if int(days) > 1 else ''} ago"
    elif hours >= 1:
        return f"{int(hours)} hr. ago"
    elif minutes >= 1:
        return f"{int(minutes)} mins ago"
    else:
        return "Just now"


def _generate_reddit_image(submission: dict, **kwargs) -> None:
    subreddit = str(submission.get('subreddit'))
    author = str(submission.get('author'))
    title = str(submission.get('title'))
    timestamp = submission.get('timestamp')
    score = int(submission.get('score'))
    comments = int(submission.get('num_comments'))

    template = Image.open(f"{_resources}/images/reddit_submission_template.png")
    submission_image = f"{_temp_path}/images/{author}.png"
    community_logo = f"{_resources}/images/subreddits/{subreddit.lower()}.png"
    default_community_logo = f"{_resources}/images/subreddits/default.png"

    if len(author) > 22:
        submission_author_formatted = author[:22]
        return submission_author_formatted

    else:
        author_formatted = author

    characters_to_linebreak = 37
    line_start = 0
    chunks = []

    while line_start < len(title):
        line_end = line_start + characters_to_linebreak

        if line_end < len(title):
            line_end = _split_string(title, line_end)
        chunks.append(title[line_start:line_end].strip())
        line_start = line_end + 1

    title_formatted = '\n'.join(chunks)
    line_break_count = title_formatted.count('\n')

    if line_break_count >= 3:
        third_line_break_index = title_formatted.find(
            '\n',
            title_formatted.find(
                '\n',
                title_formatted.find(
                    '\n'
                )
                + 1
            )
            + 1
        )

        title_formatted = title_formatted[:third_line_break_index]

    time_formatted = _relative_time(datetime.datetime.fromtimestamp(timestamp))

    score_formatted = _abbr_number(score)
    comments_formatted = _abbr_number(comments)

    font = "LiberationSans"
    draw = ImageDraw.Draw(template)
    twenty_pt_bold = ImageFont.truetype(f'{font}-Bold', 82)
    twenty_pt_reg = ImageFont.truetype(f'{font}-Regular', 82)
    twenty_six_pt_bold = ImageFont.truetype(f'{font}-Bold', 110)

    if os.path.exists(community_logo):
        community_image = Image.open(community_logo)
        community_image = community_image.resize((244, 244))

    else:
        community_image = Image.open(default_community_logo)
        community_image = community_image.resize((244, 244))

    template.paste(community_image, (222, 368), mask=community_image)

    draw.text((569, 459), author_formatted, (35, 31, 32,), font=twenty_pt_bold)

    author_length = draw.textlength(author_formatted, font=twenty_pt_bold)

    author_length_offset = 569 + author_length

    draw.ellipse(((author_length_offset + 36), 504,
                  (author_length_offset + 50), 518),
                 (35, 31, 32,))

    draw.text(((author_length_offset + 95), 459),
              time_formatted, (35, 31, 32,),
              font=twenty_pt_reg)

    draw.multiline_text((236, 672), title_formatted,
                        (35, 31, 32,), font=twenty_six_pt_bold, spacing=43.5
                        )

    if len(score_formatted) < 4:
        offset_needed = 4 - len(score_formatted)
        score_offset = offset_needed * 22

        draw.text((460+score_offset, 1253),
                  score_formatted, (35, 31, 32,),
                  font=twenty_pt_bold)

    else:
        draw.text((460, 1253), score_formatted,
                  (35, 31, 32,), font=twenty_pt_bold)

    if len(comments_formatted) < 4:
        offset_needed = 4 - len(comments_formatted)
        comments_offset = offset_needed * 24

        draw.text((1172+comments_offset, 1253),
                  comments_formatted, (35, 31, 32,),
                  font=twenty_pt_bold)

    else:
        draw.text((1172, 1253), comments_formatted,
                  (35, 31, 32,), font=twenty_pt_bold)

    if __name__ == "__main__":
        template.show()
    else:
        template.save(submission_image)


if __name__ == "__main__":
    _generate_reddit_image({
        'subreddit': '',
        'author': '',
        'title': '',
        'timestamp': '',
        'score': '',
        'num_comments': ''
    })
