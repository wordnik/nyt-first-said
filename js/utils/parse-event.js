function parseEvent(event) {
  var eventS3 = event?.Records?.length > 0 && event.Records[0]?.s3;
  var bucket = eventS3?.bucket;
  if (!bucket) {
    // console.log doesn't block the thread in a lambda because this thread
    // instance isn't going to receive any more events before it's disposed.
    return new Error(`No valid bucket found in event ${event.id}`);
  }
  const key = decodeURIComponent(eventS3?.object?.key.replace(/\+/g, ' '));
  if (!key) {
    throw new Error(`No valid key found in event ${event.id}`);
  }
  const filePath = key.split(' ').pop();
  if (!filePath) {
    throw new Error(`No valid file path found in key ${key}`);
  }
  return { filePath, bucket, key };
}

module.exports = parseEvent;
