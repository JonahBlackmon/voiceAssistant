# from webScrape import get_text_from_webpage
from .webScrape import get_text_from_webpage
from .getSearch import get_url
import os


os.chdir("C:/Users/Jonah/Downloads/Projects")

def get_url_text(question):
    response = get_url(question)
    result = get_text_from_webpage(response)
    return result

