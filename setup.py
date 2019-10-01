import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gt-dicom-connector",
    version="0.0.2",
    author="Martin Bührer",
    author_email="info@gyrotools.com",
    description="A DICOM Node Connector for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gyrotools/gt-dicom-connector-py",
    packages=setuptools.find_packages(),
    install_requires=[
        'pynetdicom',
    ],
    python_requires='>=3.6.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
