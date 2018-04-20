from setuptools import setup, find_packages

setup(
    name='pywebui.bridge',
    version='0.1.0',
    url='https://github.com/kahowell/pywebui',
    author='Kevin Howell',
    author_email='kevin@kahowell.net',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'six',
    ],
    zip_safe=False,
)
