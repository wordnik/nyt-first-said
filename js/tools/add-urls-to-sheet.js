#!/usr/bin/env node
/* global process */

var fs = require('fs');
var { firefox } = require('playwright');
var { queue } = require('d3-queue');

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/add-urls-to-sheet.js <relative path to site list json> > out.json'
  );
  process.exit(1);
}

const concurrency = 4;
const inputPath = process.argv[2];
var entries = JSON.parse(fs.readFileSync(inputPath, { encoding: 'utf8' }));

console.log('[');

(async function go() {
  var browser = await firefox.launch();
  var context = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0',
  });

  var entriesWithURLs = entries.filter((e) => e.url);
  var entriesWithoutURLs = entries.filter((e) => !e.url);
  console.error(
    entriesWithURLs.length,
    'entriesWithURLs',
    entriesWithoutURLs.length,
    'entriesWithoutURLs'
  );

  entriesWithURLs.forEach((entry) =>
    process.stdout.write(JSON.stringify(entry) + ',\n')
  );

  var q = queue(concurrency);
  for (let i in entriesWithoutURLs) {
    let entry = entriesWithoutURLs[i];
    q.defer(addEntry, entry, i);
  }

  q.await(conclude);

  async function conclude() {
    await browser.close();
    console.log(']');
  }
  // console.log(JSON.stringify(entries, null, 2));

  async function addEntry(entry, i, done) {
    if (!entry.url) {
      entry.url = await getURLForName(entry.name);
      // console.error('Got url.', entry);
    }
    let commaOrNot = ',';
    if (i === entries.length - 1) {
      commaOrNot = '';
    }
    process.stdout.write(`  ${JSON.stringify(entry)}${commaOrNot}\n`);
    setTimeout(done, 0);
  }

  async function getURLForName(name) {
    var url = '';
    try {
      var page = await context.newPage();
      await page.goto(
        'https://html.duckduckgo.com/html/?q=' + encodeURIComponent(name)
      );
      var firstLink = page.locator('.web-result a.result__a').first();
      if (!firstLink) {
        console.error('Could not find result for', name);
      } else {
        const exitLink = await firstLink.getAttribute('href');
        url = decodeURIComponent(
          exitLink.split('//duckduckgo.com/l/?uddg=')[1].split('&')[0]
        );
      }
    } catch (error) {
      console.error('Error while searching for', name, error);
    }
    await page.close();
    return url;
  }
})();
