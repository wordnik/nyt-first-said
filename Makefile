
# Install helpers

install-textblob:
	mkdir -p venv/share/nltk_data
	NLTK_DATA=venv/share/nltk_data ./venv/bin/python -m textblob.download_corpora lite

run-test:
	venv/bin/python -m unittest -v test.test_fill_out_sentence_object
	venv/bin/python -m unittest -v test.test_pos
	venv/bin/python -m unittest -v test.test_word_count_cache

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
