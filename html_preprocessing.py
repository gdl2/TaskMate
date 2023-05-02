from bs4 import BeautifulSoup, Comment
import time

def preprocess_html(html):
    start_time = time.time()
    soup = BeautifulSoup(html, 'html.parser')

    # Remove style tags, script tags, link tags, and attributes except for class and id
    for tag in soup():
        if tag.name in ['style', 'script', 'link', 'meta']:
            tag.extract()
        else:
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr not in ['class', 'src', 'id']:
                    del tag[attr]

    # Remove comments
    for comment in soup(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove empty lines
    cleaned_html = '\n'.join(line for line in str(soup).splitlines() if line.strip())
    
    end_time = time.time()

    print("Time taken: {:.4f} seconds".format(end_time - start_time))
    print(cleaned_html)

    return cleaned_html