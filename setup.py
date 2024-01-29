from setuptools import setup, find_packages

setup(
    name="packutils",
    version="0.0.1",
    install_requires=[],
    packages=find_packages(
        where="packutils", 
        include=["packutils.*"]
    ),
)
