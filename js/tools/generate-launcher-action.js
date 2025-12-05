#!/usr/bin/env node
/* global process */

var fs = require('fs');
var yaml = require('js-yaml');

if (process.argv.length < 3) {
  console.error(
    'Usage: node js/tools/generate-launcher-action.js data/target-sites.json <includeWorks=true> <name=Daily launcher> .github/workflows/daily_launcher.yml'
  );
  process.exit(1);
}

const sitesPath = process.argv[2];
var sitesText = fs.readFileSync(sitesPath, { encoding: 'utf8' });
var sites = JSON.parse(sitesText);
var targetWorksStatus = true;
var name = 'Daily launcher';

if (process.argv.length > 3) {
  targetWorksStatus = JSON.parse(process.argv[3]);
}
if (process.argv.length > 4) {
  name = process.argv[4];
}

const baseYAML = `name: ${name}
on:
  workflow_dispatch:
  schedule:
    - cron: '0 4 * * *'
`;
var jobs = {};

for (let siteName in sites) {
  let site = sites[siteName];
  if (site.skip) {
    continue;
  }

  if (targetWorksStatus) {
    if (!site.works) {
      continue;
    }
  } else {
    // Skip if works is falsy, not just false.
    if (site.works) {
      continue;
    }
  }

  var id = siteName.replace(/\./g, '_');
  if (/^\d/.test(id)) {
    id = '_' + id;
  }
  jobs[id] = {
    uses: 'wordnik/nyt-first-said/.github/workflows/brush.yml@master',
    secrets: 'inherit',
    with: {
      site: siteName,
    },
  };
}

const dailyLauncherYaml = baseYAML + yaml.dump({ jobs });
console.log(dailyLauncherYaml);
