import setuptools
import os
import io

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_required = ['bs4','pandas','requests','regex','html5lib']

setuptools.setup(
    name="pykap",
    version="0.0.2.2",
    author="Cem Sinan Ozturk",
    author_email="cemsinanozturk@gmail.com",
    description="KAP (Public Disclosure Platform) Documentation Wrapper for Capital Markets Board of Turkey and Borsa Istanbul Public Disclosures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cemsinano/pykap",
    install_requires = install_required,
    project_urls={
        "Bug Tracker": "https://github.com/cemsinano/pykap/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #package_dir={"": "pykap"},
    package_data={'pykap': ['data/*.json']},
    packages=setuptools.find_packages(exclude=["tests"]),
    python_requires=">=3.6",
)
