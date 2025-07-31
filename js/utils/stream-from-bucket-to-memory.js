var { concatStreamToBuffer } = require('./concat-stream-to-buffer.js');
var { streamFromBucket } = require('./stream-from-bucket');

// #throws
async function streamFromBucketToMemory({
  s3Client,
  bucketName,
  key,
  allowedBodyContentTypes
}) {
  var Body = await streamFromBucket({
    s3Client,
    bucketName,
    key,
    allowedBodyContentTypes
  });

  return await concatStreamToBuffer({ stream: Body });
}

module.exports = { streamFromBucketToMemory };
