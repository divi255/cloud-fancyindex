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

Security
--------

* To upload files, you need to be logged in with local *gcloud* installation.
  gcs-index-upload.sh actually calls *gcloud rsync*

* To let the software index your bucket, you need to create GCP servece account
  (permissions worked for me: Storage Legacy Bucket Reader & Storage Object
  Viewer) and then create a key for it. Put a path to keyfile to
  GOOGLE_APPLICATION_CREDENTIALS env variable or specify it in application
  command line params.

Installation
------------

* Copy Makefile.default to Makefile and feel free to edit it. Set bucket,
  prefix, and etc.

* Mods required: jinja2, argparse, google.cloud.storage. Install them or just
  run *make install-modules*

Usage
-----

* gcs-indexer.py - indexes bucket and creates JSON file (by default - prints
  everyting to stdout). To start, specify at least key file and bucket name.
  Note: option "-r" will index bucket recursively, but because bucket objects
  are not real files and folders, actually API always returns all objects below
  the given prefix. You just can choose include them to index or not.

* fancyindex-generator.py - generates index.html files (by default - in
  _build/html). One theme is already included (created by [TheInsomniac] -
  https://github.com/TheInsomniac/Nginx-Fancyindex-Theme). Actually it's
  compatible with almost all themes you can find or create.

* gcs-index-upload.sh - uploads _build/html to GCS

* tpl.html - template file for the primary table.

* docker-compose.yml - just a test stuff, ignore it

With make:

* make clean - clean _build/html (don't set out to empty as it will erase
  your entire root)

* make index - generate JSON index (to stdout)

* make html - generate JSON index and then make html files from it

* make pub - generate, make, upload to GCS

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

TODO
----

* If someone need it, I can quickly add AWS indexer. Don't need it bacause we
  work with GCS only.
