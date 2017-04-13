from elasticsearch import Elasticsearch
import collector
import pprint
import facebook
f = open('es_details.txt', 'r')
SERVER = f.readline()
es = Elasticsearch([{'host': SERVER, 'port': 443, 'use_ssl': True}])

pp = pprint.PrettyPrinter(indent=4)


#check elasticsearch is responding
print es.info()

f2 = open('facebook_details.txt', 'r')

TOKEN = f2.readline()
GID = f2.readline()
graph = facebook.GraphAPI(TOKEN)
post_docs=[]
#feed = graph.get_object(id=GID, since='1486935260', until='1489354460', fields='feed{created_time, from, reactions, message}')["feed"]
# Wrap this block in a while loop so we can keep paginating requests until
# finished.
#for post in feed['data']:
#    post_docs.append(collector.post_info(post))

#print len(post_docs)
#pprint.pprint(feed)
#upload posts

#description_doc = collector.get_group_description()

posts_doc_list = collector.get_group_posts("2017-01-20","2017-01-22")
print len(posts_doc_list)

for post in posts_doc_list:
    pp.pprint(post)

posts_doc_list = collector.get_group_posts_no_date("2017-01-20","2017-01-22")
print len(posts_doc_list)
print "first docs with no date:"
pp.pprint (posts_doc_list[:10])
print "lasts docs with no date::"
pp.pprint(posts_doc_list[-9:])

