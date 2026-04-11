from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dokploy-skills",
    version="1.0.0",
    author="Xhuk",
    description="Advanced toolkit for managing Dokploy deployments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xhuk/dokploy-skills",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "click>=8.0.0",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dokploy=cli.dokploy:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/**/*", "docs/**/*"],
    },
)
