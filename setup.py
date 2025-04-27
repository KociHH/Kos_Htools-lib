from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
from tools import __me_email__, __user_name__

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kos_Htools",
    version="0.1.1.post2",
    packages=find_packages(),
    install_requires=[
        "telethon>=1.39.0",
        "python-dotenv>=1.0.0",
        "redis>=5.0.0",
    ],
    author=f"{__user_name__}",
    author_email=f"{__me_email__}",
    description="Мини библиотека для работы с Telegram и Redis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{__user_name__}/helping_libs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 