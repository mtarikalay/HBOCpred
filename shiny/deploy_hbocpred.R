# Open this file from the extracted shiny folder in RStudio.
# Run: source('deploy_hbocpred.R'); deploy_hbocpred()
# Uses your existing rsconnect account; no credentials belong in this file.
.hboc_script <- tryCatch(normalizePath(sys.frame(1)$ofile,mustWork=TRUE),error=function(e) NA_character_)
.hboc_default <- if(!is.na(.hboc_script)) dirname(.hboc_script) else getwd()
hboc_preflight <- function(app_dir=.hboc_default) {
 if(getRversion()<"4.1") stop("R 4.1 or newer is required.")
 app_dir <- normalizePath(app_dir,mustWork=TRUE)
 required_packages <- c('shiny','DT','jsonlite','rsconnect')
 missing <- required_packages[!vapply(required_packages,requireNamespace,logical(1),quietly=TRUE)]
 if(length(missing)) stop('Install these packages first: ',paste(missing,collapse=', '),'. Use install.packages(c("shiny","DT","jsonlite","rsconnect"))')
 paths <- c('app.R','R/catalogue.R','www/app.css','data/release.json','data/summary.json','data/per_gene_held_out.csv','data/application_catalogue.csv.gz')
 stopifnot(all(file.exists(file.path(app_dir,paths))))
 meta <- jsonlite::read_json(file.path(app_dir,'data/release.json'),simplifyVector=TRUE)
 stopifnot(unname(tools::md5sum(file.path(app_dir,'data/application_catalogue.csv.gz')))==meta$catalogue_md5)
 old <- setwd(app_dir);on.exit(setwd(old),add=TRUE)
 e <- new.env(parent=globalenv());app <- source('app.R',local=e)$value
 stopifnot(inherits(app,'shiny.appobj'),nrow(e$atlas)==43679L)
 files <- c('app.R',list.files('R',recursive=TRUE,full.names=TRUE),list.files('www',recursive=TRUE,full.names=TRUE),list.files('data',recursive=TRUE,full.names=TRUE))
 message('Ready: Viewer ',meta$viewer_release,' / analysis ',meta$analysis_release,'; 43,679 records; ',length(files),' application files.')
 invisible(list(app_dir=app_dir,files=files,release=meta))
}
deploy_hbocpred <- function(app_dir=.hboc_default,check_only=FALSE,app_name='HBOCpred_Shiny_R4_4') {
 ready <- hboc_preflight(app_dir)
 if(isTRUE(check_only)) return(invisible(ready))
 accounts <- rsconnect::accounts()
 if(!any(accounts$name=='alaymd' & accounts$server=='shinyapps.io')) {
  stop('The alaymd account is not configured in this R session. In your own RStudio, open Tools > Global Options > Publishing > Connect > ShinyApps.io and connect the existing alaymd account. Then run deploy_hbocpred() again. Do not paste tokens or passwords into chat.')
 }
 apps <- rsconnect::applications(account='alaymd',server='shinyapps.io')
 if(!app_name %in% c('hbocpred','HBOCpred_Shiny_R4_4')) stop('Choose hbocpred or HBOCpred_Shiny_R4_4.')
 target <- apps[apps$name==app_name,,drop=FALSE]
 if(nrow(target)!=1L) stop('Expected exactly one existing ',app_name,' application on alaymd.')
 app_id <- as.character(target$id[[1]])
 if(app_name=='HBOCpred_Shiny_R4_4' && app_id!='17838814') stop('The registered R4.4 application ID does not match 17838814.')
 message('Updating alaymd/',app_name,' (ID ',app_id,').')
 rsconnect::deployApp(appDir=ready$app_dir,appFiles=ready$files,appId=app_id,appName=app_name,
  account='alaymd',server='shinyapps.io',appTitle='HBOCpred Variant Score Atlas',
  appMode='shiny',launch.browser=TRUE,logLevel='normal',lint=TRUE)
 message('Deployment command finished. Verify only Variant explorer and Model audit tabs are shown, with counts 43,679 / 33,414 / 4,491 / 5,774. The About this release tab and version badge have been removed.')
 invisible(app_id)
}
message('Loaded. Run deploy_hbocpred(check_only=TRUE) to verify locally, or deploy_hbocpred() to update alaymd/HBOCpred_Shiny_R4_4 (ID 17838814).')
