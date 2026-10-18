#!/bin/sh
# Create the four parking-space keys with the value "empty" if they do not
# exist. Run once when the system is installed; safe to run again, since
# SETNX leaves an existing key untouched.
for k in stephens synge westland kildare; do
  redis-cli SETNX "$k" empty
done
