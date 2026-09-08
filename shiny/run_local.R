# source('run_local.R') from the extracted shiny folder in RStudio.
if(!requireNamespace('shiny',quietly=TRUE)) stop('Install shiny, DT and jsonlite first.')
app_file <- tryCatch(normalizePath(sys.frame(1)$ofile,mustWork=TRUE),error=function(e) NA_character_)
app_dir <- if(!is.na(app_file)) dirname(app_file) else getwd()
shiny::runApp(app_dir,launch.browser=TRUE)
