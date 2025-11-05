import os

def add_line(self, s):
  with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
    f.print(s + "\n")
    f.close()
