import os

def add_line(s):
  with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
    print(s + "\n", file=f)
    f.close()
