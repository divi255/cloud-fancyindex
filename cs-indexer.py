#!/usr/bin/env python3

_me = 'Cloud Storage indexer'

import os
import fnmatch
import json
import argparse

object_field_map = {
    'gcs': {
        'name': 'name',
        'date': 'updated',
        'size': 'size'
    },
    's3': {
        'name': 'Key',
        'date': 'LastModified',
        'size': 'Size'
    }
}

checksum_files = {'md5sums': 'md5', 'sha1sums': 'sha1', 'sha256sums': 'sha256'}
checksums = ['md5', 'sha1', 'sha256']


class GenericStorageObject:
    pass


ap = argparse.ArgumentParser(description=_me)

ap.add_argument('bucket', help='bucket to index', metavar='BUCKET')

ap.add_argument(
    '-p',
    '--prefix',
    help='Bucket object prefix (default: /)',
    metavar='DIR',
    default='',
    dest='prefix')

ap.add_argument(
    '-k',
    '--key-file',
    help=
    'Get CS key from file ' + \
        '(default for gcs: from GOOGLE_APPLICATION_CREDENTIALS ' + \
        'environment variable)',
    metavar='FILE',
    default=None,
    dest='keyfile')

ap.add_argument(
    '-s',
    '--cloud-storage',
    help='Cloud storage type: gcs for Google, ' + \
            's3 for Amazon S3 and compatible (default: gcs)',
    metavar='TYPE',
    choices = ['gcs', 's3'],
    default='gcs',
    dest='cloud_storage')

ap.add_argument(
    '-r',
    '--recursive',
    help='Recursively include "subdirectories" and their objects',
    action='store_true',
    dest='recursive')

ap.add_argument(
    '-x',
    '--exclude',
    help='Files (masks) to exclude (default: index.html)',
    metavar='FILE',
    default='index.html',
    dest='exclude')

ap.add_argument(
    '-c',
    '--checksums',
    help='Get checksums from md5sums, sha1sums and sha256sums',
    action='store_true',
    dest='checksums')

ap.add_argument(
    '-E',
    '--exclude-fancyindex',
    help='Exclude /fancyindex directory',
    action='store_true',
    dest='exclude_fancyindex')

ap.add_argument(
    '-P',
    '--pretty-print',
    help='Print pretty JSON (default: no formatting)',
    action='store_true',
    dest='pretty_print')

ap.add_argument(
    '-T',
    '--time-format',
    help='Time format (default: %%Y-%%b-%%d %%H:%%M)',
    metavar='DIR',
    default='%Y-%b-%d %H:%M',
    dest='time_format')

a = ap.parse_args()

# to cli params
exclude = a.exclude.split('|')
exclude_fancyindex = a.exclude_fancyindex
prefix = a.prefix
recursive = a.recursive
pretty_print = a.pretty_print
time_format = a.time_format
bucket = a.bucket
cloud_storage = a.cloud_storage
get_checksums = a.checksums
if get_checksums:
    import re
    css_reg = re.compile('[\ \t]+')
# end to params

if prefix.endswith('/'):
    prefix = prefix[:-1]

if prefix.startswith('/'):
    prefix = prefix[1:]

structure = {}
folder_info = {}


def get_blob(o):
    if cloud_storage == 'gcs':
        return o.download_as_string().decode()
    elif cloud_storage == 's3':
        return client.get_object(
            Key=o['Key'], Bucket=bucket)['Body'].read().decode()
    else:
        return None


def apply_checksum_file(o, filename, foldername, ctype):
    key = ('/' + prefix if prefix else '/') + foldername
    sfile = get_blob(o)
    if not sfile: return
    sums = {}
    for l in (sfile.split('\n')):
        if l:
            try:
                s, f = re.split(css_reg, l.strip())
                sums[f] = s
                # update files if we already have any
                if key in structure:
                    l = structure.get(key)
                    for x in l:
                        if x['name'] == f:
                            x['checksum_' + ctype] = s
            except:
                raise Exception('Parse error {}'.format(filename))
    folder_info.setdefault(key, {})[ctype] = sums


def append_file(name, size, d=None, folder='', update_info_only=False):
    key = (('/' + prefix + ('/' if folder else '')) if prefix else '/') + folder
    if not update_info_only:
        file_info = {
            'is_dir': False,
            'name': name,
            'size': size,
            'date': (d.strftime(time_format) if d else None)
        }
        if get_checksums:
            for c in checksums:
                file_info['checksum_' + c] = None
            i = folder_info.get(key)
            if i:
                for c in checksums:
                    sums = i.get(c)
                    if sums:
                        file_info['checksum_' + c] = sums.get(name)

        structure.setdefault(key, []).append(file_info)
    if d and key != '/': update_folder_info(key, d, size)


def append_folder(folder):
    if folder.find('/') != -1:
        append_folder('/'.join(folder.split('/')[:-1]))
    parent = '/'.join(folder.split('/')[:-1])
    key = ('/' + prefix if prefix or not parent else '') + ('/' + parent
                                                            if parent else '')
    name = folder.split('/')[-1]
    try:
        min(filter(lambda el: el['name'] == name, structure.get(key, [])))
        return
    except:
        pass
    structure.setdefault(key, []).append({
        'is_dir': True,
        'name': name,
        'date': None,
        'size': None
    })


def update_folder_info(folder, d, size):
    if folder.find('/') != -1 and folder != '/':
        update_folder_info('/'.join(folder.split('/')[:-1]), d, size)
    if folder not in folder_info:
        folder_info[folder] = {'d': d, 's': size}
    else:
        if 's' not in folder_info[folder]:
            folder_info[folder]['s'] = size
        else:
            folder_info[folder]['s'] += size
        if 'd' not in folder_info[folder]:
            folder_info[folder]['d'] = d
    n = folder.split('/')
    key = '/'.join(n[:-1])
    if not key: key = '/'
    foldername = n[-1]
    f = structure.get(key)
    if not f: return
    for l in f:
        if l['is_dir'] and l['name'] == foldername:
            if not l['date'] or folder_info.get(folder)['d'] < d:
                l['date'] = d.strftime(time_format)
            l['size'] = folder_info.get(folder)['s']
            break


if cloud_storage == 'gcs':
    if a.keyfile:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = a.keyfile
    from google.cloud import storage

    client = storage.Client()

    bucket = client.get_bucket(bucket)
    objects = bucket.list_blobs(prefix=prefix)
elif cloud_storage == 's3':
    import boto3
    key = json.load(open(a.keyfile))
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=key.get('region_name'),
        endpoint_url=key.get('endpoint_url'),
        aws_access_key_id=key['aws_access_key_id'],
        aws_secret_access_key=key['aws_secret_access_key'])
    try:
        objects = client.list_objects(Bucket=bucket, Prefix=prefix)['Contents']
    except KeyError:
        # empty bucket
        objects = []
else:
    print('cloud storage type unknown: ' + cloud_storage)
    exit(2)


def format_object(o, cs):
    out = GenericStorageObject()
    for k, v in object_field_map[cs].items():
        if isinstance(o, dict):
            value = o[v]
        else:
            value = getattr(o, v)
        setattr(out, k, value)
    return out


for obj in objects:
    o = format_object(obj, cloud_storage)
    if o.name.endswith('/'): continue
    n = o.name[len(prefix) + 1 if prefix else 0:].split('/')
    if exclude_fancyindex and not prefix and n[0] == 'fancyindex':
        continue
    skip = False
    if get_checksums and n[-1].lower() in checksum_files:
        foldername = '/'.join(n[:-1])
        apply_checksum_file(obj, o.name, foldername,
                            checksum_files[n[-1].lower()])
    for x in exclude:
        if fnmatch.fnmatch(n[-1], x):
            skip = True
            break
    if skip: continue
    if len(n) == 1:
        # we have a file in root
        append_file(n[-1], o.size, o.date)
    else:
        # we have a file in a "folder"
        foldername = '/'.join(n[:-1])
        if not recursive and prefix != foldername:
            append_folder(n[0])
            append_file(
                n[-1], o.size, o.date, '/'.join(n[:-1]), update_info_only=True)
            continue
        append_folder(foldername)
        append_file(n[-1], o.size, o.date, '/'.join(n[:-1]))

if pretty_print:
    print(json.dumps(structure, indent=4, sort_keys=True))
else:
    print(json.dumps(structure))
