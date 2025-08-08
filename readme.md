# Multifactor visual analysis of the spread of epidemiological diseases and their relationship with sociodemographic factors

This repository contains the implementation of the work presented in the paper "Multifactor visual analysis of the spread of epidemiological diseases and their relationship with sociodemographic factors". The project offers a comprehensive visual framework to analyze the spatiotemporal evolution of diseases in relation to key sociodemographic factors.

Our goal is to enable the simultaneous spatial and analytical interpretation of complex data, thereby improving evidence-based decision-making for public health strategies.


## Project Evolution: From Concept to a Robust Dashboard

This project's development was an iterative process that culminated in a refined, final dashboard. We initially implemented four distinct dashboards, each building upon the last to overcome specific limitations and enhance the user's analytical capabilities.

* **Dashboard 1:** The initial prototype focused on basic visualizations, primarily a geographical map with temporal progression. It allowed for a fundamental understanding of case spread but lacked the tools to correlate this data with sociodemographic factors.

* **Dashboard 2:** This version introduced basic sociodemographic data integration, allowing users to see some correlations. However, the visualization was static and did not yet feature the interactive and multivariate analysis capabilities we aimed for.

* **Dashboard 3:** We focused on improving interactivity and data segmentation. This dashboard introduced the concept of grouping regions with similar behavior (clusters), a key feature that would be refined in the final version.

* **Dashboard 4 (Final Version):** This is the definitive implementation, integrating all the previous improvements into a single, cohesive tool. It features coordinated views (map, time series, and radial charts) that allow for a dynamic, multifactor analysis of disease spread and its connection to community characteristics. This version effectively fulfills all the analytical requirements of the paper.


## Key Features
* **Regional Behavior Analysis:** The system identifies and groups regions with similar epidemiological behavior (clusters). It then visually displays central tendency and dispersion measures for these groups

* **Key Sociodemographic Factors:** The tool helps identify the most influential sociodemographic factors for each regional group, allowing for visual comparison between them

* **Spatiotemporal Visualization:** It visualizes the spatiotemporal evolution of cases on an interactive map. Regions are colored according to their cluster, and case density is represented visually, highlighting outbreak points and risk zones.

* **Interactive Control:** An interactive control panel lets users select datasets and configure sociodemographic factors for analysis. It also offers temporal exploration, with an option to play an automatic animation of case evolution or manually control a timeline.


## Data Used

* **Epidemiological Data:** COVID-19 cases in the New South Wales, Australia region, from January 25, 2020, to February 7, 2022. This dataset includes case date, and the code for the Local Health District (LHD) and Local Government Area (LGA). The data was sourced from the NSW Ministry of Health.

* **Sociodemographic Data:** Contains sociodemographic and economic data for 128 Local Government Areas (LGAs), including median age, median income, public transport usage, and population density. This data was extracted from the 2016 census.


## Technologies and Tools
* **Python:** The core language for data processing and backend logic.

* **Pandas & NumPy:** For data manipulation and numerical operations.

* **SciPy & Scikit-learn:** For statistical analysis and clustering techniques (like MDS).

* **Streamlit:** Used to build the interactive web application and dashboards.

* **Matplotlib & Plotly:** For generating visualizations like the correlation matrix, radial charts, and time series.

* **GeoPandas:** For handling geospatial data and map visualizations.

## Repository Structure

```
├── data/
│   ├── covid_cases.csv
│   ├── sociodemographic_data.csv
│   └── geojson_data.geojson
├── notebooks/
│   └── exploratory_data_analysis.ipynb
├── dashboards/
│   └── final_dashboard.py
├── paper/
│   └── paper_tcd.pdf
├── requirements.txt
└── README.md

```

### How to see Demo

You can go to [url]

### How to Run the Project Locally

Clone the repository:
```
git clone [repository_url]
```

Run the dashboard in VSC:
* Download the extension **Live Server**
* Right click on the file "dashboard4.html" and select **"open with Live Server"**


## Read the Full Paper
For a detailed explanation of the methodology, model, results, and case studies, you can read the full paper

