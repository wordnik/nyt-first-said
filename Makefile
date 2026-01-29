TODAY=(date -24hours)
# Install helpers

install-textblob:
	mkdir -p venv/share/nltk_data
	NLTK_DATA=venv/share/nltk_data ./venv/bin/python -m textblob.download_corpora lite

# Lambda deployment
#
zip:
	cd js && \
	rm -f index.zip && \
	zip \
    -r index.zip \
      *.js \
      package.json \
      node_modules \
      storage/*.js \
      utils/*.js \
      utils/*.json \
      transforms/*.js \
      routes/*.js

# Depends on `aws` being installed. See README.md.
push-lambda: zip
	aws lambda update-function-code \
    --function-name $(fnName) \
    --zip-file fileb://js/index.zip \
    --region us-west-1

push-sentences-to-elastic:
	fnName=nyt-sentences-to-elastic make push-lambda

create-elastic-lambda:
	aws lambda create-function \
    --function-name nyt-sentences-to-elastic \
    --code S3Bucket=epub-pipeline-src,S3Key=index.zip \
    --region us-west-1 \
		--role arn:aws:iam::054978852993:role/service-role/epubFilterSentencesRole \
		--runtime nodejs18.x \
		--handler routes/sentences-to-elastic.handler

drop-sentence-to-trigger-lambda:
	aws s3api delete-object --bucket nyt-said-sentences --key nyt-example-sentence.json
	aws s3api put-object --bucket nyt-said-sentences --key nyt-example-sentence.json \
    --body meta/examples/nyt-example-sentence.json --content-type application/json

generate-launcher:
	node js/tools/generate-launcher-action.js data/target_sites.json > .github/workflows/daily_launcher.yml

build-bloom:
	python -m tools.build-bloom-filter -f data/nospace-examplesWords20250910.json -o data/bloom_filter.bits

update-working-sites:
	node js/tools/sync-sites-with-db.js data/target_sites.json
	node js/tools/generate-launcher-action.js data/target_sites.json .github/workflows/daily_launcher
	node js/tools/generate-launcher-action.js data/target_sites.json .github/workflows/unproven_sites_launcher false "Unproven sites launcher"

get-failure-screenshots:
	aws s3 sync s3://nyt-said-failure-reports/ meta/failure-reports/

list-files-dropped-in-last-day:
	aws s3api list-objects-v2 --bucket nyt-said-sentences \
	  --query "Contents[?LastModified>='$(TODAY)T00:00:00+0'].Key"
