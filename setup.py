from setuptools import setup, find_packages

VERSION = '2.3.2'
DESCRIPTION = 'Python wrapper for the mangadex API'
with open("README.md", "r", encoding="utf8") as f:
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
    install_requires = ["requests", "future", "python-dateutil", "pytest"],
    source = "https://github.com/EMACC99/mangadex",
    download_url = "https://github.com/EMACC99/mangadex/releases",
    documentation = "https://github.com/EMACC99/mangadex/wiki",
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
        ],
    zip_safe = False,
    python_requires = ">=3.6"
)