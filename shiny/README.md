# HBOCpred Shiny viewer

The navy header, horizontal filters and variant-detail panel use the revised catalogue: **43,679 variants; 33,414 V0; 4,491 mixed; 5,774 V4**.

Open `HBOCpred.Rproj` in RStudio:

```r
install.packages(c("shiny", "DT", "jsonlite", "rsconnect"), repos = "https://cloud.r-project.org")
source("run_local.R")
```

Stop the local app. From your RStudio session connected to the `alaymd` account:

```r
source("deploy_hbocpred.R")
deploy_hbocpred()
```

This deploys to **HBOCpred_Shiny_R4_4**, the existing application with ID **17838814**:
https://alaymd.shinyapps.io/HBOCpred_Shiny_R4_4/

To update the established `hbocpred` address instead, explicitly use:

```r
deploy_hbocpred(app_name = "hbocpred")
```

The source is ready for deployment; publishing requires the connected rsconnect account. Confirm the four counts above after deployment. Source annotations and all model outputs are included in the CSV. Predictor matrices are supplied separately in the repository.
