"""Setup configuration for Legal Debate System."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="legal-debate-system",
    version="0.1.0",
    author="Legal Debate System Contributors",
    description="AI-powered multi-agent legal debate system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tumul001/Legal-debate-system-with-multi-agent-architecture",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.4.2",
            "pytest-cov>=6.0.0",
            "black>=25.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "legal-debate=examples.run_debate_example:main",
        ],
    },
)
