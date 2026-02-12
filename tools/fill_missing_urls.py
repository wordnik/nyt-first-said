# import sys
# sys.path.append('.')
from search import search
import json
import os

# print(search("unh"))

with open("data/target_sites.json", "r") as f:
    sites_dict = json.loads(f.read())
    f.close()

count = 0
for k, site_obj in sites_dict.items():
    feeder_pages = site_obj["feeder_pages"]
    if len(feeder_pages) == 1 and feeder_pages[0] == "https://":
        # print(site_obj["site"])
        try:
            feeder_pages[0] = search(site_obj["site"])
            print(site_obj)
            count +=1
            # if count > 100:
            #     break
            # Paranoid write after every url found.
            with open("data/target_sites.json", "w") as f:
                f.write(json.dumps(sites_dict, indent=2))
                f.close()
        except Exception as e:
            print(f"Error {e} while searching for {site_obj['site']}.")

print(f"{count} urls filled.")
