# A real renderPlot result from the Shiny R server, not a browser screenshot.
suppressPackageStartupMessages(library(shiny))
source('app.R')
dir.create('tests/evidence',showWarnings=FALSE)
shiny::testServer(server,{
 session$setInputs(gene='All',state='All',direction='All',query='',rank=FALSE,audit_gene='All',figure='Figure4_per_gene.png')
 i <- which(atlas$Gene=='BRCA1' & atlas$V==2)[[1]]
 session$setInputs(table_rows_selected=i)
 p <- output$learner_plot
 stopifnot(startsWith(p$src,'data:image/png;base64,'))
 writeBin(jsonlite::base64_dec(sub('^data:image/png;base64,','',p$src)),'tests/evidence/Shiny_R4_1_BRCA1_model_votes.png')
 jsonlite::write_json(list(type='Actual Shiny renderPlot output from testServer; not a live-site screenshot',SPDI=selected()$SPDI,Gene=selected()$Gene,HGVSc=selected()$HGVSc,HGVSp=selected()$HGVSp,vote_vector=selected()$vote_vector,S_MAC=selected()$S_MAC,rendered_counts=list(total=output$n,V0=output$v0,mixed=output$mixed,V4=output$v4)),'tests/evidence/server_example.json',pretty=TRUE,auto_unbox=TRUE)
})
