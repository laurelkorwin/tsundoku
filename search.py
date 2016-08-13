"""API SEARCH"""

import os
import lxml
from amazonproduct import API
import collections

def setup_API():
    """Setup API connection."""

    access_key = os.environ['AWS_ACCESS_KEY_ID']
    secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    associate_tag = os.environ['AWS_ASSOCIATE_TAG']

    api = API(locale='us', access_key_id=access_key, secret_access_key=secret_key, associate_tag=associate_tag)

    return api

def search_API(search_term, page=1):
    """Search API given a search term."""

    api = setup_API()

    result = api.item_search('Books', Title=search_term, ResponseGroup='Images,ItemAttributes', ItemPage=page, paginate=False)

    return result

def process_result(search_result):
    """Given the result of an API search, process result for data."""

    result_items = search_result.Items.Item

    results_dict = collections.OrderedDict()

    results_list = []

    for item in result_items:
        try:
            asin = item.ASIN
            url = item.DetailPageURL
            title = item.ItemAttributes.Title
            author = item.ItemAttributes.Author
            md_image = item.MediumImage.URL
            lg_image = item.LargeImage.URL
        except AttributeError:
            title = ''
            author = ''
            md_image = ''
            lg_image = ''
        if len(title) > 0:
            results_list.append({'title': title, 'author': author, 'ASIN': asin,
                                 'md_image': md_image, 'lg_image': lg_image, 'URL': url})

    return results_list
