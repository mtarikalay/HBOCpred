library(shiny)
library(DT)
source(file.path('R','catalogue.R'),local=TRUE)
atlas <- load_catalogue(file.path('data','application_catalogue.csv.gz'))
release <- jsonlite::read_json(file.path('data','release.json'),simplifyVector=TRUE)
summary_data <- jsonlite::read_json(file.path('data','summary.json'),simplifyVector=TRUE)
gene_audit <- read.csv(file.path('data','per_gene_held_out.csv'),check.names=FALSE)
genes <- sort(unique(atlas$Gene))
stopifnot(identical(unname(as.integer(state_counts(atlas))),c(33414L,4491L,5774L,0L)),unname(tools::md5sum(file.path('data','application_catalogue.csv.gz')))==release$catalogue_md5)
stat_card <- function(label,value,helper=NULL,colour='') div(class=paste('metric-card',colour),div(class='metric-value',value),div(class='metric-label',label),div(class='metric-note',helper))
figure_choices <- c('Internal performance'='Figure2_performance.png','Vote states and model pairs'='Figure3_vstates.png','Per-gene holdouts'='Figure4_per_gene.png','Constituent-score comparisons'='Figure5_comparators.png','Review-status accounting'='Figure6_review_status.png','Distribution shift and gene signal'='Figure7_shift_gene_signal.png','gnomAD candidate eligibility'='FigureS1_gnomAD_eligibility.png','Analysis workflow'='Figure1_workflow.png')
ui <- fluidPage(
 tags$head(tags$title('HBOCpred | Variant Score Atlas'),tags$meta(name='hbocpred-viewer-release',content=release$viewer_release),tags$style(HTML(paste(readLines(file.path('www','app.css'),warn=FALSE),collapse='\n')))),
 div(class='app-shell',
  div(class='app-header',
   div(class='brand-block',div(class='brand-line',h1('HBOCpred'),span('Variant Score Atlas')),p('Search by gene, HGVS, transcript, SPDI or rsID.')),
   div(class='research-note','Research use only. Vote states describe model direction, not ACMG/AMP classification. V0 does not establish benignity; S_MAC is a ranking score.')),
  tabsetPanel(id='main_tab',
   tabPanel('Variant explorer',value='catalogue',
    div(class='summary-grid',stat_card('Displayed',textOutput('n'),'Variants matching the filters'),stat_card('V0',textOutput('v0'),'Unanimous B/LB-directed'),stat_card('V1–V3',textOutput('mixed'),'Mixed votes'),stat_card('V4',textOutput('v4'),'Unanimous LP/P-directed')),
    div(class='filter-panel',
     div(class='filter-heading',div(h2('Variant explorer'),p('Filter the catalogue, select a row and inspect its scores on the right.')),div(class='filter-actions',actionButton('reset','Reset filters'),downloadButton('download','Download filtered CSV',class='btn-download'))),
     div(class='filter-grid',
      div(class='filter-item',textInput('query','Gene, HGVS or identifier',placeholder='SPDI, HGVS, transcript or rsID')),
      div(class='filter-item',selectInput('gene','Gene',c('All',genes),selectize=FALSE)),
      div(class='filter-item',selectInput('state','Vote state',c('All',paste0('V',0:4),'Incomplete'),selectize=FALSE)),
      div(class='filter-item',selectInput('direction','Model direction',c('All','Unanimous B/LB-directed','Mixed votes','Unanimous LP/P-directed'),selectize=FALSE)),
      div(class='filter-item',checkboxInput('rank','Highest S_MAC first',FALSE)))),
    div(class='workspace-grid',
     div(class='panel-card results-panel',h3('Search results'),uiOutput('empty_note'),DTOutput('table'),p(class='small-note muted','GRCh38 · 17 genes · 43,679 catalogue variants. Select a row to inspect its four learner votes.')),
     div(class='detail-column',div(class='detail-card',h3('Selected variant'),uiOutput('details'),conditionalPanel(condition='input.table_rows_selected && input.table_rows_selected.length === 1',plotOutput('learner_plot',height='285px'),p(class='small-note muted','Diamonds mark fitted learner thresholds.')))))
   ),
   tabPanel('Model audit',value='audit',
    div(class='interpretation','These are internal source-label estimates. They do not establish clinical accuracy for the unresolved catalogue.'),
    div(class='stat-grid',stat_card('Nested CV AUROC',sprintf('%.4f',summary_data$performance$AUROC$mean),'S_MAC; five-repeat mean'),stat_card('Balanced accuracy',sprintf('%.4f',summary_data$performance$balanced_accuracy$mean),'≥3-of-4 secondary endpoint'),stat_card('Evaluable anchors','2,046 / 2,160','114 incomplete in each repeat','stat-grey'),stat_card('Gene holdout AUROC',sprintf('%.4f',summary_data$logo$AUROC),'2,045 evaluable; 17 whole-gene holdouts')),
    div(class='panel-card',h3('Performance by held-out gene'),p('Each gene was excluded from the corresponding model’s training. Intervals are Wilson 95% intervals conditional on the evaluated source records.'),selectInput('audit_gene','Inspect gene',c('All',genes),selectize=FALSE),DTOutput('gene_table'),downloadButton('download_audit','Download per-gene results'),p(class='small-note muted','Small denominators and incomplete records matter. Pooled performance should not be assumed to apply uniformly to every gene.')),
    div(class='panel-card',h3('Figures from the revised analysis'),selectInput('figure','Figure',figure_choices,selectize=FALSE),uiOutput('figure_note'),div(class='figure-wrap',uiOutput('figure_display')))
   )
  ),div(class='footer-note','HBOCpred · Variant Score Atlas')
 ))
server <- function(input,output,session) {
 filtered <- reactive(filter_catalogue(atlas,input$gene,input$state,input$direction,input$query,input$rank))
 count <- reactive(state_counts(filtered()))
 output$n <- renderText(format(nrow(filtered()),big.mark=',',trim=TRUE))
 output$v0 <- renderText(format(count()[['V0']],big.mark=',',trim=TRUE))
 output$mixed <- renderText(format(count()[['Mixed']],big.mark=',',trim=TRUE))
 output$v4 <- renderText(format(count()[['V4']],big.mark=',',trim=TRUE))
 observeEvent(input$reset,{
  updateSelectInput(session,'gene',selected='All');updateSelectInput(session,'state',selected='All');updateSelectInput(session,'direction',selected='All');updateTextInput(session,'query',value='');updateCheckboxInput(session,'rank',value=FALSE)
 })
 selected_id <- reactiveVal(NULL)
 observeEvent(filtered(),{selected_id(NULL)},ignoreInit=FALSE,priority=100)
 observeEvent(input$table_rows_selected,{
  i <- input$table_rows_selected
  if(length(i)==1L && i>=1L && i<=nrow(filtered())) selected_id(filtered()$SPDI[[i]]) else selected_id(NULL)
 },ignoreNULL=FALSE)
 selected <- reactive({id <- selected_id();if(is.null(id)) return(NULL);x <- filtered();x <- x[x$SPDI==id,,drop=FALSE];if(nrow(x)==1L) x else NULL})
 output$empty_note <- renderUI({if(!nrow(filtered())) p(class='interpretation','No records match these filters. No prediction has been generated. Try resetting the filters or checking the identifier.')})
 output$table <- renderDT({
  cols <- c('Gene','SPDI','HGVSc','HGVSp','audit_state','vote_vector','S_MAC','n_observed_panel');x <- filtered()[,cols,drop=FALSE]
  names(x) <- c('Gene','SPDI','Transcript HGVS','Protein HGVS','State','Votes','S_MAC','Observed / 25')
  datatable(x,rownames=FALSE,selection='single',escape=TRUE,options=list(pageLength=10,lengthMenu=c(10,25,50),scrollX=TRUE,dom='ltip',searching=FALSE,order=list(),deferRender=TRUE)) |> formatRound('S_MAC',digits=4)
 },server=TRUE)
 output$details <- renderUI({
  x <- selected();if(is.null(x)) return(p(class='muted','Select a catalogue row to inspect its model votes.'))
  field <- function(label,value) tags$div(tags$dt(label),tags$dd(ifelse(is.na(value)|!nzchar(as.character(value)),'Not recorded',as.character(value))))
  tagList(div(class='variant-id',paste(x$Gene,x$SPDI,sep=' · ')),tags$dl(class='detail-grid',field('Transcript HGVS',x$HGVSc),field('Protein HGVS',x$HGVSp),field('Model descriptor',x$directional_descriptor),field('State',x$audit_state),field('Four-bit vote vector',x$vote_vector),field('S_MAC',sprintf('%.6f',x$S_MAC)),field('Observed predictors',paste0(x$n_observed_panel,' / ',x$panel_size)),field('Source clinical annotation',x$CLIN_SIG)))
 })
 output$learner_plot <- renderPlot({
  x <- selected();req(!is.null(x));validate(need(x$complete_flag==1L,'Incomplete annotations: outputs suppressed.'))
  p <- unlist(x[,paste0('p_',names(learner_names)),drop=FALSE],use.names=FALSE);v <- unlist(x[,paste0('vote_',names(learner_names)),drop=FALSE],use.names=FALSE);thresholds <- unlist(release$learner_thresholds[names(learner_names)],use.names=FALSE)
  par(mar=c(4,4.5,1.6,1),family='sans');bars <- barplot(p,names.arg=unname(learner_names),ylim=c(0,1.13),col=ifelse(v==1,'#ad5058','#245f95'),border=NA,ylab='Calibrated source-direction score',cex.names=.9)
  points(bars,thresholds,pch=23,bg='white',col='#243744',cex=1.4);text(bars,p,labels=paste0(sprintf('%.3f',p),' · vote ',v),pos=3,cex=.85)
 })
 output$download <- downloadHandler(filename=function()paste0('HBOCpred_R4_filtered_',Sys.Date(),'.csv'),content=function(file)write_catalogue(filtered(),file))
 gene_subset <- reactive({if(is.null(input$audit_gene)||input$audit_gene=='All') gene_audit else gene_audit[gene_audit$Gene==input$audit_gene,,drop=FALSE]})
 output$gene_table <- renderDT({
  x <- gene_subset();d <- data.frame(Gene=x$Gene,Source=x$n_total,Evaluable=x$n_evaluable,Incomplete=x$n_total-x$n_evaluable,
   `LP/P: correct/evaluable`=paste0(x$TP,'/',x$TP+x$FN),`Sensitivity (95% interval)`=sprintf('%.1f%% (%.1f–%.1f)',100*x$sensitivity,100*x$sensitivity_lo,100*x$sensitivity_hi),
   `B/LB: correct/evaluable`=paste0(x$TN,'/',x$TN+x$FP),`Specificity (95% interval)`=sprintf('%.1f%% (%.1f–%.1f)',100*x$specificity,100*x$specificity_lo,100*x$specificity_hi),AUROC=round(x$AUROC,4),check.names=FALSE)
  datatable(d,rownames=FALSE,options=list(pageLength=17,paging=FALSE,searching=FALSE,scrollX=TRUE,dom='t'))
 })
 output$download_audit <- downloadHandler(filename=function()'HBOCpred_R4_gene_holdout.csv',content=function(file)write_catalogue(gene_subset(),file))
 output$figure_display <- renderUI({req(input$figure %in% unname(figure_choices));tags$img(src=input$figure,alt=names(figure_choices)[match(input$figure,figure_choices)])})
 output$figure_note <- renderUI({if(identical(input$figure,'FigureS1_gnomAD_eligibility.png')) p(class='interpretation','Candidate eligibility and archive overlap only. The two candidates outside both archives were not scored; this figure does not report external validation.') else p(class='small-note muted','Figure regenerated from the distributed R4 data and fitted-model outputs. Performance figures describe internal source-label consistency.')})
}
shinyApp(ui,server)
