"""Setup configuration for Meshtastic MQTT CLI."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read the contents of README.md for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="meshtastic-mqtt-cli",
    version="0.1.0",
    description="A command-line tool for sending messages to Meshtastic devices via MQTT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Meshtastic MQTT CLI Contributors",
    author_email="",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "meshtastic-send=meshtastic_mqtt_cli.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
