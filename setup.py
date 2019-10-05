from setuptools import setup, find_packages

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(
	name='hsc',
	version='1.0.2',
	author='Nullifiers',
	author_email='nullifiersorg@gmail.com',
	description='Hackerrank Solution Crawler',
	url='https://github.com/Nullifiers/Hackerrank-Solution-Crawler',
	download_url='https://github.com/Nullifiers/Hackerrank-Solution-Crawler/releases',
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	entry_points={
		'console_scripts': [
			'hsc=hsc.crawler:main',
		],
	}, install_requires=['requests']
)
