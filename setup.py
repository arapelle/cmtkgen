import setuptools
import glob

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

scripts = []
# scripts = glob.glob('cmtkgen_lib/c*.py')
scripts.append('cmtkgen')
print(scripts)

setuptools.setup(
    name='cmtkgen',  
    version='0.9',
    scripts=scripts,
    author="Aymeric Pellé",
    author_email="aympelle@gmail.com",
    description="A C++ CMake project generator (using CMake ToolKit)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arapelle/cmtkgen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
