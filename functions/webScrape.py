from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def get_text_from_webpage(url):
    req = Request(
        url=url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    # Remove all script and style elements
    for element in soup(['script', 'style']):
        element.decompose()

    # Define main content containers if necessary
    # You can add more tags or use class names to identify main content
    main_content = soup.find_all(['p', 'article', 'main', 'section'])

    # Extract and clean text from the main content
    paragraphs = [tag.get_text(separator='\n', strip=True) for tag in main_content]
    cleaned_text = '\n\n'.join(paragraphs)

    return cleaned_text
