#!/usr/bin/env node

var fs = require('fs');

/* global process */

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/get-issues-stats.js <report JSON file> > issues-stats.json'
  );
  process.exit(1);
}

const reportPath = process.argv[2];
var issuesCounts = {};

var sentenceReports = JSON.parse(
  fs.readFileSync(reportPath, { encoding: 'utf8' })
);
sentenceReports.forEach(countIssuesInReport);
console.log(JSON.stringify(issuesCounts, null, 2));

function countIssuesInReport(report) {
  if (!report.issue) {
    return;
  }

  var count = issuesCounts[report.issue];
  if (!count) {
    count = 0;
  }
  count += 1;
  issuesCounts[report.issue] = count;
}
