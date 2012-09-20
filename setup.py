#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'pythonrv',
	version = '0.1',
	description = 'A runtime verification framework',
	packages = ['pythonrv', 'pythonrv.test'],
	author = 'Adam Renberg',
	author_email = 'tgwizard@gmail.com',
	url = 'https://github.com/tgwizard/pythonrv',
	keywords = ['runtime verification', 'rv', 'verification', 'testing',
		'aspect-oriented programming'],
	classifiers = [
		'Programming Language :: Python',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Testing',
		'Topic :: Software Development :: Quality Assurance',
		'Topic :: System :: Monitoring',
		'Topic :: System :: Logging',
		'Topic :: Software Development :: Libraries :: Python Modules'
		]
	)
