#!/usr/bin/env node

var fs = require('fs');

/* global process */

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/corpus-csv-to-json.js <relative path to sites csv> > out.json'
  );
  process.exit(1);
}

const inputPath = process.argv[2];
const contents = fs.readFileSync(inputPath, { encoding: 'utf8' });
var lines = contents.trim().split('\r\n');
var entries = lines.map(parseLine);

console.log('[');

(async function go() {
  for (let i in entries) {
    let entry = entries[i];
    let commaOrNot = ',';
    if (i === entries.length - 1) {
      commaOrNot = '';
    }
    console.log(`  ${JSON.stringify(entry)}${commaOrNot}`);
  }

  console.log(']');
})();

function parseLine(line) {
  var values = line.split(',');
  const name = values[values.length - 1];
  var url = '';
  if (name.includes('.') && !name.includes(' ')) {
    url = name.toLowerCase();
    if (!url.startsWith('http')) {
      url = 'https://' + url;
    }
  }
  return { name, url };
}
