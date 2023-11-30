from datetime import datetime
from atproto import Client, models
import os

USERNAME = os.environ.get("BSKY_USERNAME")
USERNAME2 = os.environ.get("BSKY_USERNAME2")
PASSWORD = os.environ.get("BSKY_PASSWORD")
PASSWORD2 = os.environ.get("BSKY_PASSWORD2")

# print(USERNAME)
# print(USERNAME2)
# print(PASSWORD)
session = Client()
session.login(USERNAME, PASSWORD)
session2 = Client()
session2.login(USERNAME2, PASSWORD2)

# session.post_bloot("skeet")
# session.post_bloot("here's an image!", "path/to/your/image")
# latest_bloot = session.get_latest_n_bloots('klatz.co',1).content
# carfile = session.get_car_file().content


def bloot(v):
    return session.send_post(text=v)


def bloot2(v, url, parent_post_ref):

    root_post_ref = models.create_strong_ref(parent_post_ref)
    reply_to = models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref)
    print(reply_to)
    # print type of reply_to


    url_start = v.find(':') + 1
    url_end = url_start + len(url)  # Assuming 'url' is the url in the text 'v'

    byte_start = len(v[:url_start].encode('UTF-8')) 
    byte_end = len(v[:url_end].encode('UTF-8'))

          
    facets = [
        models.AppBskyRichtextFacet.Main(
            features=[models.AppBskyRichtextFacet.Link(uri=url)],
            # we should pass when our link starts and ends in the text
            # the example below selects all the text
            index=models.AppBskyRichtextFacet.ByteSlice(byte_start=byte_start, byte_end=byte_end),
        )
    ]

    return session2.com.atproto.repo.create_record(
        models.ComAtprotoRepoCreateRecord.Data(
            repo=session2.me.did,  # or any another DID
            collection=models.ids.AppBskyFeedPost,
            record=models.AppBskyFeedPost.Main(created_at=datetime.now().isoformat(), text=v, facets=facets, reply=reply_to),
        )
    )
    
    # return session2.send_post(text=v, reply_to=parent_post_ref)

    # return session2.send_post(text=v, reply_to=models.AppBskyFeedPost.ReplyRef(parent_post_ref, parent_post_ref))
