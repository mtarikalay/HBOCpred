# HBOCpred

Research prioritisation of germline missense variants in 17 hereditary breast and ovarian cancer genes.

## Install

Use Python 3.12 or 3.13. In the repository folder, run:

```bash
python -m pip install -r requirements.txt
```

## Run from Excel

Place your annotated Excel file in the repository folder and run:

```bash
python scripts/score_variants.py --input variants.xlsx --output results.xlsx
```

The script reads the first worksheet, uses the saved model in `models/deployment.joblib`, and writes the results to Excel. It does not retrain the model. R and Shiny are not required. CSV input and output are also supported.

## Input

Use the predictor column names in [`data/anchor_deployment_panel.csv`](data/anchor_deployment_panel.csv). The first row contains headers; predictor cells contain numeric scores or are left blank. Each variant needs at least 20 of the 25 predictor values. Scores are withheld for incomplete rows. Variant names alone are not enough: this script does not retrieve annotations.

Results include the four model probabilities and votes, the vote vector, S_MAC and completeness indicators. These are research outputs, not ACMG/AMP classifications.

## Study materials

Processed matrices, analysis code and saved outputs remain in `data/`, `scripts/` and `outputs/`. The complete frozen study snapshot, including all cross-validation models, is supplied separately as Supplementary Data S1 (`HBOCpred_Reproducibility.zip`); it is not GitHub's automatically generated source-code ZIP.

[Data dictionary](docs/data_dictionary.md) · [Method](docs/method.md)

Code: MIT licence. Third-party annotations: see `DATA_LICENSE.md`.
