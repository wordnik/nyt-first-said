import boto3
dynamo = boto3.client("dynamodb")

def log_url_visit(url):
    res = dynamo.put_item(
            TableName="nyt-said-urls",
            Item={
                "url": {"S": url},
            })
    return res

def was_url_visited(url):
    res = dynamo.get_item(
            TableName="nyt-said-urls",
            Key={
                "url": {
                    "S": url
                    }
                }
            )

    item = res.get("Item", None)
    return item != None
