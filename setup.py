import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Tandyberg", # Replace with your own username
    version="0.1.0",
    author="Jesse B. Crawford",
    author_email="jesse@jbcrawford.us",
    description="Controller for Tandberg Precision HD cameras",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jcrawfordor/tandyberg",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires = [
        'pyserial',
        'pyqt5'
    ]
)