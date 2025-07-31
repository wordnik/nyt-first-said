var { GetObjectCommand } = require('@aws-sdk/client-s3');

// #throws
async function streamFromBucket({
  s3Client,
  bucketName,
  key,
  allowedBodyContentTypes,
}) {
  // console.log('Starting to stream from bucket.');
  var command = new GetObjectCommand({ Bucket: bucketName, Key: key });
  // console.log('Built command with', bucketName, key);
  const { ContentType, Body } = await s3Client.send(command);
  // console.log('ContentType:', ContentType);

  if (!allowedBodyContentTypes.includes(ContentType)) {
    throw new Error(
      `Object at ${key} has an invalid content type: ${ContentType}`
    );
  }

  if (!Body) {
    throw new Error(`Failed to get Body for ${key}.`);
  }

  return Body;
}

module.exports = { streamFromBucket };
