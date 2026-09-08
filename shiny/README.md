# HBOCpred Shiny viewer R4.3

The R4.3 interface adds a navy and teal header, clearer filter controls, compact summary cards, a cleaner catalogue table and a responsive layout. The selected-variant chart appears after a row is selected. The About this release tab and visible version badge remain removed. Search, filtering, downloads, learner scores and thresholds, per-gene results and eight figures are retained. The R4 catalogue, fitted model outputs and analysis figures are unchanged.

## Run and publish

Extract the ZIP, open `HBOCpred.Rproj` in RStudio, and install required packages if needed:

```r
install.packages(c("shiny", "DT", "jsonlite", "rsconnect"),
                 repos = "https://cloud.r-project.org")
source("run_local.R")
```

Stop the local app before publishing. In the RStudio session connected to the existing **alaymd** shinyapps.io account:

```r
source("deploy_hbocpred.R")
deploy_hbocpred()
```

The helper loads the app and checks catalogue integrity before resolving and updating the existing **hbocpred** application by ID. It does not create a different application. `deploy_hbocpred(check_only = TRUE)` runs local checks only. An unconfigured account must first be connected through RStudio’s Publishing settings. No credentials are included in this package.

After successful deployment, verify https://alaymd.shinyapps.io/hbocpred/ has only the Variant catalogue and Model audit tabs and unfiltered counts **43,679 / 33,414 / 4,491 / 5,774**. The viewer version is retained in HTML metadata (`hbocpred-viewer-release`) and `data/release.json`, without a visible release panel.

## Verification status

The source comparison confirms that the server code, catalogue, numerical data, all eight figure assets and 58 fitted model objects are unchanged from R4.2. Six R files pass syntax parsing. The eight executable checks in `tests/test_app.R` passed in R 4.4.3, including actual Shiny server filtering, row selection, plots, counters and exports. The deployment preflight loaded the application successfully and selected 18 application files. See `tests/runtime_verification.json`, `tests/interface_update_verification.json`, `tests/deployment_preflight.json` and `tests/R_session_info.txt` for the recorded evidence.

Browser verification is recorded separately in `tests/browser_verification.json`, with screenshots in `tests/evidence/R4_3/`. Prior R4.1 and R4.2 verification records remain under `tests/history_R4_1/` and `tests/history_R4_2/`.

Public deployment has not been performed from the preparation environment: no alaymd account is configured there. Run the deployment commands above in the RStudio session connected to the existing account.

## Interpretation and provenance

The deployment panel requires at least 20 observed predictors out of 25. All 43,679 saved records satisfy this rule. V0 and V4 describe unanimous model direction; V1–V3 describe mixed votes. These are not ACMG/AMP classes. V0 does not justify exclusion from review, and S_MAC is a ranking score, not a clinical risk probability. Source annotations remain separate from model outputs. Unseen variants receive no new prediction in this catalogue viewer.

The internal audit remains subject to source-label dependence, upstream training overlap and development-to-application shift. The gnomAD figure describes eligibility and archive overlap, not external validation: 50 candidates, 47 full-training overlaps, one additional application-archive overlap and two unscored candidates outside both archives. These scientific qualifications remain in the analysis documentation and relevant result displays.

The deployment file list includes only app.R, R/, www/ and data/. Tests, development evidence and deployment scripts are excluded from the uploaded application bundle.
