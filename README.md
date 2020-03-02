Cloud FancyIndex
================

I like NGINX fancyindex module
(https://www.nginx.com/resources/wiki/modules/fancy_index/). With a good theme
it can make your auto-indexed file trash look like solid SP500 company's Website
with a few directives in web server config.

But future is coming and we are moving to cloud storages.

* Pros: you'll have built-in scalability, speed, and multi-zones for your files.
* Cons: these cloud buckets have no indexes (or they don't look so cool as old
  good NGINX fancyindex themes).

Of course you can make an application which gets bucket contents and displays
to to user in a nice way. But for what, if the files are static? Let's build
static indexes! And let's add fancyindex themes for them!

Uploading
---------

* To upload files to Google Cloud Storage, you need to be logged in with local
  *gcloud* app. cs-index-upload.sh actually calls *gsutil rsync*

* To upload to Amazon S3 or compatible, install and configure *s3cmd*

Installation
------------

```
pip3 install cloud-fancyindex
```

You also need to install [cloudindex](https://github.com/divi255/cloudindex)
package as well.

Usage
-----

* cloud-fancyindex-generator CLI tool - generates index.html files (by default
  in ./\_build/html )

* You must also download some fancy index theme, e.g.
  https://github.com/TheInsomniac/Nginx-Fancyindex-Theme. Actually it's
  compatible with almost all themes you can find or create.

Note: theme is placed in /fancyindex bucket directory. In case theme loads any
stuff (css/js etc.) from other directory, correct paths in its header / footer.

* You may download also my cs-index-upload.sh script - uploads output directory
  to cloud storage

* tpl.html - template file for the primary table. This is jinja2 template so
  you can use all functions it has. Example: https://github.com/divi255/cloud-fancyindex/blob/master/tpl.html

* sha256.tpl.html - template example with sha256 checksums. Example: https://github.com/divi255/cloud-fancyindex/blob/master/sha256.tpl.html

* template can include any additional object meta data.

* docker-compose.yml - just a test stuff, ignore it

Note: you need to rebuild index (at least partial one) every time you upload new
file to bucket. Sad, but true.

Example:

```
cloud-index [options] <bucket> | cloud-fancyindex-generator -t <template> -F <themepath> -D <output>
```

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

* S3 actually has real "folders" (at least emulates them), so index generation
  can be more optimal. But then we'll lose unification.
