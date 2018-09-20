import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
	name='hackerrank-crawler',
	version='1.1.0',
	author='Nullifiers',
	description='Hackerrank Solution Crawler',
	url='https://github.com/Nullifiers/Hackerrank-Solution-Crawler',
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=setuptools.find_packages(),
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	entry_points='''
		[console_scripts]
		hackerrank-crawler=hackerrank.crawler:main
	''',
)
