from setuptools import setup, find_packages

setup(
    name='diblob',
    version='1.0.5',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    description='A simple example package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jakub Zelek',
    author_email='jakub.zelek@doctoral.uj.edu.pl',
    url='https://github.com/Zeleczek-kodowniczek/Diblob/tree/main',
    license='MIT',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
