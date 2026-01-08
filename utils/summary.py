import os
import logging

def add_summary_line(s):
  with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
    print(s + "\n", file=f)
    f.close()
    logging.info(s)
