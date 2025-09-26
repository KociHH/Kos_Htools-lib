from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kos_Htools",
    version='0.1.6.3.post2',
    packages=find_packages(),
    install_requires=[
        "telethon>=1.39.0",
        "python-dotenv>=1.0.0",
        "redis>=5.0.0",
        "sqlalchemy>=2.0.0",
        "pytz>=2025.1",
    ],
    author=f"KociHH",
    author_email=f"defensiv2010@gmail.com",
    description="Библиотека для работы с Telegram, Redis, SQLAlchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/KociHH/helping_lib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 