from atprototools import Session
import os

USERNAME = os.environ.get("BSKY_USERNAME")
USERNAME2 = os.environ.get("BSKY_USERNAME2")
PASSWORD = os.environ.get("BSKY_PASSWORD")
PASSWORD2 = os.environ.get("BSKY_PASSWORD2")

# print(USERNAME)
# print(USERNAME2)
# print(PASSWORD)
session = Session(USERNAME, PASSWORD)
session2 = Session(USERNAME2, PASSWORD2)

# session.post_bloot("skeet")
# session.post_bloot("here's an image!", "path/to/your/image")
# latest_bloot = session.get_latest_n_bloots('klatz.co',1).content
# carfile = session.get_car_file().content


def bloot(v):
    return session.post_bloot(v)


def bloot2(v, ref):
    return session2.post_bloot(v, reply_to=ref)
