#!/usr/bin/env node

var fs = require('fs');

/* global process */

if (process.argv.length < 3) {
  console.error('Usage: node tools/dedupe-sources.js <path to site list JSON>');
  process.exit(1);
}

const siteListPath = process.argv[2];

var dupesFound = 0;
var namesInList = [];
var dedupedList = [];
var siteList = JSON.parse(fs.readFileSync(siteListPath, { encoding: 'utf8' }));

siteList.forEach(addSiteEntry);
fs.writeFileSync(siteListPath, formatList(dedupedList), {
  encoding: 'utf8',
});

console.log(dupesFound, 'Duplicates found.');

function addSiteEntry({ name, url }) {
  if (namesInList.includes(name.toLowerCase())) {
    dupesFound += 1;
    return;
  }
  namesInList.push(name.toLowerCase());
  dedupedList.push({ name, url });
}

function formatList(list) {
  var formatted = JSON.stringify(list);
  formatted = formatted.replace(/},/g, '},\n');
  formatted = formatted.replace(/{/g, '  {');
  formatted = formatted.replace(/\[/, '[\n');
  formatted = formatted.replace(/\]/, '\n]');
  return formatted;
}
