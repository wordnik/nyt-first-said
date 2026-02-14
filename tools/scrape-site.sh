#!/bin/bash

SITE=$1
CURRENTDATE=$(/bin/date +%Y-%m-%d)
REVISIT=""
if [[ $2 ]]; then
  REVISIT="--revisit $2"
fi

# echo "${REVISIT}"
GITHUB_STEP_SUMMARY=meta/$SITE-summary-$CURRENTDATE.txt python simple_scrape.py ${SITE} ${REVISIT} > meta/$SITE-run-$CURRENTDATE.txt 2> meta/$SITE-error-$CURRENTDATE.txt

echo $GITHUB_STEP_SUMMARY
