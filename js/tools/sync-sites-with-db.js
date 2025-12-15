#!/usr/bin/env node

var fs = require('fs');
var { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
var { GetCommand, DynamoDBDocumentClient } = require('@aws-sdk/lib-dynamodb');
var { queue } = require('d3-queue');

/* global process */

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/sync-sites-with-db.js <relative path to sites JSON>'
  );
  process.exit(1);
}

const targetSitesPath = process.argv[2];

var targetSitesObject = JSON.parse(
  fs.readFileSync(targetSitesPath, { encoding: 'utf8' })
);
var unprovenSites = Object.values(targetSitesObject).filter(
  (site) => !site.works
);
var unprovenSiteNames = unprovenSites.map((site) => site.site);

var dbClient = new DynamoDBClient({});
var docClient = DynamoDBDocumentClient.from(dbClient);

(async function main() {
  var siteResults = await getSiteResults({ siteNames: unprovenSiteNames });
  var resultsWithUpdates = siteResults.filter(
    (res) => !isNaN(res?.articles_processed)
  );
  debugger;
  for (let result of resultsWithUpdates) {
    if (result?.articles_processed > 0) {
      let site = targetSitesObject[result?.site];
      if (site) {
        site.works = true;
        console.error('Setting works to true for', site.site);
      }
    }
  }

  fs.writeFileSync(
    targetSitesPath,
    JSON.stringify(targetSitesObject, null, 2),
    {
      encoding: 'utf8',
    }
  );
})();

// function addSiteEntry({ name, url }) {
//   if (name in targetSitesObject) {
//     return;
//   }
//   targetSitesObject[name] = {
//     site: name,
//     domains: [url.replace('https://', '')],
//     feeder_pattern: `^${url}`,
//     feeder_pages: [url],
//     use_archive: false,
//     parser_name: 'article_based',
//     parser_params: {},
//   };
// }

async function getSiteResults({ siteNames }) {
  var q = queue(10);
  siteNames.forEach((siteName) => q.defer(getSiteResult, siteName));
  return await new Promise((resolve, reject) => {
    q.awaitAll(done);

    function done(error, results) {
      if (error) {
        console.error('Error while getting result:', error);
        reject(error);
        return;
      }
      resolve(results);
    }
  });
}

async function getSiteResult(siteName, done) {
  var getCommand = new GetCommand({
    TableName: 'nyt-said-site-results',
    Key: { site: siteName },
  });

  var getRes;

  try {
    getRes = await docClient.send(getCommand);
    done(null, getRes?.Item);
  } catch (error) {
    if (error.name === 'ResourceNotFoundException') {
      // The key may not be there, which is OK.
      done(null, null);
      return;
    }
    console.error(
      `Error while trying to get ${siteName} in database: ${error}\n`
    );
    done(error);
  }
}
