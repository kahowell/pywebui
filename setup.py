import os

from setuptools import setup, find_packages

def find_templates():
    templates_path = os.path.join('pywebui', 'builder', 'templates')
    paths = []
    for dirname, subdirs, files in os.walk(templates_path):
        for filename in files:
            dirname_relative = dirname.replace(os.path.join('pywebui', 'builder', ''), '')
            paths.append(os.path.join(dirname_relative, filename))
    return paths

setup(
    name='pywebui',
    version='0.1.0',
    url='https://github.com/kahowell/pywebui',
    author='Kevin Howell',
    author_email='kevin@kahowell.net',
    license='MIT',
    packages=find_packages(),
    package_data={'pywebui.builder': find_templates()},
    entry_points={
        'console_scripts': [
            'pywebui = pywebui.builder.cli:main',
        ],
    },
    install_requires=[
        'cookiecutter',
        'pywebui.bridge',
    ],
    zip_safe=False,
)
