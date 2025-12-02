#!/usr/bin/env node
/* global process */

var fs = require('fs');

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/fix-urls-in-list.js <relative path to site list json> > out.json'
  );
  process.exit(1);
}

const inputPath = process.argv[2];
var entries = JSON.parse(fs.readFileSync(inputPath, { encoding: 'utf8' }));

var entriesWithURLs = entries.filter((e) => e.url);
entriesWithURLs.forEach(fixEntryURL);
console.log(JSON.stringify(entries, null, 2));

function fixEntryURL(entry) {
  if (!entry.url.startsWith('https://')) {
    entry.url = 'https://' + entry.url;
  }
}
