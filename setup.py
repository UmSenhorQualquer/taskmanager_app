#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

import os, fnmatch


def find_files(package_name,directory, pattern):
    for root, dirs, files in os.walk(os.path.join(package_name, directory)):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root[len(package_name)+1:], basename)
                yield filename

setup(
	name='Tasks manager app',
	version=0.0,
	description="""""",
	author=['Ricardo Ribeiro'],
	author_email=['ricardojvr@gmail.com'],
	include_package_data=True,
	packages=find_packages(),
	package_data={'taskmanager_app':
		list(find_files('taskmanager_app','static/', '*.*'))+list(find_files('taskmanager_app','templates/', '*.*'))
	},
)
