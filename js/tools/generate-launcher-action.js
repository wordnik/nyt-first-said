#!/usr/bin/env node
/* global process */

var fs = require('fs');
var yaml = require('js-yaml');

if (process.argv.length < 3) {
  console.error(
    'Usage: node js/tools/generate-launcher-action.js data/target-sites.json > .github/workflows/daily_launcher.yml'
  );
  process.exit(1);
}

const baseYAML = `name: Daily launcher
on:
  workflow_dispatch:
  schedule:
    - cron: '0 4 * * *'
`;

const sitesPath = process.argv[2];
var sitesText = fs.readFileSync(sitesPath, { encoding: 'utf8' });
var sites = JSON.parse(sitesText);

var jobs = {};

for (let siteName in sites) {
  if (!sites[siteName].works) {
    continue;
  }
  jobs[siteName] = {
    uses: 'wordnik/nyt-first-said/.github/workflows/brush.yml@master',
    secrets: 'inherit',
    with: {
      site: siteName,
    },
  };
}

const dailyLauncherYaml = baseYAML + yaml.dump({ jobs });
console.log(dailyLauncherYaml);
