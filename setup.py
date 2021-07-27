from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

class NPMInstall(install):
    def _npm_install(self):
        subprocess.run(['npm', 'install', '-g', 'diff2html-cli'])

    def run(self):
        self._npm_install()
        install.run(self)


with open("requirements.txt") as f:
    install_requirements = f.read().splitlines()

setup(
    name="lambda-diff",
    version="0.0.1",
    description="diff tool for AWS Lambda",
    author="tatsuya4559",
    packages=find_packages(),
    install_requires=install_requirements,
    cmdclass={
        'install': NPMInstall
    },
    entry_points={
        "console_scripts": [
            "ldiff=lambda_diff.main:diff",
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ]
)

