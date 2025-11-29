#!/bin/bash
#
for file in test/test_*.py
  do
    testname=${file//\//\.}
    testname=${testname/\.py/}
	  venv/bin/python -m unittest -v $testname
  done
