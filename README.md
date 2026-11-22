# Demand Intelligence & Forecasting

**When hundreds of products behave differently, which forecasts should a planner trust and review first?**

[English](README.md) | [Español](docs/README.es.md) | [Methodology](docs/methodology.md) | [Data and reproduction](docs/DATA.en.md)

A commercial planning team needs forecasts it can explain and a practical way to decide where to spend its attention. More complex models are not automatically more accurate. I tested that trade-off using 52 indexed weeks of observed purchase quantities for 811 products from the UCI *Sales Transactions Weekly* dataset.

## What I found

| Final evaluation, W44 to W51 | WAPE | Forecast bias |
| --- | ---: | ---: |
| Baseline: repeat the last observed week | 33.73% | -2.50% |
| Simple exponential smoothing (SES) | **27.45%** | -3.73% |
| Model selection by ABC/XYZ segment | 27.63% | -6.03% |

SES reduced the total absolute quantity error by **18.6%** versus the baseline. Choosing different methods by ABC/XYZ segment did not improve the overall result. In this case, using one simple method per product is a better starting point than adding model-selection complexity.

The aggregate result is not the whole story. In the final evaluation, the A/X segment represented 43,424 of 56,528 observed units and had a 22.22% WAPE under SES. The C/Z segment represented only 1,287 units and had a 93.59% WAPE. These differences show why a planner should review errors by product group as well as across the entire portfolio. ABC here reflects historical unit volume, not revenue or profitability.

## From forecast to review

I built an interactive, bilingual Streamlit application to examine model performance, product histories, ABC/XYZ segments and a prioritized review list. The list uses **only observations through W43**, with forecasts for W44 and W44 to W47. It ranks products by historical volume, variability and recent quantity changes. These are historical demonstration periods, not current calendar-week forecasts.

The review list can be filtered and exported as CSV. Its priority levels indicate where an analyst might investigate; they are not calibrated probabilities of stockouts or purchase orders.

## Live dashboard

[Open the interactive dashboard](https://demand-intelligence-forecasting-biexn2j5lhinfwgmdybb2x.streamlit.app/). The application includes model comparison, ABC/XYZ error analysis and an exportable product-review list in English and Spanish.

## Explore and reproduce

The repository includes the Streamlit application in `app.py`, model code, tests, permitted source data and reproducible outputs. To run it locally:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python reproduce.py
streamlit run app.py
```

See [methodology](docs/methodology.md) for the temporal evaluation and model definitions, and [data notes](docs/DATA.en.md) for source, license and reproducibility. The dashboard supports both English and Spanish.

## Data and interpretation

WAPE is the total absolute forecast error divided by total observed units; lower is better. Bias measures the signed forecast difference relative to observed units. Neither is a financial impact estimate.

The UCI series provide observed purchased quantities, not confirmed unconstrained demand. They have no real calendar dates, prices, costs, inventory records, stockout events, promotions or lead times. The final evaluation uses only two forecast origins, so these results do not establish long-term superiority for individual products.

**Source:** Tan, J. (2014), *Sales Transactions Weekly*, UCI Machine Learning Repository, [DOI: 10.24432/C5XS4Q](https://doi.org/10.24432/C5XS4Q), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Carlos Segura | CS Intelligence**
