#!/usr/bin/env python

from setuptools import setup, find_packages
 
setup (
    name='django-mysqlfulltextsearch',
    version='0.1',
    description='A full-text search app for Django and MySQL',
    author='Elf M. Sternberg',
    author_email='elf.sternberg@gmail.com',
    url='http://github.com/elfsternberg/django-mysqlfulltextsearch/',
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
)
