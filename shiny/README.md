# HBOCpred Shiny viewer

[Online viewer](https://alaymd.shinyapps.io/hbocpred/)

The revised catalogue contains **43,679 variants; 33,414 V0; 4,491 mixed; 5,774 V4**.

Open `HBOCpred.Rproj` in RStudio:

```r
install.packages(c("shiny", "DT", "jsonlite", "rsconnect"), repos = "https://cloud.r-project.org")
source("run_local.R")
```

To publish, stop the local app and use the RStudio session connected to the `alaymd` account:

```r
source("deploy_hbocpred.R")
deploy_hbocpred()
```

The default target is the existing `hbocpred` application. Confirm the four counts above after deployment.
