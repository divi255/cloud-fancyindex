#!/usr/bin/env python3

_me = 'Fancy index generator'

import json
import os
import sys
import argparse

from jinja2 import Template

ap = argparse.ArgumentParser(description=_me)

ap.add_argument(
    '-t',
    '--template',
    help='Primary template (default: tpl.html)',
    metavar='FILE',
    default='tpl.html',
    dest='template')
ap.add_argument(
    '-F',
    '--fancyindex-theme',
    help='fancyindex theme directory (default: fancyindex)',
    metavar='DIR',
    default='fancyindex',
    dest='theme')
ap.add_argument(
    '-f',
    '--input-file',
    help='JSON index input file (default: stdin)',
    metavar='FILE',
    default='stdin',
    dest='input_file')
ap.add_argument(
    '-D',
    '--destination',
    help='Destination directory (default: _build/html)',
    metavar='DIR',
    default='_build/html',
    dest='destination')

a = ap.parse_args()

input_file_name = a.input_file
if input_file_name == 'stdin':
    input_file = sys.stdin
else:
    input_file = open(input_file_name)
template_file = a.template
fancyindex_theme = a.theme
html_folder = a.destination

structure = json.load(input_file)

header_html = open(fancyindex_theme + '/header.html').read()
footer_html = open(fancyindex_theme + '/footer.html').read()

template = Template(open(template_file).read())

for f, s in structure.items():
    output_folder = html_folder + (f if f != '/' else '')
    os.system('mkdir -p ' + output_folder)
    files = sorted(
        [item for item in s if not item['is_dir']], key=lambda k: k['name'])
    folders = sorted(
        [item for item in s if item['is_dir']], key=lambda k: k['name'])
    print(' -- {}: '.format(f), end='')
    with open(output_folder + '/index.html', 'w') as out:
        out.write(header_html)
        out.write(template.render(uri=f, files=files, folders=folders))
        out.write(footer_html)
    print('OK')

print(' -- fancyindex theme: ', end='')
os.system('rm -rf {}/fancyindex'.format(html_folder))
os.mkdir(html_folder + '/fancyindex')
os.system('cp -prf {}/* {}/fancyindex/'.format(fancyindex_theme, html_folder))
print('OK')
print()
print('Completed')
