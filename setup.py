try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = [
    'cassandra-driver==2.7.2',
]

with open('README.rst') as f:
    readme = f.read()

# Get version number from the package without importing it.
# This puts __version__ (and anything else defined in
# _version.py) in our namespace.
version_filepath = '_version.py'
with open(version_filepath) as version_file:
    exec(compile(version_file.read(), version_filepath, 'exec'))

setup(
    name='cassandradump',
    maintainer='Gianluca Borello',
    maintainer_email='g.borello@gmail.com',
    url='https://github.com/gianlucaborello/cassandradump',
    version=__version__,    # noqa
    description=('A data exporting tool for Cassandra inspired from mysqldump.'),
    long_description=readme,
    py_modules=['cassandradump'],
    install_requires=requires,
    license='GPL',
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    entry_points={
        'console_scripts': [
            'cassandradump=cassandradump:main',
        ],
    },
)
