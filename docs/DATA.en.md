# Data source and reproduction

[English](DATA.en.md) | [Español](DATA.es.md)

The original **Sales Transactions Weekly** dataset is published by James Tan through UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/396/sales+transactions+dataset+weekly. DOI: https://doi.org/10.24432/C5XS4Q. UCI lists the dataset under **Creative Commons Attribution 4.0 International**, https://creativecommons.org/licenses/by/4.0/.

The source is used as published, with attribution. No client data are included. The model uses Product_Code and W0 to W51. The normalized variables included in the original file are excluded from the analysis.

Run from the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/fetch_uci_data.py
python -m pytest -q
python reproduce.py
streamlit run app.py
```

The download script retrieves the UCI archive, selects the original CSV and checks SHA-256 against the version used in the analysis: `6f939a928c04820bc291a6184f4f1d0be694b8de58d949e808852804f25969c3`. A changed hash stops the process for review rather than silently changing results.

The publishing workflow commits the verified CSV and generated output tables so Streamlit can start without rerunning models on every page load. To rebuild, run `python reproduce.py` and review metrics against the documented baseline. No calendar dates can be inferred from the relative week indices.

The underlying dataset remains under CC BY 4.0. The public availability of source code does not imply that its author has adopted a separate open-source code license.
