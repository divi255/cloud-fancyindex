__version__ = '0.0.1'

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='cloud-fancyindex',
    version=__version__,
    author='Sergei S.',
    author_email='s@makeitwork.cz',
    description=
    'Generates indexes for cloud buckets from NGINX Fancyindex themes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/divi255/cloud-fancyindex',
    packages=setuptools.find_packages(),
    license='MIT',
    install_requires=['jinja2'],
    scripts=['bin/cloud-fancyindex-generator'],
    classifiers=('Programming Language :: Python :: 3',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Text Processing :: Markup :: HTML',
                 'Topic :: Utilities'),
)
