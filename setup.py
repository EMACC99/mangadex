from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Python wrapper for the mangadex API'
LONG_DESCRIPTION = 'A python wrapper fot the new released mangadex API'

#setting up
setup(
    name = 'mangadex',
    version = VERSION,
    author = "Eduardo Ceja",
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    packages = find_packages(),
    install_requires = [],

    keywords = ['python', 'mangadex'],
    # clasifiers = ["Development Status :: "]

)