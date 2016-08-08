import os
import lxml
from amazonproduct import API

access_key = os.environ['AWS_ACCESS_KEY_ID']
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
associate_tag = os.environ['AWS_ASSOCIATE_TAG']

api = API(locale='us', access_key_id=access_key, secret_access_key=secret_key, associate_tag=associate_tag)


def item_search(term):

    item = api.item_search('Books', Title=term, ResponseGroup='Images,ItemAttributes', paginate=False)

    return item


def process_result(response):

    # results_dict = {}

    for book in response.Items.Item:
        # ASIN = book.ASIN
        try:
            title = book.ItemAttributes.Title
            author = book.ItemAttributes.Author
            md_image = book.MediumImage.URL
            lg_image = book.LargeImage.URL
        except AttributeError:
            title = ''
            author = ''
            md_image = ''
            lg_image = ''
        # results_dict[ASIN] = {'title': title, 'author': author, 'image': image_URL}
        print "Title: {}\nAuthor: {}\nMd Image URL: {}\nLg Image URL: {}\n".format(title, author, md_image, lg_image)
