"""Setup script for creating a pip package."""
from setuptools import find_packages, setup

setup(
    name='django-envcrypto',
    version='0.8.5',
    description='A safe way to store Django environmental Variables',
    long_description='Store Django environmental Variables for multiple deployments, easy and securely.',
    author='Rogerio Candeias',
    author_email='rogerio.candeias@gmail.com',
    url='https://github.com/candeias/django-envcrypto',
    license='BSD2',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    classifiers=[
        'Intended Audience :: Developers', 'Natural Language :: English',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=[
        'django>=2.1.4', 'mock', 'nose', 'coverage', 'urllib3[secure]'
    ],
    install_requires=['cryptography>=2.1.4'])
