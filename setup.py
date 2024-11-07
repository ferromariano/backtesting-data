from setuptools import setup, find_packages

VERSION = '0.0.5'
DESCRIPTION = 'Libreria para obtener datos para usar en backtesting.py'
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()
# Configurando
setup(
        name="backtesting_data", 
        version=VERSION,
        author="Mariano Damian Ferro Villanueva",
        author_email="<ferro.mariano@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        url="https://github.com/ferromariano/backtesting-data",
        packages=find_packages(),
        install_requires=[
            'pandas',
            'numpy',
            'ccxt',
            'datetime',
            'logging',
        ], 
        keywords=['python', 'backtesting.py', 'backtesting', 'exchange'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)