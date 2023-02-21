from setuptools import setup, find_packages

setup(
    name='hec_meta_extract',
    version='0.1.0',
    packages=find_packages(include=['utils'], exclude=['dev', 'output', '.vscode']),
    install_requires=[
        'PyYAML',
        'geopandas',
        'h5py'
    ]
)