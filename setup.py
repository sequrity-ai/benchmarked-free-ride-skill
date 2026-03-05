from setuptools import setup, find_packages

setup(
    name="benchmarked-free-ride",
    version="1.0.0",
    description="Auto-configure best free AI models based on benchmarked quality scores",
    author="Sequrity",
    py_modules=["main"],
    install_requires=[
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "benchmarked-free-ride=main:main",
        ],
    },
    python_requires=">=3.9",
)
