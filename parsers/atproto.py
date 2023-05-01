from atprototools import Session
import os

USERNAME = os.environ.get("BSKY_USERNAME")
PASSWORD = os.environ.get("BSKY_PASSWORD")

session = Session(USERNAME, PASSWORD)
# session.post_bloot("skeet")
# session.post_bloot("here's an image!", "path/to/your/image")
# latest_bloot = session.get_latest_n_bloots('klatz.co',1).content
# carfile = session.get_car_file().content


def bloot(v):
    session.post_bloot(v)


def bloot2(v):
    return
