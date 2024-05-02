import os 
from setuptools import setup, find_packages
from dotenv import load_dotenv
load_dotenv() 

setup(
    name='custom_crawler',
    version='1.0',
    author=os.getenv('AUTHOR_NAME'),
    author_email=os.getenv('AUTHOR_EMAIL'),
    description='A custom crawlers module',
    packages=['.'],
)