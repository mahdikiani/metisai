import os
import re

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(
            1
        )


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="metisai",
    version=get_version("metisai"),
    python_requires=">=3.7",
    url="https://github.com/mahdikiani/metisai",
    license="Apache-2.0",
    description="A Python client for Metis to streamline API interactions, enabling easy management and customization of AI-driven chatbots and image models.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Mahdi Kiani",
    author_email="mahdikiany@gmail.com",
    packages=find_packages(),
    zip_safe=False,
)
