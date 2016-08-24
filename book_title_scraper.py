import urllib2
from bs4 import BeautifulSoup

# SCRAPE DATA FROM GOODREADS
def scrape_data():
    """Given link, scrape data."""

    link = "https://www.goodreads.com/list/show/6.Best_Books_of_the_20th_Century"
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page)

    return soup

def process_scraped_data(data):
    """Given scraped data, process and return book titles."""

    lst = data.find_all('a', class_='bookTitle')
    titles = []
    for item in lst:
        contents = item.contents
        raw_title = str(contents[1])
        new = raw_title.split('>')
        new = new[1].split('<')
        title = new[0]
        titles.append(title)

    return titles
