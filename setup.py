import os


from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


REQUIREMENTS = [
    'httplib2 >= 0.9.1',
    'googleapis-common-protos',
    'oauth2client >= 2.0.0.post1',
    'protobuf >= 3.0.0b2',
    'pyOpenSSL',
    'six',
]

setup(
    name='gcloud',
    version='0.10.1',
    description='API Client library for Google Cloud',
    author='Google Cloud Platform',
    author_email='jjg+gcloud-python@google.com',
    long_description=README,
    scripts=[],
    url='https://github.com/GoogleCloudPlatform/gcloud-python',
    packages=find_packages(),
    license='Apache 2.0',
    platforms='Posix; MacOS X; Windows',
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
    ]
)
