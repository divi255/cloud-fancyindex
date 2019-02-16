#!/bin/sh

if [ ! $3 ]; then
    echo "Usage: cs-index-upload.sh <gcs|s3> <dir> <bucket>"
    exit 99
fi

cd $2 || exit 1

case $1 in
gcs)
    gsutil -m rsync -a public-read -r -c . gs://$3
    ;;
s3)
    s3cmd sync -P --no-delete-removed . s3://$3
    ;;
*)
    echo "don't know how to upload to $1"
    ;;
esac

