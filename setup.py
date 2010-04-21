# -*- coding: utf-8 -*-
#
# fred-geojson: Setup
#
from setuptools import setup, find_packages
setup(name="simplegeo-geojson",
      version='0.1.0',
      description="A geojson library.",
      url="http://github.com/simplegeo/python-geojson",
      packages=find_packages(),
      include_package_data=True,
      author="Nerds",
      author_email="nerds@simplegeo.com",
      keywords="json geojson",
      test_suite="geojson.test.unit",
      install_requires=['simplejson'],
      setup_requires=['setuptools_trial', 'setuptools_pyflakes'])