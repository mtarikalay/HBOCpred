# HBOCpred

Research prioritisation of germline missense variants in 17 hereditary breast and ovarian cancer genes.

## Use

With Python 3.12, run from the repository folder:

```bash
python -m pip install -r requirements.txt
python scripts/score_variants.py --input variants.xlsx --output results.xlsx
```

The first worksheet must contain the predictor column names shown in the [feature matrix](data/anchor_deployment_panel.csv). Enter numeric scores and leave missing values blank. At least 20 of the 25 scores are required per variant. The script uses the saved model; it does not retrieve annotations or retrain the model.

## Study files

[25-predictor feature matrix](data/anchor_deployment_panel.csv) (2,160 variants; SPDI, Gene, y and 25 predictors).

[Predictions and fold assignments](outputs/) · [Analysis scripts](scripts/) · [Data dictionary](docs/data_dictionary.md)

All fitted models are included in Supplementary Data S1 (`HBOCpred_Reproducibility.zip`).

Outputs are for research prioritisation, not ACMG/AMP classification.
