import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    install_require = [x.strip() for x in f if x.strip()]

setuptools.setup(
    name="pykap",
    version="0.0.1",
    author="Cem Sinan Ozturk",
    author_email="cemsinanozturk@gmail.com",
    description="KAP (Public Disclosure Platform) Documentation Wrapper for Capital Markets Board of Turkey and Borsa Istanbul Public Disclosures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cemsinano/pykap",
    install_requires = install_require,
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
