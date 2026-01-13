#!/usr/bin/env node
/* global process */

var fs = require('fs');
var yaml = require('js-yaml');
var pick = require('lodash.pick');

if (process.argv.length < 4) {
  console.error(
    'Usage: node js/tools/generate-launcher-action.js data/target-sites.json <yaml base file path> [includeWorks=true] [name=Daily launcher]'
  );
  process.exit(1);
}

const sitesPath = process.argv[2];
var sitesText = fs.readFileSync(sitesPath, { encoding: 'utf8' });
var allSites = JSON.parse(sitesText);
var targetWorksStatus = true;
const maxSitesInLauncher = 500;

const yamlBasePath = process.argv[3];

if (process.argv.length > 4) {
  targetWorksStatus = JSON.parse(process.argv[4]);
}
var name = 'Daily launcher';
if (process.argv.length > 5) {
  name = process.argv[5];
}

var targetJobs = {};
var allSiteNames = Object.keys(allSites);
for (
  let launcherIndex = 0;
  launcherIndex < Math.ceil(allSiteNames.length / maxSitesInLauncher);
  ++launcherIndex
) {
  const siteStartIndex = launcherIndex * maxSitesInLauncher;
  let siteNames = allSiteNames.slice(
    siteStartIndex,
    siteStartIndex + maxSitesInLauncher
  );

  for (let siteName of siteNames) {
    let site = allSites[siteName];
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

    var id = siteName.replace(/\.| |'/g, '_');
    if (/^\d/.test(id)) {
      id = '_' + id;
    }

    targetJobs[id] = {
      uses: 'wordnik/nyt-first-said/.github/workflows/brush.yml@master',
      secrets: 'inherit',
      with: {
        site: siteName,
      },
    };
  }
}

var targetJobKeys = Object.keys(targetJobs);

for (
  let launcherIndex = 0;
  launcherIndex < Math.ceil(targetJobKeys.length / maxSitesInLauncher);
  ++launcherIndex
) {
  const jobIndexStart = launcherIndex * maxSitesInLauncher;
  var launcherJobs = pick(
    targetJobs,
    targetJobKeys.slice(jobIndexStart, jobIndexStart + maxSitesInLauncher)
  );
  const baseYAML = `name: ${name} ${launcherIndex}
on:
  workflow_dispatch:
  schedule:
    - cron: '0 ${(17 + launcherIndex) % 24} * * *'
`;
  const dailyLauncherYaml = baseYAML + yaml.dump({ jobs: launcherJobs });
  const yamlPath = `${yamlBasePath}_${launcherIndex
    .toString()
    .padStart(4, '0')}.yml`;
  fs.writeFileSync(yamlPath, dailyLauncherYaml, { encoding: 'utf8' });
}
