from setuptools import setup, find_packages

setup(
    name="llm-output-stability-gate",
    version="1.0.0",
    description="Pre-execution reliability gate using UQLM",
    author="Kelpejol",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "uqlm==0.1.0",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "langchain==0.0.335",
        "openai==1.3.5",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
