import boto3
dynamo = boto3.client("dynamodb")

def reset_uninteresting_count_for_word(word):
    res = dynamo.put_item(
            TableName="nyt-said-uninteresting-words",
            Item={
                "word": {"S": word},
                "count": {"N": str(0)},
            })
    return res

def get_uninteresting_count_for_word(word):
    res = dynamo.get_item(
            TableName="nyt-said-uninteresting-words",
            Key={
                "word": {
                    "S": word
                    }
                }
            )

    item = res.get("Item", None)
    if item:
        return int(item.get("count", {}).get("N", 0))
    else:
        return 0

def increment_uninteresting_count_for_word(word):
    count = get_uninteresting_count_for_word(word)
    count += 1
    res = dynamo.put_item(
            TableName="nyt-said-uninteresting-words",
            Item={
                "word": {"S": word},
                "count": {"N": str(count)},
            })
    return res


