INTRO = 'We thank the reviewer for the detailed second-round assessment. We have refitted the models, applied the same annotation-completeness rule during evaluation and application, and replaced the affected results. The manuscript now uses shared vote descriptors, reports every gene holdout, excludes Reliability_index from the primary analysis, and removes the application-based missingness screen. Claims of independent external validation have been withdrawn. The following responses quote each substantive reviewer comment in full. Section numbers in the comments refer to the reviewed version; response locations refer to the current revision.'

ITEMS = [('1. Common evaluated and applied output; retrospective reporting choice',
  'The evaluated output is never issued on the population the framework is for. The three-output rule '
  'applies only to labelled records: V0 is reported as predicted B/LB, V1–V3 as Uncertain and V4 as '
  'predicted LP/P. For the 43,679 unresolved records the same states are displayed instead as '
  'Uncertain-low, Uncertain-mid and Uncertain-high. Every performance figure in the Abstract — 94.86% '
  'definite-output coverage, 5.14% Uncertain, 97.51% source-direction concordance — therefore describes '
  'an output that is by construction never produced for the variants the tool exists to prioritise, '
  'while the labels those variants do receive have no reported performance characteristics at all. '
  'Section 4.9 further states that the three-output rule was determined deterministically from the '
  'current V-states, so the rule was selected after inspecting where the anchors fell and its coverage '
  'and concordance figures are in-sample for the rule itself.',
  ['We agree. Every evaluable record now receives the same vote-state descriptor: V0, unanimous '
   'B/LB-directed; V1–V3, mixed votes; V4, unanimous LP/P-directed. Source classification is a separate '
   'metadata field. These descriptors are used in the manuscript, frozen catalogue, scoring function '
   'and revised Shiny source. We removed the former predicted clinical-class labels and the '
   'unresolved-only zones.',
   'The reporting convention and fixed learner set are explicitly described as revision-stage choices '
   'informed by prior development. Repeated nested evaluation excludes outer-test data from fitting, '
   'but it does not independently validate the historical selection of the reporting convention or '
   'architecture. The first-repeat unanimity summary is therefore a descriptive audit of the specified '
   'model, not an estimate of clinical accuracy or validation of a prespecified triage rule.',
   'The same annotation guard now also applies to held-out predictions. In each repeat, 2,046/2,160 '
   'anchors are evaluable and 114 are incomplete. First-repeat unanimous-vote coverage is 1,968/2,160 '
   '(91.11%), and conditional source agreement is 1,920/1,968 (97.56%). All 43,679 application records '
   'are evaluable; 33,414 have V0, 4,491 mixed votes and 5,774 V4. Reference outcomes are absent for '
   'this application population, so no performance characteristic is attributed to it.'],
  'Abstract; Introduction aim paragraph; Results 2.2–2.3; Methods 4.1–4.2 and 4.6; Table 5; Figures 1 '
  'and 3; scripts/hbocpred_core.py; outputs/application_catalogue.csv.gz.'),
 ('2. Direction versus uncertainty nomenclature',
  'The zone nomenclature inverts its own meaning. Uncertain-low denotes V0, zero LP/P-directed votes, '
  'and Uncertain-high denotes V4, unanimous agreement. These are the two states of lowest model '
  'uncertainty, while V2, the state of maximum disagreement, is placed inside Uncertain-mid. The '
  'qualifier switches referent from uncertainty to pathogenic direction without notice, so a curator '
  'scanning the released catalogue reads the triage signal backwards unless they have read Section 4.2.',
  ['We agree and have removed Uncertain-low, Uncertain-mid and Uncertain-high throughout the current '
   'output schema. “Unanimous B/LB-directed”, “Mixed votes” and “Unanimous LP/P-directed” describe the '
   'quantity actually represented. V2 remains exact 2:2 disagreement. We do not equate learner '
   'agreement with biological certainty, a calibrated uncertainty probability, or independent evidence '
   'strength.',
   'The first-repeat V2 and V3 LP/P fractions in the new fit are 11/25 (44.0%; Wilson interval '
   '26.7–62.9%) and 13/26 (50.0%; 32.1–67.9%). These overlapping intervals do not support ordinal '
   'tiers. The previous point-ordering reversal belongs to the superseded fit and is not carried '
   'forward as a current result.'],
  'Results 2.3; Discussion; Methods 4.2; Figure 3; Abbreviations; shared catalogue and viewer '
  'descriptors.'),
 ('3. External arms, population selection and upstream overlap',
  'Neither external arm can estimate a performance characteristic, and the benign arm restates its own '
  'selection criterion. The hospital arm contains 16 LP/P variants and no benign records; the gnomAD '
  'arm contains 49 benign proxies and no pathogenic records. No external confusion matrix therefore '
  'exists, and no external sensitivity, specificity or accuracy can be derived, yet the Abstract '
  'presents both arms as independent validation. The gnomAD arm is the more serious. Section 4.7 states '
  'that the proxies were selected as common missense variants, that is, on allele frequency, while the '
  "model's top-ranked feature, retained in 25 of 25 outer folds, is BayesDel_addAF_rankscore, in which "
  'addAF denotes the variant that incorporates allele frequency, and the third-ranked feature derives '
  'from AlphaMissense, whose training labels were themselves constructed from population frequency. '
  'That none of the 49 proxies reached V4 largely restates how they were chosen. The arm is '
  'additionally unable to separate V0 from V1–V2, so it cannot estimate the predicted-B/LB rate that '
  'the three-output rule reports. The hospital arm consists largely of long-documented alleles such as '
  'BRCA1 c.181T>G p.(Cys61Gly) and TP53 c.742C>T p.(Arg248Trp) that are present in public variant '
  'resources and in all probability in the training corpora of the ClinVar-derived constituent '
  'predictors; anchor-overlap screening does not remove this, since absence from the 2,160-variant '
  'anchor set does not imply absence from ClinVar. Its 15/16 result carries a Wilson interval of '
  '71.7–98.9%, reported in Section 2.5 but not in the Abstract.',
  ['We have withdrawn independent external-validation claims and the previous hospital and benign-proxy '
   'performance summaries. Table 7 now covers all 47 hospital source rows within the 17-gene scope, '
   'resolving to 31 distinct missense variants. All were scored with the frozen deployment model: 22 '
   'overlap the anchor set, eight the application catalogue, and one the wider source training archive '
   'only. Record origin is shown for every variant; anchor-overlapping scores are in-sample. Repeated '
   'records and the CHEK2 Ile200Thr/Ile157Thr and Gly210Arg/Gly167Arg aliases were collapsed. All 122 '
   'source rows, including the 75 outside the gene scope, are accounted for in the accompanying audit. '
   'Clinical reference labels remain unadjudicated, so these illustrations are not an independent '
   'clinical test set.',
   'Frequency-based selection of benign candidates is not independent of frequency-informed predictors. '
   'Our gnomAD audit found 50 candidates: 47 overlapped the full training archive and one additional '
   'candidate overlapped the unresolved archive. The two remaining candidates were missense on '
   'alternative transcripts but lacked complete aligned model inputs; neither was scored. These '
   'eligibility findings are reported briefly in Results 2.5, with the full records in Supplementary '
   'Figure S1 and the release.',
   'A carefully verified single-class sample can describe the proportion receiving a specified output '
   'within that class. The present source-selected arms cannot establish overall accuracy, predictive '
   'values or clinical utility in the intended population. Requiring both classes to come from one '
   'database would not resolve selection bias or upstream training overlap. We therefore report neither '
   'a pooled external confusion matrix nor an external performance estimate.'],
  'Results 2.5; Table 7; Discussion; Methods 4.8; Supplementary Figure S1; audit/gnomAD_candidates.csv; '
  'audit/hospital_all_rows_audit.csv; tables/hospital_all_in_scope.csv; '
  'audit/hospital_full_verification.json.'),
 ('4. Predictor training overlap and reference-label incorporation',
  'Circularity is not addressed and now underwrites an external claim. Two distinct mechanisms operate. '
  'Several retained predictors — ClinPred at consensus rank 2, BayesDel addAF at rank 1 and MetaLR at '
  'rank 20 — are trained wholly or partly on ClinVar-derived labels. More fundamentally, ACMG/AMP '
  'submitters routinely invoke PP3 or BP4, which is computed from in silico predictors of exactly the '
  'kind constituting the 25-predictor panel, so the anchor labels are partly downstream of the features '
  'and no external sampling can remove the dependence. The 97.51% concordance is consequently a measure '
  "of agreement with ClinVar obtained using features that helped produce ClinVar's classifications; it "
  'is a consistency statistic rather than an accuracy statistic. The Discussion concedes residual '
  'circularity in one sentence, which is no longer sufficient now that Section 2.5 rests an '
  'external-validity claim upon it.',
  ['We agree and distinguish the two mechanisms explicitly. Several candidate or retained '
   'meta-predictors may overlap clinical-label resources used in the anchor archive. Separately, the '
   'source classifications can themselves incorporate computational evidence through PP3/BP4. The '
   'source materials do not identify the evidence contribution for each label, so neither mechanism can '
   'be quantified or removed by anchor-overlap screening alone.',
   'All internal metrics, including AUROC, binary sensitivity/specificity and unanimous-direction '
   'concordance, are now interpreted against processed source labels. S_MAC is not described as a '
   'clinical posterior probability. We refitted the first-repeat analysis after excluding '
   'BayesDel_addAF_rankscore and am_pathogenicity in addition to Reliability_index: AUROC was 0.9896 '
   'versus 0.9886 in the primary first repeat. This is a limited ablation result. Other clinically '
   'trained or frequency-informed predictors remain, so preserved discrimination does not demonstrate '
   'independence or resolution of circularity.',
   'The new deployment panel differs from the earlier fit: it does not retain BayesDel addAF or '
   'ClinPred, but it does retain AlphaMissense and several meta-predictors. We therefore report the '
   'actual new panel and refrain from treating the earlier rank ordering as a result of this '
   'reanalysis. Independent functional, segregation or case–control evidence and documented upstream '
   'overlap would be needed for a stronger reference standard.'],
  'Abstract; Results 2.1, 2.4 and 2.7; first new limitations paragraph in Discussion; Methods 4.7 and '
  '4.9; Tables 3 and 6; models/without_addAF_AlphaMissense_f*.joblib.'),
 ('5. Ascertainment and development-to-application shift',
  'The development and application populations differ systematically, and the manuscript reports the '
  'evidence without connecting it. Section 2.7 records absolute standardised mean differences of at '
  'least 0.20 for 17 of 25 final predictors between anchors and the application catalogue, mostly '
  'negative. Section 2.3 reports 12.09% of unresolved records in Uncertain-mid against 5.14% of anchors '
  'receiving an Uncertain output, a 2.35-fold difference. These are two signatures of one fact: a '
  'ClinVar variant reaches a definite classification partly because the computational evidence was '
  'decisive, so the model is developed where the features agree with the labels and deployed on the '
  'complement of that set. The internal estimates are therefore optimistic specifically for the '
  'intended use, by an amount the data cannot quantify.',
  ['We agree that these findings must be interpreted together. In the new deployment panel, 19/25 '
   'predictors have absolute standardised mean differences of at least 0.20, and 24/25 shift '
   'negatively. Among evaluable records, mixed votes occur in 78/2,046 anchors (3.81%) and 4,491/43,679 '
   'unresolved records (10.28%), a 2.70-fold difference. The 114 incomplete anchors are shown '
   'separately, so missing annotation is not conflated with model disagreement in this comparison.',
   'The Discussion connects both findings to plausible ascertainment through the availability of '
   'decisive evidence. It describes this explanation as compatible with the observed shift rather than '
   'proven by it. Internal consistency may be optimistic for the intended application, but its error in '
   'the application population cannot be quantified from these data; no internal metric is assigned to '
   'the unresolved catalogue. Ancestry-specific error or fairness cannot be assessed from the available '
   'variant-level source data.'],
  'Results 2.3 and 2.7; Discussion; Methods 4.8; Figure 7; tables/feature_shift.csv.'),
 ('6. Gene identity and pooled holdout results',
  'Gene identity is an uncontrolled confounder. Table 1 shows LP/P prevalence ranging from 10% in NBN '
  'and 11% in BARD1 to 91% in PTEN and 83% in STK11. Several retained features — bStatistic, GERP++, '
  'phyloP and phastCons — are gene- or region-level rather than variant-level, so gene identity is '
  'partially recoverable from the feature vector and carries most of the label signal in the extreme '
  'genes. The held-out-gene analysis is the correct instrument but is reported only pooled, as a single '
  'AUROC of 0.9787; per-gene results are required before any aggregate figure can be interpreted. The '
  'two external arms compound this, being drawn from opposite ends of the same gradient: the hospital '
  'LP/P variants sit in BRCA1, TP53 and BRCA2, while 15 of the 50 benign proxies are FANCA.',
  ['We performed 17 complete leave-one-gene-out fits, excluding the held-out gene from preprocessing, '
   'feature selection, tuning, calibration and threshold development. The pooled AUROC is 0.9812 on '
   '2,045 evaluable records, but Figure 4 and the distributed per-gene table give all gene-specific '
   'denominators, confusion counts, exact V-state counts, sensitivity, specificity, AUROC and '
   'evaluability.',
   'FANCA sensitivity is 50/75 (66.7%) among evaluable LP/P anchors; NBN sensitivity is 0/2, with wide '
   'uncertainty. PTEN specificity of 5/5 rests on only five evaluable benign anchors, while 17 benign '
   'anchors are incomplete. These examples are discussed in the main Results rather than hidden in a '
   'pooled estimate.',
   'An auxiliary first-repeat out-of-fold classifier recovered gene identity from training-selected '
   'predictor panels with 89.40% accuracy, compared with a majority-gene baseline of 26.11%. A separate '
   'training-fold gene-prevalence-only classifier gave source-label AUROC 0.7553. These diagnostics '
   'establish substantial gene information and label imbalance, while not proving that a specific '
   'fraction of model performance is caused by confounding. The previous external arms are no longer '
   'used to claim generalisability across genes.'],
  'Results 2.5 and 2.7; Discussion; Methods 4.7; Figures 4 and 7; tables/per_gene_held_out.csv; '
  'outputs/logo_predictions.csv; outputs/gene_recoverability_oof.csv.'),
 ('7. Opposite-direction asymmetry and clinical cost',
  'The error asymmetry runs against clinical cost. In Table 5, 34 of 973 LP/P anchors (3.49%) receive a '
  'predicted B/LB output, against 17 of 1,187 B/LB anchors (1.43%) receiving a predicted LP/P output. '
  'False-benign directional calls are 2.4 times more frequent than false-pathogenic ones, which inverts '
  'the cost ordering in cancer predisposition, and the output is labelled predicted B/LB rather than '
  'given a neutral low-priority tag. This appears only as a table cell and is not discussed.',
  ['We agree. The new first-repeat audit records 32/973 LP/P anchors at V0 (3.29%; Wilson interval '
   '2.34–4.61%) and 16/1,187 B/LB anchors at V4 (1.35%; 0.83–2.18%), a 2.44-fold rate ratio using all '
   'source-label denominators. Incomplete counts are provided alongside these rates. The Abstract now '
   'explicitly mentions the 32 LP/P anchors at V0.',
   'The Discussion addresses the risk of deprioritising a pathogenic variant and states that V0 must '
   'not be used to exclude a variant from expert review or provide clinical reassurance. Output '
   'renaming does not correct the underlying errors. The balanced-accuracy objective assigns equal '
   'class costs and has not been justified for cancer-predisposition decisions. We do not '
   'retrospectively choose a lower threshold after seeing the errors and present that as a validated '
   'solution; a clinically cost-sensitive operating point requires independent development and '
   'evaluation.'],
  'Abstract; Results 2.2; dedicated Discussion paragraph; Methods 4.9; Table 5; Shiny interpretation '
  'text.'),
 ('8. Reproducibility artifacts, persistent deposition and TRIPOD+AI',
  'The paper is not publishable without deposition of the 25-predictor feature matrix. The processed '
  'matrix for the 2,160 anchors, with gene labels, fold assignments and out-of-fold predictions, is the '
  'minimum artifact required to verify the held-out-gene analysis, to obtain per-gene performance, to '
  'test whether gene identity is recoverable from the feature vector and to isolate the contribution of '
  'individual predictors such as Reliability_index. None of these can be checked by any reader from '
  'what is presented. The Code Availability statement defers deposition until after publication, which '
  'is not a reproducibility standard and is incompatible with the TRIPOD+AI adherence the manuscript '
  'claims. Deposition in a persistent, DOI-bearing repository, together with the frozen model objects '
  'and the scripts that regenerate the reported tables, is a precondition for publication in any form '
  'and must precede a further round of review rather than follow acceptance. Section 4.8 shows '
  'concretely why: the UniProt localisation analysis was removed because the row-level table required '
  'to recompute it was not available in the supplied revision package, so the authors were themselves '
  'unable to regenerate their own analysis from their own materials.',
  ['The missing original fitted objects prevented verification of the earlier estimates. We therefore '
   'refitted the models and saved the full analysis. The earlier matrix is retained as a labelled '
   'legacy reference; current results derive from the R4 matrices, models and predictions.',
   'The accompanying release contains the 2,160-anchor numeric matrix, the 25-predictor deployment '
   'matrix, gene and source labels, outer and inner fold memberships, row-level predictions, 17 '
   'gene-held-out fits, 15 sensitivity fits and the deployment fit. All 58 fitted objects are present '
   'and nonempty. We reran prediction replay from the delivered archive: all saved assessment outputs '
   'and 43,679 application outputs agreed within a maximum absolute probability difference of 1.11 × '
   '10⁻¹⁶. Scripts regenerate the tables and eight figures. The unreproducible UniProt analysis remains '
   'removed.',
   'Persistent DOI deposition and verified reviewer access are still outstanding. This requirement '
   'remains open and must be completed before resubmission. The TRIPOD+AI reporting map identifies the '
   'available evidence and remaining gaps; we no longer claim complete adherence.'],
  'Data and Code Availability; Supplementary reporting map; README.md; audit/model_verification.json; '
  'data/; models/; outputs/; scripts/; documentation/.'),
 ('9. Software version, Reliability_index and transductive selection',
  'Further items. Section 4.9 cites Rstudio 4.13, which is not a version of either R or RStudio. '
  'Carried over unaddressed from the original submission: Reliability_index remains the 25th predictor '
  'although it is annotation-quality metadata correlated with ascertainment intensity, and the '
  'greater-than-40% missingness filter is still applied using the unlabelled application archive before '
  'resampling, which is transductive feature selection and is not identified as such.',
  ['We corrected the software record to the environment actually used: Python 3.12.13, NumPy 2.3.5, '
   'pandas 2.2.3 and scikit-learn 1.8.0, with exact auxiliary package versions in the release. No '
   'reanalysed result is attributed to an unverified R or RStudio version. The revised Shiny viewer '
   'passed R runtime and local HTTP checks in this environment. Browser interaction and public '
   'redeployment remain unverified.',
   'Reliability_index is excluded from the primary candidate set and from all primary inner and outer '
   'feature selection. A paired inclusion sensitivity yielded AUROC 0.9891 and balanced accuracy 0.9614 '
   'versus 0.9886 and 0.9592 in the primary first repeat. The primary exclusion reflects its metadata '
   'role and is not justified by claiming a statistically proven absence of contribution.',
   'The earlier application-based missingness screen is explicitly acknowledged as transductive and has '
   'been removed from the new analysis. We reconstructed the numeric matrix before that screen; the '
   'primary semantic candidate set has 47 predictors. The >40% missingness filter, constant-feature '
   'exclusion, median imputation, scaling, supervised ranking and correlation pruning are fitted '
   'independently in each inner-training partition and again in outer training. The unresolved archive '
   'does not determine the candidate set or fitted parameters. We also corrected the previous claim of '
   'nine-learner family selection to the four-family design actually evaluated in this revision.'],
  'Methods 4.3–4.5 and 4.9; Results 2.1 and 2.4; Tables 2–4 and 6; scripts/prepare_inputs.py; '
  'scripts/hbocpred_core.py; audit/environment.json.')]

ADDITIONAL = ['We also checked annotation completeness and transcript identity. In each repeated assessment, 114 '
 'anchors receive no output under the same ≥20/25 observed-predictor rule used for application. All 101 '
 'NR-status anchors are incomplete, including all 23 NR LP/P anchors. The previous “22/23 versus 5/23” '
 'learner comparison depended on imputed inputs and has been withdrawn from the Results, Figure 6 and '
 'Discussion.',
 'Current annotation identifies 2,039 MANE missense anchors and 81 additional same-gene '
 'alternative-transcript missense anchors; 40 lack a current same-gene missense consequence. The '
 '2,120-record sensitivity analysis was refitted separately. These current annotations do not establish '
 'the missing historical transcript assignments.',
 'The source manuscript’s 35 reference entries, 26 Mendeley citation fields and one bibliography field '
 'are preserved, together with the Introduction literature paragraphs and the main '
 'literature-comparison Discussion paragraph. Supplementary Materials are retained consistently and '
 'supplied with the manuscript.']
