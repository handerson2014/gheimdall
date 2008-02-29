#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   GHeimdall - A small web application for Google Apps SSO service.
#   Copyright (C) 2007 SIOS Technology, Inc.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
#   USA.
#
#   $Id$

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("gheimdall", "release.py"))

packages=find_packages()
package_data = find_package_data(where='gheimdall',
                                 package='gheimdall')
if os.path.isdir('locales'):
    packages.append('locales')
    package_data.update(find_package_data(
        where='locales',
        exclude=('*.po','*.back'), only_in_packages=False)) 

print packages

setup(
    name="gheimdall",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    #description=description,
    author='Takashi Matsuo',
    author_email='tmatsuo@sios.com',
    #url=url,
    #download_url=download_url,
    #license=license,
    
    install_requires = [
        "TurboGears >= 1.0.2.2",
    ],
    scripts = ["start-gheimdall.py"],
    zip_safe=False,
    packages=packages,
    package_data = package_data,
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        
        # if this has widgets, uncomment the next line
        # 'turbogears.widgets',
        
        # if this has a tg-admin command, uncomment the next line
        # 'turbogears.command',
        
        # if this has identity providers, uncomment the next line
        # 'turbogears.identity.provider',
    
        # If this is a template plugin, uncomment the next line
        # 'python.templating.engines',
        
        # If this is a full application, uncomment the next line
        # 'turbogears.app',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Applications',
        
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'nose.collector',
    )
    
