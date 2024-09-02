from datetime import datetime
from atproto import Client, client_utils, models
import os

USERNAME = os.environ.get("BSKY_USERNAME")
USERNAME2 = os.environ.get("BSKY_USERNAME2")
PASSWORD = os.environ.get("BSKY_PASSWORD")
PASSWORD2 = os.environ.get("BSKY_PASSWORD2")

client = Client()
client.login(USERNAME, PASSWORD)
client2 = Client()
client2.login(USERNAME2, PASSWORD2)

def bloot(v):
    return client.send_post(text=v)

def bloot2(v, url, parent_post):
    text = client_utils.TextBuilder().text(v[:v.find(':') + 1]).link(url, url).text(v[v.find(':') + len(url) + 1:])
    
    return client2.send_post(
        text=text,
        reply_to=models.AppBskyFeedPost.ReplyRef(
            parent=models.ComAtprotoRepoStrongRef.Main(uri=parent_post.uri, cid=parent_post.cid),
            root=models.ComAtprotoRepoStrongRef.Main(uri=parent_post.uri, cid=parent_post.cid)
        )
    )
