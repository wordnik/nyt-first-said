#!/bin/bash

# Run this script with .<space>, e.g. `. tools/init-aws.sh` so that this gets
# executed in the current shell and makes the environment variables available there.
# Assumes you have a `[profile wordnik]` section in ~/.aws/config.
export AWS_PROFILE=wordnik
