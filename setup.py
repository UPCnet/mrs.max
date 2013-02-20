from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='mrs.max',
      version=version,
      description="MAX UI integration for Plone and related portlets and views.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone max maxui',
      author='UPCnet Plone Team',
      author_email='plone.team@upcnet.es',
      url='https://github.com/UPCnet/mrs.max',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mrs', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pas.plugins.preauth',
          'plone.app.z3cform',
          'plone.directives.form',
      ],
      extras_require={'test': ['plone.app.testing[robot]>=4.2.2']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )