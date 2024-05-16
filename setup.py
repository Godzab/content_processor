from setuptools import setup, find_packages

setup(
    name='content_processor',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'content_processor=content_processor.cli:run'
        ]
    },
    install_requires=[
        # Add any dependencies here
    ],
    # Add other package metadata (author, description, license, etc.)
)