.PHONY: replay tables figures train
replay:
	python scripts/verify_release.py
	python scripts/audit_source_snapshots.py
tables:
	python scripts/summarise_results.py
	python scripts/conditional_intervals.py
figures:
	python scripts/make_figures.py
train:
	python scripts/run_analysis.py --jobs 6
