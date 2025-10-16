/* global process */
var { S3Client } = require('@aws-sdk/client-s3');
var { streamFromBucketToMemory, parseEvent } = require('sentence-utils');
var { esExampleSentenceSchema } = require('validation-library');
var VError = require('verror');

require('dotenv').config();

const elasticAPIKey = process.env.ELASTIC_API_KEY;
const indexJSONLine =
  JSON.stringify({ index: { _index: 'examples-epub-020225' } }) + '\n';

var allowedBodyContentTypes = ['application/json', 'application/octet-stream'];
const elasticBaseURL =
  'https://es-examples-042023.es.vpce.us-west-1.aws.elastic-cloud.com';

async function handler(event) {
  // console.log('event:', JSON.stringify(event, null, 2));

  try {
    const { bucket, key } = parseEvent(event);
    var s3Client = new S3Client();

    var buffer;

    try {
      buffer = await streamFromBucketToMemory({
        s3Client,
        bucketName: bucket.name,
        key,
        allowedBodyContentTypes,
      });
    } catch (error) {
      const message = `Error getting object ${key} from bucket ${bucket.name}.`;
      throw new VError(error, message);
    }

    var sentenceObj = [];

    try {
      const fileContents = buffer.toString('utf8');
      sentenceObj = JSON.parse(fileContents);
    } catch (error) {
      const message = `Error reading contents of ${key}.`;
      throw new VError(error, message);
    }

    var { error } = esExampleSentenceSchema.validate(sentenceObj);
    if (error) {
      throw new VError(error, 'Sentence object failed validattion.');
    }

    const authValues = 'ApiKey ' + elasticAPIKey;

    try {
      const bulkInitURL = elasticBaseURL + '/examples-epub-020225/_open';
      let res = await fetch(bulkInitURL, {
        headers: { Authorization: authValues },
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error(
          `Failure response to open elastic bulk posting: ${res.status}/${res.statusText}`
        );
      }
    } catch (error) {
      throw new VError(error, 'Open step of elastic bulk posting failed.');
    }

    var body;

    try {
      // const uploadURL = elasticBaseURL + '/_bulk';
      body = indexJSONLine + JSON.stringify(sentenceObj, null, 0) + '\n';
      console.log('Would have posted to elastic:', body);
      // let res = await fetch(uploadURL, {
      //   headers: {
      //     Authorization: authValues,
      //     'Content-Type': 'application/x-ndjson',
      //   },
      //   method: 'POST',
      //   body,
      // });
      // if (!res.ok) {
      //   throw new Error(
      //     `Failure response to elastic sentence upload: ${res.status}/${res.statusText}`
      //   );
      // }

      // const resText = await res.text();
      // if (res.ok) {
      //   console.log('Completed', body, res.status, resText);
      // } else {
      //   throw new Error(`Bulk upload failed: ${res.status} | ${resText}`);
      // }
    } catch (error) {
      throw new VError(error, 'Bulk upload failed.');
    }
  } catch (error) {
    // This gets us more detail than letting the error get caught outside this
    // function. AWS won't log the cause property on its own, for example.
    console.log(
      'Error caught at the top level in sentences-to-elastic:',
      error,
      error.stack
    );
    if (error.jse_cause) {
      console.log('jse_cause', JSON.stringify(error.jse_cause, null, 2));
    }
    throw error;
  }
}

module.exports = { handler };
