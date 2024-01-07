import datetime
import os

from PIL import Image, ImageFont, ImageDraw

from config import launcher_path
from scripts.utils import split_string_at_space, abbreviate_number, format_relative_time
# from utils import split_string_at_space, abbreviate_number, format_relative_time


# test values
# launcher_path = "/Users/gavinkondrath/projects/youtube_shorts/pyapp"
# submission_author = "gavink"
# submission_title = "This is a test"
# subreddit = "askreddit"
# submission_timestamp = 1703679574
# submission_score = 1
# submission_comments_int = 0


def generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int):
    # add flair
    subreddit_lowercase = subreddit.lower()

    story_template = Image.open(f"{launcher_path}/resources/images/reddit_submission_template.png")
    submission_image = f"{launcher_path}/temp/images/{submission_author}.png"
    community_logo_path = f"{launcher_path}/resources/images/subreddits/{subreddit_lowercase}.png"
    default_community_logo_path = f"{launcher_path}/resources/images/subreddits/default.png"

    if len(str(submission_author)) > 22:
        submission_author_formatted = str(submission_author)[:22]
        return submission_author_formatted
    else:
        submission_author_formatted = str(submission_author)

    characters_to_linebreak = 37
    start_index = 0
    chunks = []

    while start_index < len(submission_title):
        end_index = start_index + characters_to_linebreak
        if end_index < len(submission_title):
            end_index = split_string_at_space(submission_title, end_index)
        chunks.append(submission_title[start_index:end_index].strip())
        start_index = end_index + 1

    submission_title_formatted = '\n'.join(chunks)

    line_break_count = submission_title_formatted.count('\n')

    if line_break_count >= 3:
        third_line_break_index = submission_title_formatted.find('\n', submission_title_formatted.find('\n', submission_title_formatted.find('\n') + 1) + 1)
        submission_title_formatted = submission_title_formatted[:third_line_break_index]

    converted_time = datetime.datetime.fromtimestamp(submission_timestamp)
    submission_time_formatted = format_relative_time(converted_time)

    submission_score_formatted = abbreviate_number(submission_score)
    submission_comments_formatted = abbreviate_number(submission_comments_int)

    font = "LiberationSans"
    draw = ImageDraw.Draw(story_template)
    twenty_pt_bold = ImageFont.truetype(f'{font}-Bold', 82)
    twenty_pt_reg = ImageFont.truetype(f'{font}-Regular', 82)
    twenty_six_pt_bold = ImageFont.truetype(f'{font}-Bold', 110)

    if os.path.exists(community_logo_path):
        community_logo = Image.open(community_logo_path)
        community_logo = community_logo.resize((244, 244))

    else:
        community_logo = Image.open(default_community_logo_path)
        community_logo = community_logo.resize((244, 244))

    story_template.paste(community_logo, (222, 368), mask=community_logo)

    draw.text((569, 459), submission_author_formatted, (35, 31, 32,), font=twenty_pt_bold)

    author_length = draw.textlength(submission_author_formatted, font=twenty_pt_bold)

    author_length_offset = 569 + author_length

    draw.ellipse(((author_length_offset + 36), 504, (author_length_offset + 50), 518), (35, 31, 32,))

    draw.text(((author_length_offset + 95), 459), submission_time_formatted, (35, 31, 32,), font=twenty_pt_reg)

    draw.multiline_text((236, 672), submission_title_formatted, (35, 31, 32,), font=twenty_six_pt_bold, spacing=43.5)

    if len(submission_score_formatted) < 4:
        offset_needed = 4 - len(submission_score_formatted)
        score_offset = offset_needed * 22

        draw.text((460+score_offset, 1253), submission_score_formatted, (35, 31, 32,), font=twenty_pt_bold)

    else:
        draw.text((460, 1253), submission_score_formatted, (35, 31, 32,), font=twenty_pt_bold)

    if len(submission_comments_formatted) < 4:
        offset_needed = 4 - len(submission_comments_formatted)
        comments_offset = offset_needed * 24

        draw.text((1172+comments_offset, 1253), submission_comments_formatted, (35, 31, 32,), font=twenty_pt_bold)

    else:
        draw.text((1172, 1253), submission_comments_formatted, (35, 31, 32,), font=twenty_pt_bold)

    story_template.save(submission_image)

    # story_template.show()

# generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)
