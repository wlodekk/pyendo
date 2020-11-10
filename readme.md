# pyendo
> Pyendo is an Endomondo json files to pandas dataframe and feather file converter written in Python. 

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Features](#features)
* [Status](#status)
* [Inspiration](#inspiration)
* [Contact](#contact)

## General info
As we all know Endomondo is terminating its services by the end of 2020. I created a Python script that imports Endomodo json files with your training data (which you can downdload from the Endomondo website), converts it to a Pandas dataframe and saves it to a feather file.
You can use is it to analyze your training results in Python or R which both support the feather file format.

## Technologies
* Python - version 3.8.5
* Pandas - version 1.1.2
* Numpy - version 1.19.1
* Glom - version 20.8.0
* Pyarrow - version 1.0.1
* Timezonefinder- version 4.4.1

## Setup
Download the Python script, change the folder location of the json files in the script, set the default timezone for trainings without GPC coordinates, run it and convert your files to a feather format file. 


## Features
* Determines the timezone on the basis of GPS coordinates
* Saves the pandas dataframe in the feather format which is much faster to load then a CSV file


## Status
Project is: _in progress_

## Inspiration
Project inspired by Endomondo's planned termination of services.

## Contact
Created by Włodek Kuczyński [wlo.kucz(at)gmail.com](mailto:wlo.kucz@gmail.com)- feel free to contact me!
