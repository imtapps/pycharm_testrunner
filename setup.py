from setuptools import setup, find_packages

setup(
    name="pycharm-testrunner",
    description="pycharm testrunner",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'django',
    ]
)
