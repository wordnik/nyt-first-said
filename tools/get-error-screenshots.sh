#!/bin/bash

date=$1
limit=1000

if [ -z $date ]; then
  echo "You must specify a date. e.g. 2026-03-16"
  exit 1
fi

mkdir -p screenshots-tmp
rm -rf screenshots-tmp/*

content=$(aws s3api list-objects-v2 --bucket nyt-said-failure-reports \
  --query "Contents[?LastModified>='${date}T00:00:00+0'].Key" | jq -r ".[]")

echo $content

declare -i count=0

for file in $content;
do
    aws s3api get-object --bucket nyt-said-failure-reports --key $file screenshots-tmp/$file
    count+=1
    if ((count > limit)); then
      echo "Stopping at $limit files."
      exit 0
    fi
done
