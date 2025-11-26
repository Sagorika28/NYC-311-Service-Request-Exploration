# NYC 311 Service Requests Analysis
DATA 512: Human-Centered Data Science  
Author: Sagorika Ghosh  
Date: 1 November 2025

## Overview
This project analyzes patterns in NYC 311 service requests to understand who reports, how they report, and how quickly issues are closed.  It was inspired by my personal experience living in New York City during my 2025 summer internship.

## Dataset
Source: NYC Open Data Portal (https://data.cityofnewyork.us/)
Dataset: 311 Service Requests from 2010 to Present (Social Services)
Dataset Link: https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9  
Dataset ID: erm2-nwe9
Terms of Use: https://opendata.cityofnewyork.us/terms-of-use/

Key fields: created_date, closed_date, complaint_type, descriptor, agency, borough, latitude, longitude, open_data_channel_type, unique_key.

## Accessing the data
The full dataset is very large. I will use the Socrata API with SoQL filters to pull a manageable slice for analysis. I will also focus on 2024 since it is a complete year. Lastly, I will keep a sample in the repo so that anyone can run the notebook without large downloads.

Example CSV query for selected fields and 2024:
```
https://data.cityofnewyork.us/resource/erm2-nwe9.csv?$select=unique_key,created_date,closed_date,agency,complaint_type,descriptor,borough,open_data_channel_type,latitude,longitude&$where=created_date >= '2024-01-01T00:00:00'&$limit=500000&$offset=0
```

## Expected Project Structure
```
data/
  sample_311_2024.csv      # subsample for the notebook
notebooks/
  final_report.ipynb       # main analysis and writeup
  data_munging.ipynb       # optional preprocessing steps
README.md
LICENSE
A4: Final Project Preliminary Proposal
```

## Reproducibility notes
The notebook lists the exact query, date, and fields used. It shows each step of cleaning and analysis with markdown cells. If you want to run on more data, increase the date range or the limit and offset values in the query.

## Ethics and limits
311 records are reports by people, not verified measurements. I will use safe aggregation, avoid raw text fields, include a clear limits section and avoid claims that could harm any neighborhood.

## References
NYC Open Data portal: https://opendata.cityofnewyork.us/  
Socrata API docs: https://dev.socrata.com/