import re


def _title_video(submission, **kwargs) -> str:
    submission_title = submission.get('title')
    platform = kwargs.get('platform')

    if platform == "youtube":
        character_limit = 100

    else:
        character_limit = 2200

    title_hashtags = "#reddit #minecraft"

    truncated_limit = character_limit - len(title_hashtags) - 4

    if len(submission_title) >= truncated_limit:
        truncated_title = submission_title[:truncated_limit]
        if truncated_title.endswith(' '):
            truncated_title = truncated_title[:-1]

        video_title = f"{truncated_title}... {title_hashtags}"
    else:
        video_title = f"{submission_title} {title_hashtags}"

    print(video_title)
    return video_title


def _video_keywords(
        title: str,
        subreddit: str,
        additional_keywords: str = None
) -> list:
    # character limit is 500 on youtube
    cleaned_sentence = re.sub(r'[^\w\s]', '', title.lower())
    keywords = cleaned_sentence.split()
    unique_keywords = []
    keywords.append(subreddit)
    if additional_keywords is not None:
        additional_keys = additional_keywords.split(',')
        keywords.extend(additional_keys)

    for word in keywords:
        if word not in unique_keywords:
            unique_keywords.append(word)

    return unique_keywords


# start here
def _ai_title() -> str:
    try:
        from transformers import pipeline

    except ImportError:
        print("You do not have the required imports")

    model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
    pipe = pipeline("text-generation", model=model, device="mps")

    content = "this is a test just to see if its working :) hello world, how do you do?"

    messages = [
        {"role": "system", "content": "You are writing click bait video titles for a youtube video based on the content of the video", },
        {"role": "user", "content": f"{content}"},
    ]

    prompt = pipe.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    resp = pipe(prompt, max_new_tokens=128)
    # print(resp[0]['generated_text'])
    print(resp)


if __name__ == "__main__":
    _ai_title()
