from setuptools import setup, find_packages

import carton


setup(
    name='django-carton-no-database',
    version=carton.__version__,
    description=carton.__doc__,
    packages=find_packages(),
    url='https://github.com/julianogouveia/django-carton',
    author='jgouveia',
    long_description=open('README.md').read(),
    include_package_data=True,
)
