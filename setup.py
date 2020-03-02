import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ConfigDmanager",
    version="0.0.1",
    author="Dhia Hmila",
    author_email="hmiladhia@hotmail.fr",
    description="A simple configuration files manager package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hmiladhia/ConfigDmanager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)