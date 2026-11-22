# Demand Intelligence & Forecasting

**How much forecasting complexity does a product portfolio actually need?**

[English](README.md) | [Español](docs/README.es.md) | [Method and data / Método y datos](docs/methodology.md)

When hundreds of products have different purchasing patterns, forecasting is only part of the job. Someone must also decide which forecasts deserve review and when a more complex model adds value.

I built this case using 52 indexed weeks of observed quantities for 811 products from the UCI *Sales Transactions Weekly* dataset. I compared simple forecasting methods, evaluated them on later weeks, and designed a practical review queue for commercial planners.

## What the results say

| Final holdout, weeks W44 to W51 | WAPE | Bias |
| --- | ---: | ---: |
| Naive baseline | 33.73% | -2.50% |
| Global simple exponential smoothing (SES) | **27.45%** | -3.73% |
| Segmented ABC/XYZ model policy | 27.63% | -6.03% |

The global SES model reduced pooled absolute error by **18.6%** compared with the naive baseline. A more elaborate ABC/XYZ model policy did not outperform it in this evaluation.

That result changed the practical recommendation. Rather than add complexity for its own sake, I would retain the simple global model as the default and use segmentation to organize analysts' attention. The prospective review queue highlights unusual purchasing patterns and recent changes without using holdout outcomes.

## Explore the work

The code includes a Streamlit dashboard covering model performance, product-level forecasts, ABC/XYZ portfolio diagnostics, retrospective exceptions and a prospective Decision Center. The dashboard supports **English and Spanish**.

**Deployment status:** the repository contains the publication candidate. A verified public Streamlit URL will be added only after the cloud app has been deployed and checked.

## Data and boundaries

The original dataset contains 811 anonymous products and 52 relative weekly indices. These are **observed purchase quantities**, not confirmed unconstrained demand. There are no actual calendar dates, prices, costs, inventory balances, stockout indicators, promotions or lead times. ABC groups refer to historical unit volume, not revenue.

Forecasts and review rules are not inventory orders, monetary risk estimates or proven causal effects. Only two forecast origins were used for the final holdout, so product-level performance should not be generalized without more data.

**Source:** Tan, J. (2014), *Sales Transactions Weekly*, UCI Machine Learning Repository, DOI: https://doi.org/10.24432/C5XS4Q, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Original dataset is credited and reproduced without claiming ownership. No client data are included.

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python reproduce.py
streamlit run app.py
```

The source dataset and generated outputs are incorporated through a documented build process. See [data setup](docs/DATA.en.md) and [methodology](docs/methodology.md). The final output tables can be regenerated with the commands above.

**Carlos Segura | CS Intelligence**
