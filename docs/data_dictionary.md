# Data dictionary

The unit is a genomic variant record, not a patient. Rows with identical genomic identity are not separate observations within the primary source or application catalogue.

| Field | Meaning |
|---|---|
| SPDI | Sequence accession:zero-based position:deleted sequence:inserted sequence; chromosome accessions imply the archived reference assembly |
| Gene | Source study-gene symbol; excluded as an explicit main predictor |
| y | Processed source outcome: 0 = B/LB, 1 = LP/P; not an independently adjudicated ground truth |
| ACMG_variations | Original processed LB/LP source grouping |
| clinvar_clnsig | Embedded annotation snapshot of clinical significance; retained separately from y |
| clinvar_review | Embedded review-status text; missing/unmapped is NR, not an ordered evidence tier |
| clinvar_hgvs / HGVSc / HGVSp | Source genomic/coding/protein annotation as supplied; version and alignment must be checked |
| Feature / MANE_SELECT | Source transcript identifiers where present; current audit does not overwrite historical assignments |
| numeric predictors | Source units and rank-score fields retained; no cross-tool rescaling until training-fitted standardisation |
| Reliability_index | Annotation metadata; available in the numeric archive and inclusion sensitivity, excluded from primary fitting |
| SpliceAI_DS_max | Row-wise maximum of four SpliceAI delta scores; all missing remains missing |
| p_SVM_RBF, p_ENET_LR, p_EXTRA_TREES, p_HIST_GB | Calibrated source-direction scores; not clinical risk probabilities |
| vote_* | Binary decision at that fitted learner's training-derived threshold |
| vote_vector | Four-character string in SVM_RBF, ENET_LR, EXTRA_TREES, HIST_GB order; retain leading zeroes |
| V | Integer 0–4, sum of LP/P-directed votes; missing if incomplete |
| directional_descriptor | Unanimous B/LB-directed / Mixed votes / Unanimous LP/P-directed; same mapping in every dataset |
| Mean4 | Mean of four calibrated learner scores; no extra vote |
| S_MAC | Logistic meta-calibration of Mean4; research ranking score |
| n_observed_panel | Number of observed selected-panel values before imputation |
| panel_size | Number of selected predictors in that particular fit |
| complete_flag | 1 iff n_observed_panel >= ceil(0.8 * panel_size); otherwise all model outputs are missing |
| partition | Saved fit identifier (repeat/fold, held-out gene, sensitivity or deployment) |
| repeat / outer_fold | Outer CV split membership; repeated rows must not be treated as independent variants |
| TP, TN, FP, FN | Counts at V >= 3 among evaluable records, relative to y |
| n_total / n_evaluable | All source rows and scored subset for the corresponding analysis |
| AUROC, AUPRC, Brier | Continuous performance against source labels using S_MAC, conditional on evaluability |
| SMD | Observed-value application-minus-anchor mean difference divided by sqrt((sample variance A + sample variance B)/2) |

Missing numeric fields are NaN/empty CSV cells, not zero scores. Source multi-valued annotations use the first finite numeric token separated by comma or semicolon; this is reproducible but not a verified transcript-matching procedure. The deployment panel matrix is before imputation; fitted objects contain the exact medians/scales and model-ready transformations. Per-fold panels can differ and are recorded in the fit audits.

For the gnomAD audit, `variant_id` is GRCh38 chromosome-1-based-position-ref-alt. `AF` is AC/AN within the selected callset/population; `qualifying_populations` retains every qualifying combination. The screen uses alternate-allele frequency >0.05, AN >=2000 and PASS records in afr/amr/eas/nfe/sas/mid. `minor_AF` is supplied separately and is not silently substituted. Overlap flags distinguish anchors, all 7,137 training records and the unresolved archive. `eligible_any_transcript_no_overlap` is an annotation/identity condition only. BA1 adjudication and clinical prediction fields are explicitly uncompleted.
