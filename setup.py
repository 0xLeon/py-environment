from setuptools import find_packages
from setuptools import setup

setup(
	name='winenv',
	version='0.0.0',

	url='https://github.com/0xLeon/py-environment',
	author='Stefan Hahn',
	author_email='development@0xleon.com',

	license='MIT',

	packages=find_packages(),

	install_requires=[
		'future'
	],
)
