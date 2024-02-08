from setuptools import setup, find_packages

setup(
    name='hec_meta_extract',
    # python_requires='3.9.13',
    version='0.1.0',
    packages=find_packages(include=['utils'], exclude=['dev', 'output', '.vscode']),
    install_requires=[
        'cython',
        'numpy',
        'pkgconfig',
        'PyYAML',
        'geopandas',
        'h5py',
        'pyinstaller'
    ]
)