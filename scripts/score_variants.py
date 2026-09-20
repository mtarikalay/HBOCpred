"""Read an annotated Excel/CSV table and score it with the saved HBOCpred model."""
from pathlib import Path
import argparse
import sys

import joblib
import numpy as np
import pandas as pd
from hbocpred_core import predict_partition

ROOT = Path(__file__).resolve().parents[1]
GENES = {
    "ATM", "BARD1", "BLM", "BRCA1", "BRCA2", "BRIP1", "CDH1", "CHEK2",
    "FANCA", "FANCC", "NBN", "PALB2", "PTEN", "RAD51C", "RAD51D", "STK11", "TP53",
}
IDENTIFIERS = ["SPDI", "Gene", "HGVSc", "HGVSp", "Feature", "MANE_SELECT",
               "rsID", "clinvar_id", "clinvar_review", "y"]
MISSING = {"", "-", ".", "na", "nan", "none", "null", "n/a"}


def read_input(path: Path) -> pd.DataFrame:
    """Excel: first worksheet, headers in row 1. Predictor cells must be numeric."""
    if path.suffix.lower() in {".xlsx", ".xlsm"}:
        raw = pd.read_excel(path, engine="openpyxl", header=None, dtype=object)
    elif path.suffix.lower() == ".csv":
        raw = pd.read_csv(path, header=None, dtype=object)
    else:
        raise ValueError("Input must be .xlsx, .xlsm or .csv; save old .xls files as .xlsx.")
    if raw.empty or len(raw) < 2:
        raise ValueError("The input contains no variant rows.")
    headers = [str(v).strip() if pd.notna(v) else "" for v in raw.iloc[0]]
    if any(not h for h in headers) or len(set(headers)) != len(headers):
        raise ValueError("Row 1 must contain non-empty, unique column names.")
    data = raw.iloc[1:].copy().reset_index(drop=True)
    data.columns = headers
    if data.isna().all(axis=1).any():
        raise ValueError("Remove entirely empty rows from the input table.")
    return data


def prepare_features(data: pd.DataFrame, model: dict) -> pd.DataFrame:
    if "Gene" in data:
        genes = data["Gene"].astype("string").str.strip().str.upper()
        invalid = genes.isna() | ~genes.isin(GENES)
        if invalid.any():
            rows = (data.index[invalid] + 2).tolist()[:5]
            raise ValueError(f"Missing or out-of-scope Gene values at worksheet rows {rows}.")
    panel = model["panel"]
    required = int(np.ceil(0.8 * len(panel)))
    if sum(c in data for c in panel) < required:
        raise ValueError(
            f"At least {required}/{len(panel)} named predictor columns are needed. "
            "Use the supplied variants.xlsx headers. Variant names alone are not annotated."
        )
    features = pd.DataFrame(index=data.index)
    for column in model["columns"]:
        if column not in data:
            features[column] = np.nan
            continue
        values = data[column]
        missing = values.isna() | values.astype(str).str.strip().str.lower().isin(MISSING)
        numeric = pd.to_numeric(values.mask(missing), errors="coerce")
        invalid = (~missing & numeric.isna()) | np.isinf(numeric.to_numpy(dtype=float))
        if invalid.any():
            rows = (data.index[invalid] + 2).tolist()[:5]
            raise ValueError(f"Non-numeric predictor '{column}' at worksheet rows {rows}.")
        features[column] = numeric.astype(float)
    return features


def write_output(results: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        results.to_csv(path, index=False)
        return
    from openpyxl.styles import Alignment, Font
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        results.to_excel(writer, index=False, sheet_name="Results")
        sheet = writer.sheets["Results"]
        sheet.freeze_panes = "C2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            sheet.column_dimensions[cell.column_letter].width = 38 if cell.value == "SPDI" else 23
        sheet.row_dimensions[1].height = 32
        # Preserve identifiers/vote vectors as literal text, not spreadsheet formulas.
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                if isinstance(cell.value, str):
                    cell.data_type = "s"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("variants.xlsx"))
    parser.add_argument("--output", type=Path, default=Path("results.xlsx"))
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must be different files.")
        if args.output.suffix.lower() not in {".xlsx", ".csv"}:
            raise ValueError("Output must be .xlsx or .csv.")
        if args.output.exists():
            raise FileExistsError(f"Output already exists: {args.output}. Choose another name.")
        data = read_input(args.input)
        # Only the saved model bundled with this repository is loaded; no fitting occurs.
        model = joblib.load(ROOT / "models" / "deployment.joblib")
        features = prepare_features(data, model)
        predictions = predict_partition(model, features)
        identity = [c for c in IDENTIFIERS if c in data]
        results = pd.concat([data[identity], predictions], axis=1)
        write_output(results, args.output)
        count = int(predictions.complete_flag.sum())
        print(f"Saved {args.output}: {len(results)} rows; {count} scored; "
              f"{len(results) - count} incomplete (scores withheld).")
        return 0
    except (OSError, ValueError, KeyError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
