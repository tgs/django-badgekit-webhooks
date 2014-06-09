import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="Thomas Grenfell Smith",
    author_email="thomathom@gmail.com",
    description="Webhook endpoint for Mozilla's BadgeKit API",
    name="django-badgekit-webhooks",
    long_description=read("README.rst"),
    version=__import__("badgekit_webhooks").__version__,
    url="http://django-badgekit-webhooks.rtfd.org/",
    license="MIT",
    include_package_data=True,
    packages=find_packages(),
    tests_require=[
        "Django>=1.4",
        'httpretty',
        "django-nose",
    ],
    install_requires=[
        "pyjwt",
        "django-appconf",
        "requests",
        "badgekit-api-client>=0.5.1",
        "django_inlinecss",
    ],
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
