#!/usr/bin/env node

var fs = require('fs');
var { queue } = require('d3-queue');
var { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
var { DynamoDBDocumentClient, GetCommand } = require('@aws-sdk/lib-dynamodb');

const concurrency = 25;

/* global process */

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/drop-problem-sites.js <path to target sites JSON>'
  );
  process.exit(1);
}

const siteDictPath = process.argv[2];
const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

var problemSitesFound = 0;
var correctedDict = {};
var siteDict = JSON.parse(fs.readFileSync(siteDictPath, { encoding: 'utf8' }));
const totalCount = Object.keys(siteDict).length;

// Check each table entry, then fix the sites entry's `works` property or delete it.
var q = queue(concurrency);
Object.values(siteDict).forEach((entry, i) => q.defer(addSiteEntry, entry, i));
q.awaitAll(allDone);

function allDone(error) {
  if (error) {
    console.error(error);
  } else {
    console.log(problemSitesFound, 'Problem sites found.');

    fs.writeFileSync(siteDictPath, JSON.stringify(correctedDict, null, 2), {
      encoding: 'utf8',
    });
  }
}

async function addSiteEntry(entry, number, done) {
  const getCommand = new GetCommand({
    TableName: 'nyt-said-site-results',
    Key: {
      site: entry.site,
    },
    // Set this to make sure that recent writes are reflected.
    // For more information, see https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html.
    // But: It's not *just* recent writes. Writes that are days old may not show up without this.
    ConsistentRead: true,
  });
  try {
    console.log('Processing entry', number, 'of', totalCount);

    const res = await docClient.send(getCommand);
    if (res?.$metadata?.httpStatusCode !== 200) {
      console.error('Could not get record for', entry.site, 'Response:', res);
      done();
      return;
    }
    let record = res.Item;
    if (!record) {
      // There's no record of a problem.
      correctedDict[entry.site] = entry;
      done();
      return;
    }
    // console.log('record:', record);
    if (
      record.site_is_invalid &&
      (record.articles_processed === undefined || record.articles_processed < 1)
    ) {
      problemSitesFound += 1;
    } else {
      correctedDict[entry.site] = entry;
    }
  } catch (error) {
    console.error('Error while getting record for', entry.site, error);
  }
  done();
}
