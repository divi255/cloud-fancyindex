#!/bin/sh

if [ ! $1 ]; then
    echo "Usage: gcs-index-upload.sh <bucket>"
    exit 99
fi

cd _build/html && gsutil -m rsync -a public-read -r -c . gs://$1

