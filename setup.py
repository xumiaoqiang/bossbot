# coding=utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='bossbot',

    version="0.3",
    description=(
        'A boss chat bot'

    ),
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    author='xmq',
    author_email='jiongbo416jie@qq.com',
    maintainer='xmq',
    maintainer_email='jiongbo416jie@qq.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/wangyitao/cbot',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'paho-mqtt',
        'protobuf',
        'qrcode',
        'requests',
        'Pillow',
    ]
)