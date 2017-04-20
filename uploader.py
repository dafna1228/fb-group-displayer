from elasticsearch import Elasticsearch
from elasticsearch import helpers
import collector
import pprint

f = open('es_details.txt', 'r')
SERVER = f.readline()
es = Elasticsearch([{'host': SERVER, 'port': 443, 'use_ssl': True}])

pp = pprint.PrettyPrinter(indent=4)
BULK_SIZE = 500
# check elasticsearch is responding
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
gets a list of bulks containing documents' and uploades them
assuming each doc has an "id" field
"""

def bulk_uploader(docs_list, index, type):
    bulk_list = list(chunks(docs_list, BULK_SIZE))
    for idx, bulk in enumerate(bulk_list):
        actions = []
        for doc in bulk:
            action = {
                "_index": index,
                "_type": type,
                "_id": doc["id"],
                "_source": doc
            }
            actions.append(action)
        helpers.bulk(es, actions)
        print "uploaded bulk ", idx + 1, " out of ", len(bulk_list)


if __name__ == '__main__':
    # upload_description()
    posts = collector.get_group_posts_in_range("2017-03-06", "2017-03-07")
    # bulk_uploader(posts, "posts_index", "post")

    # group all comments of all the posts, then make only one upload for all the comments
    comments = []
    for post in posts:
        if post["comment_count"] > 0:
            post_comments = collector.get_group_comment(post)
            for comment in post_comments:
                comments.append(comment)
    bulk_uploader(comments, "comments_index", "comment")

    replies = []
    for comment in comments:
        if comment["comment_count"] > 0:
            comment_replies = collector.get_group_reply(comment)
            for reply in comment_replies:
                replies.append(reply)
    bulk_uploader(replies, "replies_index", "reply")

