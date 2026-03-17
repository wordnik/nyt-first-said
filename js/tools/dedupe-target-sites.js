#!/usr/bin/env node

var fs = require('fs');

/* global process */

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/dedupe-sources.js <path to target sites JSON>'
  );
  process.exit(1);
}

const siteDictPath = process.argv[2];

var dupesFound = 0;
var noURLEntriesFound = 0;
var urlsInList = [];
var dedupedDict = {};
var siteDict = JSON.parse(fs.readFileSync(siteDictPath, { encoding: 'utf8' }));

Object.values(siteDict).forEach(addSiteEntry);
fs.writeFileSync(siteDictPath, JSON.stringify(dedupedDict, null, 2), {
  encoding: 'utf8',
});

console.log(dupesFound, 'Duplicates found.');
console.log(noURLEntriesFound, 'Missing-URL entries found.');

function addSiteEntry(entry) {
  const url = entry.feeder_pages?.[0];
  if (!url) {
    noURLEntriesFound += 1;
    return;
  }
  if (urlsInList.includes(url.toLowerCase())) {
    dupesFound += 1;
    return;
  }
  urlsInList.push(url.toLowerCase());
  dedupedDict[entry.site] = entry;
}
