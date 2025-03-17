from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="deepmindset",
    version="0.1.0",
    author="DeepMindset Team",
    author_email="info@deepmindset.ai",
    description="A Streamlit-based chat quiz application that leverages RAG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/deepmindset",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "deepmindset=app:main",
        ],
    },
) 