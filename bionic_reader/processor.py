import re
from bs4 import BeautifulSoup, NavigableString
from .utils import get_logger


def wrap_word(word, bold_ratio):
    """
    Wrap the first part of the word in a bold span.
    """
    if len(word) == 1:
        return f'<span class="bionic-prefix">{word}</span>'
        
    k = max(1, int(len(word) * bold_ratio))
    left = word[:k]
    right = word[k:]
    return f'<span class="bionic-prefix">{left}</span><span class="bionic-rest">{right}</span>'

def process_text_node(text, bold_ratio):
    if not text.strip():
        return None
        
    new_html = []
    last_index = 0
    # Find words (unicode aware)
    for m in re.finditer(r"(\w+)", text, flags=re.UNICODE):
        start, end = m.span()
        word = m.group(0)
        
        # Add non-word content before this word
        if start > last_index:
            new_html.append(text[last_index:start])
            
        # Add wrapped word
        new_html.append(wrap_word(word, bold_ratio))
        last_index = end
        
    # Add remaining text
    if last_index < len(text):
        new_html.append(text[last_index:])
        
    return "".join(new_html)

def apply_bionic_reading(html_content, bold_ratio=0.5):
    """
    Parse HTML and apply bionic reading formatting to text nodes.
    Returns modified HTML string.
    """
    logger = get_logger()
    logger.info("Applying Bionic Reading transformation...")
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # We want to modify text nodes in place. 
    # Recursive traversal is easiest with BS4.
    
    def recurse_replace(node):
        if hasattr(node, "children"):
            # List conversion needed because we might modify the tree
            for child in list(node.children):
                if isinstance(child, NavigableString):
                    if child.parent and child.parent.name not in ['script', 'style', 'title']:
                         new_html = process_text_node(str(child), bold_ratio)
                         if new_html:
                             # Create new soup fragment from the string
                             new_tag = BeautifulSoup(new_html, "html.parser")
                             child.replace_with(new_tag)
                else:
                    recurse_replace(child)

    body = soup.body
    if body:
        recurse_replace(body)
    else:
        recurse_replace(soup)
        
    return str(soup)
