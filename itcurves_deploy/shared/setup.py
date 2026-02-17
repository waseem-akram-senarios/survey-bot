from setuptools import setup, find_packages

setup(
    name="survey-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0",
        "psycopg2-binary>=2.9",
        "httpx>=0.27",
        "pydantic>=2.0",
    ],
)
