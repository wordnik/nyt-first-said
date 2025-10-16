# -*- coding: utf-8 -*-
#!/usr/bin/python

# This is a script for testing the GitHub Actions environment.
import os
from dotenv import load_dotenv
import boto3

load_dotenv()
s3 = boto3.client("s3")

print(f"S3A length: {len(os.getenv('S3A'))}, Wordnik key length: {len(os.getenv('WORDNIK_API_KEY'))}")

s3.put_object(Bucket="nyt-said-sentences", Key="_a_test.txt",
              Body="Hey", ContentType="text/plain")
