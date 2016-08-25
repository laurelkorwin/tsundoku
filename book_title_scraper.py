import urllib2
from bs4 import BeautifulSoup
from search import setup_API, search_API, process_result, return_first_result
import time
from model import User, Book, Board, Node, Rating, Recommendation, Relationship
from model import connect_to_db, db
from tsundoku import check_for_node
from server import app

# SCRAPE DATA FROM GOODREADS
def scrape_data(link):
    """Given link, scrape data."""

    # opens link given and scrapes data into beautiful soup format
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page, "lxml")

    return soup

def process_scraped_data(data):
    """Given scraped data, process and return book titles."""
    # gets a list of all link elements with class "book title"
    lst = data.find_all('a', class_='bookTitle')

    # for each item in the list, goes through and picks the book title itself from their contents
    # then puts the title into larger list of titles
    titles = []
    for item in lst:
        contents = item.contents
        raw_title = str(contents[1])
        new = raw_title.split('>')
        new = new[1].split('<')
        title = new[0]
        titles.append(title)

    return titles

def process_scraped_scifi_data(data):

    lst = data.find_all('a', class_='bookTitle')

    # for each item in the list, goes through and picks the book title itself from their contents
    # then puts the title into larger list of titles
    titles = []
    for item in lst:
        contents = item.contents
        raw_title = str(contents[1])
        new = raw_title.split('>')
        new = new[1].split('<')
        title = new[0].split('(')
        title = title[0]
        titles.append(title)

    return titles

# lst_1 = process_scraped_data(scrape_data('https://www.goodreads.com/list/show/6.Best_Books_of_the_20th_Century'))

# lst_2 = process_scraped_data(scrape_data('https://www.goodreads.com/list/show/6.Best_Books_of_the_20th_Century?page=2'))

# lst_3 = process_scraped_data(scrape_data('https://www.goodreads.com/list/show/6.Best_Books_of_the_20th_Century?page=3'))

# lst_4 = process_scraped_scifi_data(scrape_data('https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books'))

# lst_5 = process_scraped_scifi_data(scrape_data('https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books?page=2'))

# SEARCH FUNCTION

def search_many(lst):
    """Given a list of book titles, searches API for title and returns the first result (an object) of each search."""
    results = []

    # for each item in the list:
    for item in lst:
    # sets a timer (so as not to break API usage limits)
        time.sleep(3)
    # searches the API for that title
        search = search_API(item)
    # of the results, returns just the first result and processes it into a dictionary format
        processed_search = return_first_result(search)
    # if the first result is not equal to none, appends it to the list of results
        if processed_search:
            results.append(processed_search)

    return results


def add_new_books_from_list(lst):
    """Given a list of dictionaries of book info, add book to DB if not currently there."""

    for book in lst:
        # queries DB to see if book already exists - if not, adds it
        book_exists = Book.query.filter_by(asin=str(book['ASIN'])).first()
        if book_exists is None:
            new_book = Book(asin=book['ASIN'], title=book['title'], author=book['author'], md_image=book['md_image'],
                            lg_image=book['lg_image'], url=book['URL'], num_pages=book['num_pages'],
                            primary_node_id=book['primary_node_id'], parent_node_id=book['parent_node_id'])
            # checks for book nodes in DB - if they are not there, adds them to db
            add_node_primary = check_for_node(str(book['primary_node_id']), str(book['primary_node']))
            add_node_parent = check_for_node(str(book['parent_node_id']), str(book['parent_node']))
            db.session.add(new_book)
            db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
