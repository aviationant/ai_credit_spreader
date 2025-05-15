from setuptools import setup, find_packages

setup(
    name="Credit Spreader",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pymongo>=4.7",
        "mongoengine>=0.27",
        "alpaca-py>=0.40.0",
        "tqdm>=4.67.0",
        "requests>=2.32.0",
        "openai>=1.78.0",
        "python-dotenv>=1.1.0",
    ],
    python_requires=">=3.8",
)