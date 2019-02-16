Cloud FancyIndex
================

I like NGINX fancyindex module
(https://www.nginx.com/resources/wiki/modules/fancy_index/). With a good theme
it can make your auto-indexed file trash look like solid SP500 companys' website
with a few directives in webserver config.

But future is coming and we are moving to cloud storages.

* Pros: you'll have built-in scalability, speed, and multi-zones for your files.
* Cons: these cloud buckets have no indexes (or they don't look so cool as old
  good NGINX fancyindex themes).

Of course you can make an application which gets bucket contents and displays
to to user in a nice way. But for what, if the files are static? Let's build
static indexes! And let's add fancyindex themes for them!

Uploading
---------

* To upload files to Google Clound Storage, you need to be logged in with local
  *gcloud* app. cs-index-upload.sh actually calls *gsutil rsync*

* To upload to Amazon S3 or compatible, install and configure *s3cmd*

Security
--------

* To let the software index your bucket, you need to create GCP servece account
  (permissions worked for me: Storage Legacy Bucket Reader & Storage Object
  Viewer) and then create a key for it. Put a path to keyfile to
  GOOGLE_APPLICATION_CREDENTIALS env variable or specify it in application
  command line params.

* For Amazon S3 JSON key is also required. Amazon doesn't supply JSON keys,
  create it manually:

    {
        "aws_access_key_id": "KEYID",
        "aws_secret_access_key": "SECRETKEY"
    }

* Additionally, for S3 you can specify in JSON fields *region_name* and
  *endpoint_url*, e.g. to connect to Digital Ocean Spaces:

    {
        "aws_access_key_id": "KEYID",
        "aws_secret_access_key": "SECRETKEY",
        "region_name": "nyc3",
        "endpoint_url": "https://nyc3.digitaloceanspaces.com"
    }

Installation
------------

* Copy Makefile.default to Makefile and feel free to edit it. Set bucket,
  prefix, cloud storage (*cs=gcs* for Google (default), *cs=s3* for Amazon S3)
  and etc.

* Mods required: jinja2, argparse, google.cloud.storage (for GCS), boto3
  (for S3). Install them or just run *sudo make install-modules*

Usage
-----

* cs-indexer.py - indexes bucket and creates JSON file (by default - prints
  everyting to stdout). To start, specify at least key file and bucket name.
  Note: option "-r" will index bucket recursively, but because bucket objects
  are not real files and folders, actually API always returns all objects below
  the given prefix. You just can choose include them to index or not.

* fancyindex-generator.py - generates index.html files (by default - in
  _build/html). One theme is already included (created by [TheInsomniac] -
  https://github.com/TheInsomniac/Nginx-Fancyindex-Theme). Actually it's
  compatible with almost all themes you can find or create.

* cs-index-upload.sh - uploads output directory to cloud storage

* tpl.html - template file for the primary table.

* docker-compose.yml - just a test stuff, ignore it

With make:

* make clean - clean _build/html (don't set out to empty as it will erase
  your entire root)

* make index - generate JSON index (to stdout)

* make html - generate JSON index and then make html files from it

* make pub - generate, make, upload to Cloud

Note: you need to rebuild index (at least partial one) every time you upload new
file to bucket. Sad, but true.

Usage in real life
------------------

E.g. you have a cool build script which makes your project tarball and uploads
it to */releases/${VERSION}/blahblahblah* path into cloud bucket. To re-index
the path, put the following string in your script after upload command:

    cd /path/to/cloud-fancyindex && make prefix=/releases/${VERSION} pub

Nuts and bolts
--------------

* Unfortunately it's impossible to implement sorting, as it called a server
  request with a query string only NGINX can understand. Maybe I'll do sorting
  with JS, some day.

* But a bonus - now you can easily display sizes of folders (or directories (or
  bucket paths (etc)))

* As buckets don't have real folders, sometimes it can't get a proper
  modification date or calculate folder size. Sorry for that.

* S3 actually has real "folders" (at least emulates them), so index generation
  can be more optimal. But then we'll lose unification.


TODO
----

* Working with Digital Ocean Spaces is untested. Will test it some time later.

