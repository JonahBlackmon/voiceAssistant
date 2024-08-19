from googlesearch import search

def get_url(question):
    query = f"{question} -images -video -videos"

    for url in search(query, num=1, stop=1):
        print(url)
        return url
        
