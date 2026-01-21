from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="uqlm-guard",
    version="1.0.0",
    description="AI Code Uncertainty Detection using UQLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kelpejol",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "uqlm==0.1.0",
        "langchain==0.0.335",
        "openai==1.3.5",
        "python-dotenv==1.0.0",
        "click==8.1.7",
        "rich==13.7.0",
        "pydantic==2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "uqlm-guard=uqlm_guard.cli.main:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="llm ai uncertainty hallucination detection code-quality",
    project_urls={
        "Bug Reports": "https://github.com/kelpejol/uqlm-guard/issues",
        "Source": "https://github.com/kelpejol/uqlm-guard",
    },
)