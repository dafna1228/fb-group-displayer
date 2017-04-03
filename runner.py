#!/usr/bin/env python
import facebook
import pprint
import urllib2
from BeautifulSoup import BeautifulSoup


"""
TODO:
- get number of members- too hard and gross to write! :(

- get info on sub comments

-find out more info about posts
"""

f = open('details.txt', 'r')
TOKEN = f.readline()
GID = f.readline()
graph = facebook.GraphAPI(TOKEN)
pp = pprint.PrettyPrinter(indent=4)


"""
gets - ['feed']['data']["reactions"]["data"]
returns a list of dicts, containing a user name and their reaction
"""


def get_reactions(reacts):
    all_reacts = []
    for i in reacts:
        r = {
            'name': i['name'],
            'reaction': i['type']
        }
        all_reacts.append(r)
    return all_reacts


# parses the post id from an id given from the feed
def get_post_id(pid):
    return pid.split('_')[1]


"""
create a document containing the poster, id, time created, id, message, and dict of reactions
"""

def post_info(post):
    post_doc = {}
    post_doc["created_time"] = post["created_time"]
    post_doc["from"] = post["from"]["name"]
    post_doc["id"] = get_post_id(post["id"])
    try:
        post_doc["message"] = post["message"]
    except KeyError:
        post_doc["message"] = ""

    try:
        post_doc["reactions"] = get_reactions(post["reactions"]["data"])
    except KeyError:
        post_doc["reactions"] = []

    return post_doc


"""
create a document containing comment details- the poster, id, time created, id, message, and dict of reactions
"""

def comment_info(comment):
    comment_doc = {}
    comment_doc["created_time"] = comment["created_time"]
    comment_doc["from"] = comment["from"]["name"]
    comment_doc["id"] = comment["id"]
    comment_doc["message"] = comment["message"]
    comment_doc["comment_count"] = comment["comment_count"]
    comment_doc["like_count"] = comment["like_count"]

    return comment_doc

"""
create a document containing comment details- the poster, id, time created, id, message, and dict of reactions
"""

def reply_info(reply):
    reply_doc = {}
    reply_doc["created_time"] = reply["created_time"]
    reply_doc["from"] = reply["from"]["name"]
    reply_doc["id"] = reply["id"]
    reply_doc["message"] = reply["message"]
    reply_doc["parent_id"] = reply['parent']["id"]
    reply_doc["like_count"] = reply["like_count"]

    return reply_doc

"""
create a document containing the group name, description, number of members requests
TODO: get member count from the web, as well as admins
"""

def group_info(obj):
    group_doc = {}
    group_doc["name"] = obj["name"]
    group_doc["id"] = obj["id"]
    group_doc["decsription"] = obj["description"]
    group_doc["member_request_count"] = obj["member_request_count"]
    return group_doc


if __name__ == '__main__':
    #TOKEN = str(raw_input("Access token: "))
    #GID = str(raw_input("Group ID: "))

    feed = graph.get_object(id=GID,
                            fields='name, description, member_request_count,'
                                     'feed.limit(5){created_time, from, reactions, message}')
 #   print "printing whole feed:"
 #   pp.pprint(feed)

    all_posts = feed['feed']['data']
    print "\n group description:"
    pp.pprint(group_info(feed))
    for post in all_posts:
        post_doc = post_info(post)
        print "\n printing post in feed"
        pp.pprint(post_doc)
        comments = graph.get_connections(id=post_doc["id"],
                                             connection_name='comments')
        for comment in comments["data"]:
            comment_object = graph.get_object(id=comment["id"], fields='id, comment_count, from, like_count, '
                                                                     'created_time, message, parent')
            print "\n printing post comments info for post " + post_doc["id"]
            pp.pprint(comment_info(comment_object))
            if (comment_info(comment_object)["comment_count"] != 0):
                print "\n trying to print comment replies:"
                replies_info = graph.get_object(id=comment["id"], fields='comments{comments, from, id, message, like_count, parent, created_time}')
                #pp.pprint(replies_info)
                for reply in replies_info["comments"]["data"]:
                    reply_doc = reply_info(reply)
                    pp.pprint(reply_doc)

"""
def get_members(gid):
  #  print 'https://www.facebook.com/groups/' + gid + '/members/'
    page = urllib2.urlopen('https://www.facebook.com/groups/' + gid)
    print page.read()
    #soup = BeautifulSoup(page.read())
    #print soup.find('head')

"""