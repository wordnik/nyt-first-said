/* global Buffer */

// body is expected to be a Body from GetObjectOutput:
// https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-s3/modules/getobjectoutput.html#body
// #throws
function concatStreamToBuffer({ stream }) {
  var chunks = [];
  return new Promise(executor);

  function executor(resolve, reject) {
    stream.on('end', passConcatenatedChunks);
    stream.on('error', reject);
    stream.on('data', saveChunk);

    function passConcatenatedChunks() {
      resolve(Buffer.concat(chunks));
    }
  }

  function saveChunk(chunk) {
    chunks.push(chunk);
  }
}

module.exports = { concatStreamToBuffer };
