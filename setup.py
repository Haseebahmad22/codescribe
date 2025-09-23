# Setup script for CodeScribe
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codescribe",
    version="1.0.0",
    author="CodeScribe Team",
    author_email="info@codescribe.ai",
    description="AI-Powered Code Documentation Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codescribe/codescribe",
    packages=find_packages(where="backend/src"),
    package_dir={"": "backend/src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "openai>=1.3.0",
        "transformers>=4.36.0",
        "torch>=2.1.0",
        "astunparse>=1.6.3",
        "jinja2>=3.1.2",
        "markdown>=3.5.1",
        "pygments>=2.17.2",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.2.1",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "treesitter": [
            "tree-sitter>=0.20.4",
            "tree-sitter-python>=0.20.4",
            "tree-sitter-javascript>=0.20.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "codescribe=cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md"],
    },
)