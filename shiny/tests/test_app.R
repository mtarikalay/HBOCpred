# Run from the shiny directory: Rscript tests/test_app.R
suppressPackageStartupMessages(library(testthat))
suppressPackageStartupMessages(library(shiny))
app <- source('app.R')$value
results <- list()
check <- function(name,code) {force(code);results[[name]] <<- 'PASS';cat('PASS:',name,'\n')}
check('Frozen catalogue counts and exact four-bit vectors', {
 stopifnot(nrow(atlas)==43679L,all(nchar(atlas$vote_vector)==4),sum(atlas$vote_vector=='0000')==33414L)
 stopifnot(identical(unname(as.integer(state_counts(atlas))),c(33414L,4491L,5774L,0L)))
})
check('Every saved vote agrees with its fitted threshold', {
 for(k in names(learner_names)) stopifnot(all(as.integer(atlas[[paste0('p_',k)]]>=release$learner_thresholds[[k]])==atlas[[paste0('vote_',k)]]))
})
check('Combined gene/state filters and literal identifier search', {
 expected <- atlas[atlas$Gene=='BRCA1' & atlas$V==4,,drop=FALSE]
 actual <- filter_catalogue(atlas,gene='BRCA1',state='V4')
 stopifnot(nrow(actual)>0,identical(actual$SPDI,expected$SPDI))
 one <- filter_catalogue(atlas,query=atlas$SPDI[[1]])
 stopifnot(nrow(one)==1L,one$SPDI==atlas$SPDI[[1]])
 stopifnot(nrow(filter_catalogue(atlas,query='NO_SUCH_VARIANT_LITERAL_TEST'))==0L)
})
check('Ranking and CSV export preserve the complete selected row set', {
 x <- filter_catalogue(atlas,gene='BRCA2',direction='Mixed votes',rank=TRUE)
 stopifnot(nrow(x)>0,all(diff(x$S_MAC)<=0))
 dest <- tempfile(fileext='.csv');write_catalogue(x,dest)
 back <- read.csv(dest,check.names=FALSE,colClasses=c(vote_vector='character'))
 stopifnot(identical(back$SPDI,x$SPDI),identical(back$vote_vector,x$vote_vector),nrow(back)==nrow(x))
})
check('Incomplete-input guard suppresses all model output fields', {
 # Synthetic input is restricted to this guard test and never enters research results.
 x <- atlas[1:2,,drop=FALSE];x$complete_flag[[1]] <- 0L;x$n_observed_panel[[1]] <- 1L
 x <- prepare_catalogue(x)
 cols <- grep('^(p_|vote_)|^(V|Mean4|S_MAC|directional_descriptor)$',names(x),value=TRUE)
 stopifnot(all(is.na(x[1,cols])),x$audit_state[[1]]=='Incomplete',x$vote_vector[[2]]==atlas$vote_vector[[2]])
})
check('Gene audit retains all 17 denominators and incomplete accounting', {
 stopifnot(nrow(gene_audit)==17L,sum(gene_audit$n_total)==2160L,sum(gene_audit$n_evaluable)==2045L)
 x <- subset(gene_audit,Gene=='PTEN');stopifnot(x$TN+x$FP==5L,x$n_B==22L)
 x <- subset(gene_audit,Gene=='NBN');stopifnot(x$TP==0L,x$FN==2L)
})
check('Shiny server: rendered counters, selection, filter reset and per-gene output', {
 shiny::testServer(server, {
  session$setInputs(gene='All',state='All',direction='All',query='',rank=FALSE,audit_gene='All',figure='Figure2_performance.png')
  stopifnot(output$n=='43,679',output$v0=='33,414',output$mixed=='4,491',output$v4=='5,774')
  session$setInputs(table_rows_selected=1L)
  stopifnot(selected()$SPDI==atlas$SPDI[[1]])
  stopifnot(grepl(atlas$SPDI[[1]],output$details$html,fixed=TRUE))
  plot_result <- output$learner_plot
  stopifnot(!is.null(plot_result$src))
  session$setInputs(gene='BRCA1',state='V4')
  stopifnot(is.null(selected()),nrow(filtered())==sum(atlas$Gene=='BRCA1' & atlas$V==4))
  session$setInputs(query='NO_SUCH_VARIANT_LITERAL_TEST')
  stopifnot(output$n=='0',grepl('No prediction',output$empty_note$html,fixed=TRUE))
  session$setInputs(gene='All',state='All',query='',audit_gene='FANCA')
  stopifnot(nrow(gene_subset())==1L,gene_subset()$TP==50L,gene_subset()$FN==25L)
  gene_render <- output$gene_table
  stopifnot(nzchar(gene_render))
  session$setInputs(figure='FigureS1_gnomAD_eligibility.png')
  stopifnot(grepl('not scored',output$figure_note$html,fixed=TRUE))
 })
})
check('UI and figure assets are present', {
 rendered <- htmltools::renderTags(ui)
 html <- paste(rendered$head,rendered$html)
 stopifnot(grepl('Variant catalogue',html,fixed=TRUE),grepl('Model audit',html,fixed=TRUE),!grepl('About this release',html,fixed=TRUE),!grepl('release-badge',html,fixed=TRUE),grepl('hbocpred-viewer-release',html,fixed=TRUE),all(file.exists(file.path('www',unname(figure_choices)))))
})
report <- list(status='PASS',viewer_release=release$viewer_release,analysis_release=release$analysis_release,checked_at=format(Sys.time(),tz='UTC',usetz=TRUE),R=R.version.string,packages=lapply(c('shiny','DT','rsconnect','testthat'),function(x)list(package=x,version=as.character(packageVersion(x)))),checks=results,limitations=c('This script checks local R and Shiny server behaviour; browser checks are recorded separately.','This test script does not publish to shinyapps.io.'))
jsonlite::write_json(report,'tests/runtime_verification.json',pretty=TRUE,auto_unbox=TRUE)
cat('All runtime checks passed.\n')
