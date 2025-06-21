from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
from tools import USER_NAME, ME_EMAIL

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kos_Htools",
    version='0.1.5',
    packages=find_packages(),
    install_requires=[
        "telethon>=1.39.0",
        "python-dotenv>=1.0.0",
        "redis>=5.0.0",
    ],
    author=f"{USER_NAME}",
    author_email=f"{ME_EMAIL}",
    description="Мини библиотека для работы с Telegram, Redis, SQLAlchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{USER_NAME}/helping_libs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 