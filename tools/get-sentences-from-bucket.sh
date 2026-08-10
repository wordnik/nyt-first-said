#!/bin/bash

date=$1
bucket=$2

mkdir -p sentences-tmp
rm -rf sentences-tmp/*

content=$(aws s3api list-objects-v2 --bucket ${bucket} \
  --query "Contents[?LastModified>='${date}T00:00:00+0'].Key" | jq -r ".[]")

# echo $content

for file in $content;
do
  echo "Key: ${file}"
  aws s3api get-object --bucket nyt-said-sentences --key $file sentences-tmp/$file
done

# for file in $content;
# do
#     cat sentences-tmp/$file | jq -r "{word: .word, text: .text, url: .url}"
# done
