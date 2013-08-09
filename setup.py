
import sys

try:
    # Setuptools: you know you want it!
    from setuptools import setup
except ImportError:
    # But I guess you don't have to have it...
    from distutils.core import setup


REQUIRES = ['pyramid',  'scrypt']
TESTS_REQUIRE = REQUIRES + ['webtest']

if sys.version_info < (2, 7):
    TESTS_REQUIRE.append('unittest2')


setup(name='scrypt-helper',
    version='0.1',
    description='Web API to help you calculate scrypt()',
    long_description='Web API to help you calculate scrypt()',
    license='MPLv2.0',
    classifiers=[
      "Programming Language :: Python",
      "Framework :: Pylons",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
      ],
    author='Mozilla Identity Team',
    author_email='identity-dev@mozilla.org',
    url='https://github.com/mozilla/scrypt-helper',
    keywords='web pyramid pylons auth scrypt',
    packages=['scrypt_helper'],
    zip_safe=False,
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRE,
    test_suite="scrypt_helper.tests",
)
