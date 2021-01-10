import os
import vpapp
from setuptools import setup,find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'vpapp',
    version=vpapp.__version__,
    packages=find_packages(),
    include_package_data=True,
    description='A Django app to parse and server replacement-plans for the realschule herrieden.',
    long_description=README,
    url='https://github.com/RSHerrieden/vpapp',
    author='Moritz \'e1mo\' Fromm',
    author_email='git@e1mo.de',
    license = 'AGPL-3.0',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.1  # Replace "X.Y" as appropriate',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: AGPLN License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    python_requires=">=3.5",
    install_requires=[
        'django',
        'beautifulsoup4',
        'lxml',
        'requests',
        'python-dateutil'
    ]
)
