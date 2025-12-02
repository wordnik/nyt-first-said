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
const lineRange = process.argv[3].split('-').map((n) => (isNaN(n) ? 0 : +n));
const siteListPath = process.argv[4];

var targetSitesObject = JSON.parse(
  fs.readFileSync(targetSitesPath, { encoding: 'utf8' })
);
var siteList = JSON.parse(fs.readFileSync(siteListPath, { encoding: 'utf8' }));

siteList.slice(lineRange[0], lineRange[1]).forEach(addSiteEntry);

fs.writeFileSync(targetSitesPath, JSON.stringify(targetSitesObject, null, 2), {
  encoding: 'utf8',
});

function addSiteEntry({ name, url }) {
  if (name in targetSitesObject) {
    return;
  }
  targetSitesObject[name] = {
    site: name,
    feeder_pattern: `^${url}`,
    feeder_pages: [url],
    use_archive: false,
    parser_name: 'article_based',
    parser_params: {},
  };
}
