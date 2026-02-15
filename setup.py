"""Setup configuration for AI Email Assistant."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-email-assistant",
    version="0.1.0",
    author="Vinay K",
    author_email="itzvinay@gmail.com",
    description="Multi-agent AI system for professional email generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vinaytocode/ai-email-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "email-assistant=src.ui.streamlit_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src.memory": ["user_profiles.json"],
        "src.config": ["mcp.yaml"],
    },
)
