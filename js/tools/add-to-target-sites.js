#!/usr/bin/env node

var fs = require('fs');

/* global process */

if (process.argv.length < 5) {
  console.error(
    'Usage: node tools/add-to-target-sites.js <relative path to sites JSON> <path to site list JSON> <line range to add>'
  );
  process.exit(1);
}

const targetSitesPath = process.argv[2];
const siteListPath = process.argv[3];
const lineRange = process.argv[4].split('-').map((n) => (isNaN(n) ? 0 : +n));
var sitesAdded = 0;

var targetSitesObject = JSON.parse(
  fs.readFileSync(targetSitesPath, { encoding: 'utf8' })
);
var siteList = JSON.parse(fs.readFileSync(siteListPath, { encoding: 'utf8' }));

siteList.slice(lineRange[0], lineRange[1]).forEach(addSiteEntry);
fs.writeFileSync(targetSitesPath, JSON.stringify(targetSitesObject, null, 2), {
  encoding: 'utf8',
});

console.log(sitesAdded, 'sites added.');

function addSiteEntry({ name, url }) {
  if (name in targetSitesObject) {
    return;
  }
  const domain = url.replace('https://', '');
  if (!url.includes(':')) {
    // There's no protocol, so assume https.
    url = 'https://' + url;
  }
  targetSitesObject[name] = {
    site: name,
    domains: [domain],
    feeder_pages: [url],
    use_archive: false,
    parser_name: 'article_based',
    parser_params: {},
  };
  sitesAdded += 1;
}
