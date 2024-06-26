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
        'pyexiftool',
        'Pillow',  # Changed from 'pillow' to 'Pillow'
        'python-magic',  # Changed from 'magic' to 'python-magic'
        'mutagen',
        'PyYAML',
        'boto3',
        'google-cloud-storage',
        'inquirer',
        'azure-storage-blob'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)