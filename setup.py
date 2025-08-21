from setuptools import setup, find_packages

setup(
    name="diblob",
    version="2.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description="Diblob is a lightweight Python package for test case coverage of directed graphs (digraphs), with a focus on SESE graphs (Single Entry, Single Exit — graphs with one source and one sink). It is primarily developed for testing purposes and provides a simple, dependency-free solution built entirely on standard Python data structures.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jakub Zelek",
    author_email="jakub.zelek@doctoral.uj.edu.pl",
    url="https://github.com/JakubZelek/Diblob",
    license="MIT",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
