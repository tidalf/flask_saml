import setuptools
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

with open('README.md') as f:
    long_description = f.read()

with open(os.path.join(here, 'flask_saml.py')) as v_file:
    VERSION = re.compile(
        r".*__version__ = '(.*?)'",
        re.S).match(v_file.read()).group(1)

install_requires = [
    'json_log_formatter>=0.1.0',
    'Flask>=0.8.0',
    'blinker>=1.1',
    'pysaml2>=4.0.0,<5',
]

setuptools.setup(
    name='Flask-SAML',
    version=VERSION,
    url='https://bitbucket.org/asecurityteam/flask_saml',
    author='Florian Ruechel',
    tests_require=['pytest >= 2.5.2', 'mock', 'sphinx', 'pytest-mock'],
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    author_email='fruechel@atlassian.com',
    description='Flask SAML integration',
    long_description=long_description,
    py_modules=['flask_saml'],
    include_package_data=True,
    zip_safe=False,
)
