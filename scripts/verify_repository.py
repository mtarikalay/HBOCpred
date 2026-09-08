"""Check distributed files and replay the frozen deployment model."""
from pathlib import Path
import hashlib
import json
import joblib
import numpy as np
import pandas as pd
from hbocpred_core import predict_partition, LEARNERS

ROOT = Path(__file__).resolve().parents[1]
for line in (ROOT / "SHA256SUMS").read_text().splitlines():
    expected, name = line.split(maxsplit=1)
    with (ROOT / name).open("rb") as handle:
        assert hashlib.file_digest(handle, "sha256").hexdigest() == expected, name

anchors = pd.read_csv(ROOT / "data/anchors_all_numeric.csv")
application = pd.read_csv(ROOT / "data/application_all_numeric.csv.gz")
oof = pd.read_csv(ROOT / "outputs/oof_predictions_repeated_cv.csv")
folds = pd.read_csv(ROOT / "outputs/fold_assignments.csv")
genes = pd.read_csv(ROOT / "outputs/logo_predictions.csv")
assert len(anchors) == 2160 and anchors.SPDI.is_unique
assert len(application) == 43679 and application.SPDI.is_unique
assert not set(anchors.SPDI) & set(application.SPDI)
assert len(oof) == 10800 and not oof.duplicated(["SPDI", "repeat"]).any()
assert oof.groupby("repeat").SPDI.nunique().eq(2160).all()
keys = ["SPDI", "repeat", "outer_fold"]
assert set(map(tuple, oof[keys].to_numpy())) == set(map(tuple, folds[keys].to_numpy()))
assert genes.SPDI.is_unique and set(genes.SPDI) == set(anchors.SPDI)

model = joblib.load(ROOT / "models/deployment.joblib")
maximum_error = 0.0
for data, file in [(anchors, "deployment_predictions.csv"), (application, "application_catalogue.csv.gz")]:
    expected = pd.read_csv(ROOT / "outputs" / file)
    assert data.SPDI.tolist() == expected.SPDI.tolist()
    actual = predict_partition(model, data)
    for column in ["S_MAC", "Mean4", "V", "complete_flag", "n_observed_panel"] + ["p_" + x for x in LEARNERS] + ["vote_" + x for x in LEARNERS]:
        np.testing.assert_allclose(actual[column], expected[column], atol=1e-12, rtol=1e-10, equal_nan=True)
        maximum_error = max(maximum_error, float(np.nanmax(np.abs(actual[column] - expected[column]))))
empty = application.iloc[:1].copy()
empty.loc[:, model["panel"]] = np.nan
assert predict_partition(model, empty)[["S_MAC", "V"]].isna().all().all()
print(json.dumps({"distributed_files": "checksums verified", "deployment_model_replayed": True,
                  "anchor_records": len(anchors), "application_records": len(application),
                  "maximum_numeric_difference": maximum_error,
                  "oof_identity_and_fold_mapping": "verified",
                  "scope": "Deployment replay and recorded row/fold checks; omitted fold models are not replayed."}, indent=2))
