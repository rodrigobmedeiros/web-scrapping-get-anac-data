# Web Scrapping Get ANAC Data

This project was developed in order to learn web scrapping techniques and apply it to get data from ANAC website.

# ANAC - Agência Nacional de Aviação Civil (National Civil Aviation Agency)

ANAC is a federal regulatory agency whose responsibility is to standardize and supervise civil aviation activity in Brazil, both with regard to its economic aspects and with regard to the technical safety of the sector.

# About the code and data

The ANAC website contains information on all flights in Brazil since 2000, grouped month by month. The idea of the code is to scan the site looking for links to each of the files, organizing them and at the end, concatenating them in a single dataset of information. Later, these data can be used in an exploratory analysis or in the development of a machine learning model

# How to run it

1) intall all packages contained at `requirements.txt`

- `pip install -r requirements.txt`

2) run the python file get-anac-dataset.py (inside /anac/dataset/) in the best directory for you.

  Write the following command in a command line:

- `python get-anac-dataset.py`
