from setuptools import setup, find_packages

setup(
    name="ccontext",
    version="0.1.1",
    author="Nicolas Arnouts",
    author_email="arnouts.software@gmail.com",
    description="collect-context: Makes the process of collecting and sending context to an LLM like ChatGPT-4o as easy as possible.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NicolasArnouts/ccontext",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ccontext": ["config.json"],
    },
    install_requires=[
        "colorama==0.4.6",
        "pyperclip==1.8.2",
        "tiktoken==0.7.0",
        "pathspec==0.12.1",
    ],
    entry_points={
        "console_scripts": [
            "ccontext=ccontext.cli:main",
            "ccontext-configure=ccontext.configurator:copy_default_config",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
