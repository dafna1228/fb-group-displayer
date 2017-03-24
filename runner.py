#!/usr/bin/env python
import facebook


TOKEN = "EAAbMxK2gORwBAMv5lZCHx9nRVPgBApZCGBqrjbK0rj3yJRmuQICiKLdqMJhgJnzUNsR0AveZBJlkJ8yRDG8s9oweZAuduZAJXu0KKQzBPUeamMxNgr0NU2RvBZB6ZBGPmlZAjNJWNUrsIhh2ZCcAt3QyLZAoGEcEMjyIsZD"
GID = "140579966013837"

print "StArTiNggg!!"

graph = facebook.GraphAPI(TOKEN)

groupData = graph.get_object(GID + "/feed", page=True, retry=3, limit=500)
print groupData

