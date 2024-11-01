from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Libreria para obtener datos para backtesting.py'
LONG_DESCRIPTION = 'En este paquete se encuentran funciones para obtener datos de distintos exchange para poder usarlos en backtesting.py'

# Configurando
setup(
        name="backtesting_data", 
        version=VERSION,
        author="Mariano Damian Ferro Villanueva",
        author_email="<ferro.mariano@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            'pandas',
            'numpy',
            'requests',
            'ccxt',
            'datetime',
            'time',
            'json',
            'os',
            'sys',
            'csv',
            'logging',
            'binance-futures-connector',
            'load-dotenv',
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