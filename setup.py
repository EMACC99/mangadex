from setuptools import setup, find_packages

VERSION = '1.3.0'
DESCRIPTION = 'Python wrapper for the mangadex API'
with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()


#setting up
setup(
    name = 'mangadex',
    version = VERSION,
    author = "Eduardo Ceja",
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = "text/markdown",
    packages = find_packages(),
    install_requires = ["requests", "urllib"],
    source = "https://github.com/EMACC99/mangadex",
    download_url = "https://github.com/EMACC99/mangadex/releases",
    license = "MIT",
    keywords = ['python', 'mangadex'],
    clasifiers = [
        "License :: MIT License",
        "Operating System :: OS Independent",
        "Programming Languaje :: Python :: 3.6",
        "Programming Languaje :: Python :: 3.7",
        "Programming Languaje :: Python :: 3.8",
        "Programming Languaje :: Python :: 3.9",
        "Programming Languaje :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Library",
        "Topic :: Wrapper"
        ]
)