"""Setup configuration for Piddy Phase 5."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="piddy-phase5",
    version="5.0.0",
    author="DevOps Team",
    description="Advanced DevOps & MLOps Integration Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/piddy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "prometheus-client>=0.15.0",
        "opentelemetry-api>=1.15.0",
        "opentelemetry-sdk>=1.15.0",
        "scikit-learn>=1.2.0",
        "tensorflow>=2.11.0",
    ],
    entry_points={
        "console_scripts": [
            "phase5=src.phase5_cli:main",
            "piddy=src.phase5_cli:main",
        ],
    },
)
