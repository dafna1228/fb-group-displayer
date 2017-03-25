#!/usr/bin/env python
import facebook
import pprint

TOKEN = "EAAbMxK2gORwBAMv5lZCHx9nRVPgBApZCGBqrjbK0rj3yJRmuQICiKLdqMJhgJnzUNsR0AveZBJlkJ8yRDG8s9oweZAuduZAJXu0KKQzBPUeamMxNgr0NU2RvBZB6ZBGPmlZAjNJWNUrsIhh2ZCcAt3QyLZAoGEcEMjyIsZD"
# GID = "140579966013837" of uif
GID = "314412645435066"
print "StArTiNggg!!"
RES_FILE = "res_file.json"

graph = facebook.GraphAPI(TOKEN)

groupData = graph.get_object(GID + "/feed", page=True, retry=3, limit=20)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(groupData)
f = open(RES_FILE, 'wb')
f.write(str(groupData))
f.close()

