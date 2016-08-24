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

    try:
        result = api.item_search('Books', Title=search_term, ResponseGroup='Images,ItemAttributes,BrowseNodes', ItemPage=page, paginate=False)
        return result
    except:
        return False

def process_result(search_result):
    """Given the result of an API search, process result for data."""

    if search_result:

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
                num_pages = item.ItemAttributes.NumberOfPages
                primary_node_id = item.BrowseNodes.BrowseNode.BrowseNodeId
                primary_node = item.BrowseNodes.BrowseNode.Name
                parent_node_id = item.BrowseNodes.BrowseNode.Ancestors.BrowseNode.BrowseNodeId
                parent_node = item.BrowseNodes.BrowseNode.Ancestors.BrowseNode.Name
            except AttributeError:
                title = ''
                author = ''
                md_image = ''
                lg_image = ''
            if len(title) > 0:
                results_list.append({'title': title, 'author': author, 'ASIN': asin,
                                     'md_image': md_image, 'lg_image': lg_image, 'URL': url, 'num_pages': num_pages,
                                     'primary_node_id': primary_node_id, 'primary_node': primary_node,
                                     'parent_node_id': parent_node_id, 'parent_node': parent_node})

        return results_list

def return_first_result(search_result):

    if search_result:

        result_items = search_result.Items.Item

        our_result = result_items[0]

        try:
            asin = our_result.ASIN
            url = our_result.DetailPageURL
            title = our_result.ItemAttributes.Title
            author = our_result.ItemAttributes.Author
            md_image = our_result.MediumImage.URL
            lg_image = our_result.LargeImage.URL
            num_pages = our_result.ItemAttributes.NumberOfPages
            primary_node_id = our_result.BrowseNodes.BrowseNode.BrowseNodeId
            primary_node = our_result.BrowseNodes.BrowseNode.Name
            parent_node_id = our_result.BrowseNodes.BrowseNode.Ancestors.BrowseNode.BrowseNodeId
            parent_node = our_result.BrowseNodes.BrowseNode.Ancestors.BrowseNode.Name
        except AttributeError:
                        title = ''
                        author = ''
                        md_image = ''
                        lg_image = ''

        if len(title) > 0:
            processed_result = {'title': title, 'author': author, 'ASIN': asin,
                                 'md_image': md_image, 'lg_image': lg_image, 'URL': url, 'num_pages': num_pages,
                                 'primary_node_id': primary_node_id, 'primary_node': primary_node,
                                 'parent_node_id': parent_node_id, 'parent_node': parent_node}

            return processed_result
        else:
            return None

