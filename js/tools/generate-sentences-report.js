#!/usr/bin/env node

var {
  S3Client,
  paginateListObjectsV2,
  S3ServiceException,
  GetObjectCommand,
} = require('@aws-sdk/client-s3');
var fs = require('fs');

// TODO:
// kaikki entries
// s3-epub entries

/* global process */

const header = '|Word|Sentence|Source|Filename|Date|\n|--|--|--|--|--|\n';

if (process.argv.length < 3) {
  console.error(
    'Usage: GITHUB_STEP_SUMMARY=path-to-file.txt node tools/generate-sentences-report.js <days back to go> [branch]'
  );
  process.exit(1);
}

var s3Client = new S3Client();
const summaryPath = process.env.GITHUB_STEP_SUMMARY;
const daysBack = +process.argv[2];

var endDate = new Date();
// We want to include entries from today.
endDate.setDate(endDate.getDate() + 1);
endDate.setHours(0);
endDate.setMinutes(0);
endDate.setSeconds(0);

var startDate = new Date(endDate);
startDate.setDate(endDate.getDate() - daysBack);

var branch = 'master';
if (process.argv.length > 3) {
  branch = process.argv[3];
}
console.error(
  'Getting sentences from',
  startDate,
  'to',
  endDate,
  'for branch',
  branch
);

getObjects({ bucketName: 'nyt-said-sentences' });

async function getObjects({ bucketName }) {
  var objectPages = [];

  var listObjectOpts = { Bucket: bucketName };
  if (branch) {
    listObjectOpts.Prefix = branch + '/';
    listObjectOpts.Delimiter = '/';
  }

  try {
    const paginator = paginateListObjectsV2(
      { client: s3Client, pageSize: 100 },
      listObjectOpts
    );
    for await (const page of paginator) {
      if (!page.Contents) {
        continue;
      }
      let contentsInRange = page?.Contents?.filter((c) => {
        let contentsDate = new Date(c.LastModified);
        return contentsDate >= startDate && contentsDate < endDate;
      });
      objectPages.push(
        contentsInRange?.map((o) => ({
          key: o.Key,
          date: new Date(o.LastModified),
        }))
      );
    }
    for (let pageNum = 0; pageNum < objectPages.length; ++pageNum) {
      await getEntryDetails(objectPages[pageNum], pageNum, bucketName);
    }

    if (summaryPath) {
      fs.writeFileSync(summaryPath, header, { encoding: 'utf8' });
    } else {
      process.stdout.write(header);
    }

    objectPages.flat().forEach(reportEntry);
  } catch (caught) {
    if (
      caught instanceof S3ServiceException &&
      caught.name === 'NoSuchBucket'
    ) {
      console.error(
        `Error from S3 while listing objects for "${bucketName}". The bucket doesn't exist.`
      );
    } else {
      console.error(
        `Error from S3 while listing objects for "${bucketName}".  ${caught.name}: ${caught.message}`
      );
    }
  }
}

async function getEntryDetails(objectList, pageNum, bucketName) {
  for (let obj of objectList) {
    try {
      let getCommand = new GetObjectCommand({
        Bucket: bucketName,
        Key: obj.key,
      });
      let res = await s3Client.send(getCommand);
      const entryString = await res.Body.transformToString();
      let entry = JSON.parse(entryString);
      obj.word = entry?.word;
      obj.sentence = entry?.text;
      obj.source = entry?.metadata?.source;
    } catch (error) {
      console.error(
        'Error while getting details for',
        obj.key,
        'entry:',
        error
      );
    }
  }
}

function reportEntry(entryObj) {
  var entryText = `|${entryObj.word}|${entryObj.sentence
    ?.replace(/\n/g, ' ')
    ?.replace(/\r/g, ' ')}|${entryObj.source}|${
    entryObj.key
  }|${entryObj.date.toISOString()}|\n`;
  if (summaryPath) {
    fs.appendFileSync(summaryPath, entryText, { encoding: 'utf8' });
  } else {
    process.stdout.write(entryText);
  }
}
