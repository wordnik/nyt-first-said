#!/usr/bin/env node

var fs = require('fs');

/* global process */

if (process.argv.length < 3) {
  console.error(
    'Usage: node tools/fill-missing-urls.js <relative path to sites JSON>'
  );
  process.exit(1);
}

const targetSitesPath = process.argv[2];
var sitesWithURLsAdded = 0;
var siteNamesFixed = 0;

var targetSitesObject = JSON.parse(
  fs.readFileSync(targetSitesPath, { encoding: 'utf8' })
);

var fixedTargetSitesObject = {};

for (let site in targetSitesObject) {
  let siteConfig = targetSitesObject[site];
  const fixedSiteName = fixSiteName(site);
  siteConfig.site = fixedSiteName;
  if (site !== fixedSiteName) {
    siteNamesFixed += 1;
  }

  let feederPages = siteConfig.feeder_pages;
  const urlBase = site.toLowerCase().replace(/[^a-z\d]/g, '');
  let urlGuesses = ['com', 'net', 'org'].map(
    (suffix) => `https://${urlBase}.${suffix}`
  );
  if (!feederPages || feederPages.length < 1) {
    siteConfig.feeder_pages = urlGuesses;
    sitesWithURLsAdded += 1;
  } else {
    let needsGuesses = false;
    for (let i = feederPages.length - 1; i > -1; --i) {
      let page = feederPages[i];
      if (!page || page === 'https://') {
        feederPages.splice(i, 1);
        needsGuesses = true;
      }
    }

    if (needsGuesses) {
      feederPages = feederPages.concat(urlGuesses);
      siteConfig.feeder_pages = feederPages;
      sitesWithURLsAdded += 1;
    }
  }
  let existingSiteConfig = fixedTargetSitesObject[fixedSiteName];
  if (
    !existingSiteConfig ||
    // Replace existing site config only if this one is more detailed.
    (siteConfig.feeder_pages?.length >
      existingSiteConfig.feeder_pages?.length &&
      siteConfig.domains?.length >
        existingSiteConfig.domainsfixedTargetSitesObject?.length)
  ) {
    fixedTargetSitesObject[fixedSiteName] = siteConfig;
  }
}

fs.writeFileSync(
  targetSitesPath,
  JSON.stringify(fixedTargetSitesObject, null, 2),
  {
    encoding: 'utf8',
  }
);

console.log(
  sitesWithURLsAdded,
  'sites with urls added.',
  siteNamesFixed,
  'site names fixed.'
);

function fixSiteName(s) {
  return s.toLowerCase().replace(/[^a-z\d]/g, '_');
}
