#!/bin/bash

# Get arg from command line
# $1: file path

file_path=$1

FILE=$(cat $file_path)
gpt ask "$FILE" \
    --example ./recipes/document/document.yml \
    --output tsv \
    --temperature 0 \
    --max-tokens 7500 > tmp.$file_path
