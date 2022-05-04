from setuptools import setup, find_packages

setup(
    name='expydite',
    version='0.1',
    description="",
    author="John Corn",
    author_email="johncorn271828@gmail.com",
    packages=find_packages(include=["expydite", "expydite.*"]),
    install_requires=["nuitka", "astor"]
)
