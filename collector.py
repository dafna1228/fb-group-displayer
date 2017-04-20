#!/usr/bin/env python
import facebook
import pprint
import requests
import time
"""

this collects facebook posts, comments, and comment replies in a spesific date range

TODO:
- get number of members- gross to write! :(

- more cleanup

- less printing

- figure out how to upload the docs
"""

f = open('facebook_details.txt', 'r')
TOKEN = f.readline()
GID = f.readline()
graph = facebook.GraphAPI(TOKEN)
pp = pprint.PrettyPrinter(indent=4)


"""
gets - ['feed']['data']["reactions"]["data"]
returns a list of dicts, containing a user name and their reaction
"""

def parse_reactions(reacts):
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
create a document containing the post info-  the user, id, time created, message, like count, comment count,
and dict of reactions
from the post dict created in the graph API
"""

def post_info(post):
    post_doc = {}
    post_doc["created_time"] = post["created_time"]
    post_doc["from"] = post["from"]["name"]
    post_doc["id"] = get_post_id(post["id"])
    post_doc["comment_count"] = post["comments"]["summary"]["total_count"]
    post_doc["like_count"] = post["likes"]["summary"]["total_count"]
    try:
        post_doc["message"] = post["message"]
    except KeyError:
        post_doc["message"] = ""

    try:
        post_doc["reactions"] = parse_reactions(post["reactions"]["data"])
    except KeyError:
        post_doc["reactions"] = []

    return post_doc


"""
create a document containing comment details- the user, id, time created, message, comment count ans like count
from the post dict created in the graph API
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
create a document containing reply details- the poster, id, time created, message, comment parent id and like count
from the post dict created in the graph API
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

def group_info(group):
    group_doc = {}
    group_doc["name"] = group["name"]
    group_doc["id"] = group["id"]
    group_doc["decsription"] = group["description"]
    group_doc["member_request_count"] = group["member_request_count"]
    return group_doc


"""
connects to facebook and returns a document containing the group details
"""

def get_group_description():
    feed = graph.get_object(id=GID, fields='name, description, member_request_count, feed.limit(1)')
    return group_info(feed)

"""
connects to facebook and returns a list of documents containing all the posts in the given group
"""

def get_all_group_posts():
    post_docs = []
    feed = graph.get_object(id=GID, fields='feed{created_time, from, reactions, message, likes.summary(true),'
                                           'comments.summary(true)}')["feed"]

    # Wrap this block in a while loop so we can keep paginating requests until
    # finished.
    while (True):
        try:
            for post in feed['data']:
                post_docs.append(post_info(post))
            # Attempt to make a request to the next page of data, if it exists.
            feed = requests.get(feed['paging']['next']).json()
        except KeyError:
            # When there are no more pages (['paging']['next']), break from the
            # loop and end the script.
            break

    return post_docs


"""
connects to facebook and returns a list of documents containing the posts in the given group, at a date range
parameter since, until, are string representing the date in format: yyyy-mm-dd 
"""

def get_group_posts_in_range(since, until):
    post_docs = []
    feed = graph.get_object(id=GID, since=since, until=until,
                            fields='feed{created_time, from, reactions, message, likes.summary(true),'
                                           'comments.summary(true)}')["feed"]
    # set cursor on given date range
    pattern = '%Y-%m-%d'
    since_epoch = str(int(time.mktime(time.strptime(since, pattern))))
    until_epoch = str(int(time.mktime(time.strptime(until, pattern))))
    url = feed['paging']['next'] + "&since=" + since_epoch + "&until=" + until_epoch

    # Wrap this block in a while loop so we can keep paginating requests until
    # finished.
    while (True):
        try:
            for post in feed['data']:
                post_docs.append(post_info(post))

            # Attempt to make a request to the next page of data, if it exists.
            feed = requests.get(url).json()
            url = feed['paging']['next']
        except KeyError:
            # When there are no more pages (['paging']['next']), break from the
            # loop and end the script.
            break

    return post_docs


"""
connects to facebook and returns a list of documents containing all the comments in the given post
"""

def get_group_comment(post):
    if (post["comment_count"] != 0):
        comment_docs = []
        comments = graph.get_connections(id=post["id"], connection_name='comments')
        # Wrap this block in a while loop so we can keep paginating requests until
        # finished.
        while (True):
            try:
                for comment in comments['data']:
                    comment_object = graph.get_object(id=comment["id"], fields='id, comment_count, '
                                                      'from, like_count, created_time, message, parent, '
                                                      'comments.limit(1000)')
                    comment_docs.append(comment_info(comment_object))
                # Attempt to make a request to the next page of data, if it exists.
                comments = requests.get(comments['paging']['next']).json()
            except KeyError:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                break

        return comment_docs


"""
connects to facebook and returns a list of documents containing all the replies in the given comment
"""

def get_group_reply(comment):
    if (comment["comment_count"] != 0):
        reply_docs = []
        replies = graph.get_object(id=comment["id"], fields='comments{comments, from, id, message, '
                                                                 'like_count, parent, created_time}')
        # Wrap this block in a while loop so we can keep paginating requests until
        # finished.
        while (True):
            try:
                for reply in replies["comments"]["data"]:
                    reply_docs.append(reply_info(reply))
                # Attempt to make a request to the next page of data, if it exists.
                replies = requests.get(replies['paging']['next']).json()
            except KeyError:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                break

        return reply_docs
