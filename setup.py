from setuptools import setup, find_packages

setup(
    name="pss-lang",
    version="1.0.0",
    author="Your Name",
    description="A lightweight, indentation-based programming language that transpiles to C.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KUNBU8U7B/PSS",
    packages=find_packages(),
    py_modules=["pss"],
    entry_points={
        "console_scripts": [
            "pss=pss:main_cli",
        ],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
