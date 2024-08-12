from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="browsinator",
    version="0.1.1",
    author="Slava Vishnyakov",
    author_email="bomboze@gmail.com",
    description="A Python library for programmatically controlling and interacting with a web browser using the Chrome DevTools Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slava-vishnyakov/browsinator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "websocket-client",
    ],
)
