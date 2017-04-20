from elasticsearch import Elasticsearch
from elasticsearch import helpers
import collector
import pprint
import pprofile


f = open('es_details.txt', 'r')
SERVER = f.readline()
es = Elasticsearch([{'host': SERVER, 'port': 443, 'use_ssl': True}])

pp = pprint.PrettyPrinter(indent=4)
BULK_SIZE = 500
#check elasticsearch is responding
print es.info()


def costume_index():
    request_body = {"settings": {"number_of_shards": 1}}
    es.indices.create(index='description_index', body=request_body)

def upload_description():
    description_doc = collector.get_group_description()
    es.index(index="description_index", doc_type='description', id=1, body=description_doc)

"""Yield successive n-sized chunks from l."""
def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

"""
upload to es documents containing posts in the given group, in a time range
parameter since, until, are string representing the date in format: yyyy-mm-dd 
"""

def upload_posts_in_range(since, until):
    posts_doc_list = collector.get_group_posts_in_range(since, until)
    #create sub lists, so we can bulk index the documents, about 500 docs at a time
    bulk_list = list(chunks(posts_doc_list, BULK_SIZE))
    for bulk in bulk_list:
        actions=[]
        for doc in bulk:
            action = {
                "_index": "posts_index",
                "_type": "post",
                "_id": doc["id"],
                "_source": doc
            }
            actions.append(action)
        helpers.bulk(es, actions)


"""
upload to es documents containing all the posts in the given group
"""

def upload_all_posts():
    posts_doc_list = collector.get_all_group_posts()
    # create sub lists, so we can bulk index the documents, about 500 docs at a time
    bulk_list = list(chunks(posts_doc_list, BULK_SIZE))
    for bulk in bulk_list:
        actions = []
        for doc in bulk:
            action = {
                "_index": "posts_index",
                "_type": "post",
                "_id": doc["id"],
                "_source": doc
            }
            actions.append(action)
        helpers.bulk(es, actions)

posts_list = collector.get_group_posts_in_range("2017-04-04","2017-04-05")
#def upload_comments(posts_list):

comments_doc_list = []
for post in posts_list:
    if post["comment_count"] > 0:
        post_comments = collector.get_group_comment(post)
        for comment in post_comments:
            comments_doc_list.append(comment)
bulk_list = list(chunks(comments_doc_list, BULK_SIZE))
for bulk in bulk_list:
    actions = []
    for doc in bulk:
        action = {
            "_index": "comments_index",
            "_type": "comment",
            "_id": doc["id"],
            "_source": doc
        }
        actions.append(action)
    helpers.bulk(es, actions)

"""
 all_posts_doc_list = collector.get_all_group_posts()

pp.pprint(posts_doc_list[:-5])

# upload comments
for post in posts_doc_list[:5]:
    print "comments for post " + post["id"]
    com = collector.get_group_comment(post)
    pp.pprint(com)
    if com is not None:
        for comment in com:
            pp.pprint(collector.get_group_reply(comment))
"""



