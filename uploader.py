from elasticsearch import Elasticsearch
import collector
import pprint
f = open('es_details.txt', 'r')
SERVER = f.readline()
es = Elasticsearch([{'host': SERVER, 'port': 443, 'use_ssl': True}])

pp = pprint.PrettyPrinter(indent=4)


#check elasticsearch is responding
print es.info()

#upload posts

#description_doc = collector.get_group_description()

# all_posts_doc_list = collector.get_all_group_posts()

posts_doc_list = collector.get_group_posts_in_range("2017-01-01","2017-01-2")

pp.pprint(posts_doc_list[:-5])

print "working on some comments: "

for post in posts_doc_list[:5]:
    print "comments for post " + post["id"]
    com = collector.get_group_comment(post)
    pp.pprint(com)
    if com is not None:
        for comment in com:
            pp.pprint(collector.get_group_reply(comment))




