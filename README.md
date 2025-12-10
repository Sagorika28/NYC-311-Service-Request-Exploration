# NYC 311 Service Requests Analysis: Response Time Patterns Across Channels and Geography

**DATA 512: Human-Centered Data Science**  
**Author:** Sagorika Ghosh  
**Date:** December 2025

---

## Abstract

**Background**: During my summer internship in NYC, I noticed how differently people experienced the 311 system depending on where they lived and how they reported issues. This got me wondering whether these patterns showed up in the data.

**Methods**: I analyzed over 1.8 million NYC 311 service requests from 2024, focusing on how response times varied across the 5 boroughs and 3 reporting methods (phone, web, and mobile app). I used statistical testing and built a simple predictive model to understand what factors mattered most.

**Results**: Response times differed quite a bit by borough - some areas got responses in about an hour while others waited several hours. Digital reporting (web and app) consistently led to faster responses than calling 311, even for the same types of complaints in the same neighborhoods. I also found that certain ZIP codes had slower responses across the board, creating geographic patterns of delayed service. Complaints that people mostly reported by phone took longer to close, and high-volume periods made delays worse in some boroughs (Bronx) but not others.

**Conclusions**: How you report a 311 issue matters - digital channels get faster responses. But geography plays a big role too, with some neighborhoods (Bronx) experiencing slower service regardless of how they report or what they're reporting about. These findings suggest opportunities to improve digital access and rethink how the city allocates resources to make 311 more equitable.

---

## Research Questions

This study investigates the following questions:

1. **How do average 311 response times differ across boroughs in 2024?**
2. **Which ZIP codes have statistically significant response time problems, and do certain complaint types cluster in slow-responding neighborhoods?**
3. **Do digital channels lead to faster responses than phone reports, and which complaint types rely most on phone reporting?**
4. **Does complaint volume or seasonal workload amplify delays, or do some boroughs and complaint types remain slow even during low-demand periods?**
5. **Can we predict whether a complaint will be slower than the norm for its issue, and which structural factors drive that risk?**

---

## Data Sources

### Primary Dataset
- **Source**: [NYC Open Data Portal](https://data.cityofnewyork.us/)
- **Dataset**: [311 Service Requests from 2010 to Present](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)
- **Dataset ID**: `erm2-nwe9`
- **License**: [NYC Open Data Terms of Use](https://www.nyc.gov/main/terms-of-use)
- **API Documentation**: [Socrata Open Data API (SODA)](https://dev.socrata.com/)
- **Data Collection Date**: November 17, 2024
- **Records Analyzed**: 1,869,316 service requests from calendar year 2024

### Key Fields Used
- `unique_key`: Unique identifier for each request
- `created_date`: When the complaint was filed
- `closed_date`: When the complaint was resolved
- `complaint_type`: Category of complaint
- `descriptor`: Specific details about the complaint
- `agency`: City agency responsible for handling the request
- `borough`: NYC borough (Bronx, Brooklyn, Manhattan, Queens, Staten Island)
- `incident_zip`: ZIP code where the issue occurred
- `open_data_channel_type`: How the complaint was submitted (Phone, Web, App)
- `latitude`, `longitude`: Geographic coordinates

### Data Access Method
The full dataset contains over 40 million records. I used the Socrata API with filters to extract only 2024 data:

```python
# Example API query
base_url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
params = {
    "$where": "created_date between '2024-01-01T00:00:00' and '2024-12-31T23:59:59'",
    "$limit": 25000,
    "$offset": 0,
    "$order": "created_date"
}
```

---

## Repository Structure

```
A7/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── Project Proposal.docx              # Original project proposal (A4/A5)
├── .gitignore                         # Git ignore rules
├── .env.example                       # Example environment variables file
├── create_sample_data.py              # Script to create sample dataset
│
├── notebooks/
│   ├── 00_data_cleaning.ipynb        # Data acquisition and cleaning
│   └── 01_final_report.ipynb         # Main analysis and report
│
├── src/
│   ├── nyc311_api.py                 # API data fetching utilities
│   └── nyc311_cleaning.py            # Data cleaning functions
│
├── data/
│   ├── raw/
│   │   └── nyc311_2024_raw.parquet   # Raw data from API (364 MB)
│   ├── processed/
│   │   └── nyc311_2024_cleaned.parquet # Cleaned data (197 MB)
│   └── sample/
│       └── nyc311_2024_sample.parquet # Sample data (1000 rows) for reproducibility
│
├── figures/
│   ├── rq1_borough_response_times.png
│   ├── rq1_geographic_hotspots.html
│   ├── rq2_zip_response_times.png
│   ├── rq2_zip_geographic_hotspots.html
│   ├── rq2_complaint_type_interactions.png
│   ├── rq3_channel_comparison.png
│   ├── rq3_channel_preference.png
│   ├── rq3_phone_heavy_comparison.png
│   ├── rq4_volume_and_demand.png
│   └── rq5_simple_ml_plots.png
│
└── outputs/
    ├── 00_data_cleaning.html         # HTML export of data cleaning notebook
    ├── 00_data_cleaning.pdf          # PDF export of data cleaning notebook
    ├── 01_final_report.html          # HTML export of final report notebook
    └── 01_final_report.pdf           # PDF export of final report notebook
```

---

## Reproducibility

### Prerequisites
- Python 3.8+
- Required packages: `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `scikit-learn`, `scipy`, `requests`, `python-dotenv`

### Setup Instructions

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install pandas numpy matplotlib seaborn plotly scikit-learn scipy requests python-dotenv
   ```

3. **Set up API credentials** (optional, for fetching fresh data):
   - Copy `.env.example` to `.env`
   - Get a free app token from [NYC Open Data](https://data.cityofnewyork.us/profile/edit/developer_settings)
   - Add your token to `.env`: `NYC_OPEN_DATA_APP_TOKEN=your_token_here`

4. **Run the notebooks**:
   - Start with `00_data_cleaning.ipynb` to understand data acquisition and cleaning
   - Then run `01_final_report.ipynb` for the complete analysis

Note:
- The PDFs of the notebooks are available in the `outputs` directory.
- Github Link for this project: https://github.com/Sagorika28/NYC-311-Service-Request-Exploration

### Notes on Data Size
- The full 2024 dataset is ~364 MB (raw) and ~197 MB (cleaned)
- A sample dataset will be provided in `data/sample/` for quick testing
- All analysis can be reproduced using the provided cleaned data

### Snapshot Information
- **Data snapshot date**: November 17, 2024, 05:35:13 UTC
- **Total records fetched**: 3,458,320 (before cleaning)
- **Records after cleaning**: 1,869,316
- **Cleaning steps**: Removed records with missing dates, invalid boroughs, or negative response times

---

## Methodology

### Data Cleaning

The raw 2024 data underwent several cleaning steps (implemented in `src/nyc311_cleaning.py`):

1. **Date Conversion**: Converted `created_date` and `closed_date` from strings to datetime format
2. **Response Time Calculation**: Calculated `response_time_days` = `closed_date` - `created_date`
3. **Invalid Record Removal**: Removed records with:
   - Missing `created_date`, `closed_date`, or `borough`
   - Negative or zero response times (data entry errors)
4. **Channel Standardization**: Standardized `open_data_channel_type` to three values:
   - PHONE to Phone
   - ONLINE/UNKNOWN/OTHER to Web
   - MOBILE to App
5. **Duplicate Removal**: Removed duplicate records using `unique_key`
6. **Outlier Treatment**: Winsorized response times at the 99th percentile (273.21 days) to limit outlier influence
7. **Complaint Type Selection**: Selected top 10 complaint types by volume for reliable within-category comparisons

This process reduced the dataset from 3,458,320 raw records to 1,869,316 cleaned records.

### Analysis Methods
- **Descriptive Statistics**: I calculated median, mean, standard deviation, minimum, and maximum response times by borough, channel, and complaint type. I focused on medians because response times are heavily right-skewed.
- **Statistical Testing (RQ2)**: To statistically validate the observed disparities in response times across boroughs, I employed the **Kruskal-Wallis H-test**, a non-parametric alternative to ANOVA suitable for non-normally distributed data. Significant findings indicate that at least one borough's response time distribution differs from the others.
- **Predictive Modeling (RQ5)**: I built a Random Forest classifier to understand what factors are associated with slow service. I defined the target as a binary label based on whether response time exceeded the global median, and included features such as complaint type, borough, channel, and time of submission. I evaluated the model using the ROC-AUC score and used feature importance to identify which predictors most strongly influence delays. This helped distinguish between procedural bottlenecks and potential structural patterns.
- **Visualizations**: To explore patterns visually, I created bar charts showing borough-level averages and medians, box plots illustrating distribution and spread, geographic maps built with Plotly to show spatial patterns of response times, and interactive maps that group complaints into small grid cells for clearer visualization of dense regions.

### Why These Methods Are Appropriate
Median-based analysis provides a more stable representation of response patterns when outliers are present. Non-parametric tests like Kruskal-Wallis are well suited for non-normal service data, and the model choice allows handling interactions between multiple features without heavy assumptions. Comparing channels within the same complaint type avoids misleading cross-type comparisons since different complaints have inherently different resolution times. Borough-level analysis maintains privacy while still revealing useful insights, and ZIP-level results are used cautiously. Winsorizing the top 1 percent of values limits extreme outlier influence while preserving distribution shape, and focusing on top complaint types ensures that comparisons are based on reliable sample sizes.

### Ethical Considerations
It is important to acknowledge that 311 data reflects who reports issues, not the full experience of all residents. I avoid interpreting results as objective measures of community conditions. To protect privacy, I removed free-text fields and presented results only at borough or ZIP aggregation levels. I am careful not to label any neighborhood as problematic and instead focus on systemic service patterns, potential sources of delay, and opportunities for improvement.

---

## Key Findings

1. **Borough disparities**: Median response times ranged from ~1 hour (Staten Island) to ~6 hours (Bronx)
2. **Structural delays in Bronx**: The Bronx remained the slowest borough even during low-demand periods, indicating systemic issues beyond just complaint volume
3. **Channel effects**: Digital channels (Web/App) showed faster responses than phone, even within the same complaint types
4. **Phone-heavy complaint types suffer**: Because digital channels are faster, complaint types that are predominantly reported by phone (like HEAT/HOT WATER) experience systematically slower resolution times
5. **Geographic clusters**: Certain ZIP codes had consistently slower responses across multiple complaint types
6. **Volume effects**: High complaint volume amplified delays in some boroughs (Bronx) but not others (Staten Island)

---

## Limitations

- Analysis limited to 2024 data only
- Cannot account for complaint severity or urgency
- Response time measures closure, not actual service delivery
- Digital access barriers may affect who uses which channel
- Borough-level aggregation may mask neighborhood-level patterns
- Seasonal patterns not fully explored due to single-year scope

---

## References and Resources

### Data Sources
- [NYC Open Data Portal](https://data.cityofnewyork.us/)
- [NYC 311 Service Requests Dataset](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data)
- [NYC Open Data Terms of Use](https://www.nyc.gov/main/terms-of-use)
- [NYC Open Data Law](https://opendata.cityofnewyork.us/open-data-law/)

### API Documentation
- [Socrata Open Data API (SODA)](https://dev.socrata.com/)
- [SODA Query Documentation](https://dev.socrata.com/docs/queries/)
- [SODA Filtering](https://docs.soda.io/sodacl-reference/filters)
- [Socrata API App Token](https://data.cityofnewyork.us/profile/edit/developer_settings)

### Related Research
- Kontokosta, C. E., Hong, B., & Korsberg, K. J. (2017). [Equity in 311 Reporting: Understanding Socio-Spatial Differentials in the Propensity to Complain](https://doi.org/10.48550/arXiv.1710.02452). *Journal of Urban Technology*, 24(3), 1-22.
- Wang, P., Hunter, T., Bayen, A. M., Schechtner, K., & González, M. C. (2017). [Structure of 311 service requests as a signature of urban ecology](https://doi.org/10.1371/journal.pone.0186314). *PLOS ONE*, 12(10).
- Kontokosta, C. E., & Hong, B. (2021). [Bias in smart city governance: How socio-spatial disparities in 311 complaint behavior impact the fairness of data-driven decisions](https://doi.org/10.1016/j.scs.2020.102503). *Sustainable Cities and Society*, 64, 102503.
- NYC 311 Language Access Implementation Plan (2024). [NYC.gov - Language Access Implementation Plan](https://www.nyc.gov/assets/oti/downloads/pdf/about/oti-311-language-access-plan-2024.pdf)
- Glaeser, E. L., Hillis, A., Kominers, S. D., & Luca, M. (2016). [Crowdsourcing City Government: Using Tournaments to Improve Inspection Accuracy](https://doi.org/10.1257/aer.p20161027). *American Economic Review*, 106(5), 114-118.

### Tools and Libraries
- [Python](https://www.python.org/)
- [Pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [scikit-learn](https://scikit-learn.org/)
- [SciPy](https://scipy.org/)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The NYC 311 data is provided by the City of New York under the [NYC Open Data Terms of Use](https://www.nyc.gov/main/terms-of-use, https://opendata.cityofnewyork.us/open-data-law/).

---

## Contact

For questions or feedback about this analysis, please contact Sagorika Ghosh (sagorika@uw.edu).

**Course**: DATA 512: Human-Centered Data Science  
**Institution**: University of Washington  
**Quarter**: Fall 2025