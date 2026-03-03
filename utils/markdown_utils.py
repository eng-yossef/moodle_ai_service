import markdown

def to_html(text: str) -> str:
    return markdown.markdown(text)