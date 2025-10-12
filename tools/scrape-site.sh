#!/bin/bash

SITE=$1
CURRENTDATE=$(/bin/date +%Y-%m-%d)

echo "$SITE $CURRENTDATE"
python simple_scrape.py ${SITE} > meta/$SITE-run-$CURRENTDATE.txt 2> meta/$SITE-error-$CURRENTDATE.txt
