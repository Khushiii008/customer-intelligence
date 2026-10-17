# Customer Intelligence Dashboard

An interactive machine learning dashboard that segments customers based on their purchasing behaviour using **K-Means clustering**.

## Project Overview

This project analyses customer-level purchasing patterns to identify groups with different spending habits, purchase frequencies, and recency. The results are presented through an interactive dashboard built with Streamlit and Plotly.

## Features

- Customer segmentation using K-Means clustering
- Customer-level feature engineering using Recency, Frequency, and Monetary value (RFM)
- Interactive visualisations for segment distribution and customer behaviour
- Spending distribution analysis using logarithmic transformation for visualisation
- Segment filtering and customer exploration
- Downloadable customer segment data

## Tech Stack

- Python
- Pandas and NumPy
- Scikit-learn
- Streamlit
- Plotly
- Jupyter Notebook

## Dataset Attribution

This project uses the **Online Retail** dataset from the UCI Machine Learning Repository.

- **Creator:** Daqing Chen
- **Source:** https://doi.org/10.24432/C5BW33
- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

The original dataset was used for educational and portfolio purposes. Data cleaning, customer-level feature engineering, clustering, and visualisation were performed as part of this project.

## Project Files

- `app.py` — Streamlit dashboard application
- `customer_segments.csv` — Prepared customer-level data with cluster assignments
- `notebook.ipynb` — Data preparation, exploratory analysis, and modelling workflow
- `requirements.txt` — Python dependencies

## Run Locally

1. Clone this repository.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

## Methodology

1. Clean the original transaction data.
2. Remove cancelled transactions and prepare customer-level features.
3. Calculate Recency, Frequency, and Monetary value.
4. Standardise the selected features.
5. Use the elbow method to help choose the number of clusters.
6. Apply K-Means clustering and interpret the resulting customer segments.
7. Explore the results through an interactive dashboard.

---
## Live Link : https://customer-intelligence-ghrpc7rmiuwfr7refmgpsn.streamlit.app/
*Built as a machine learning and data visualisation portfolio project.*
