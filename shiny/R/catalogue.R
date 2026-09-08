learner_names <- c(SVM_RBF='SVM–RBF', ENET_LR='L2 logistic', EXTRA_TREES='Extra Trees', HIST_GB='HistGB')
prepare_catalogue <- function(x, expected_n=NULL) {
 required <- c('SPDI','Gene','V','S_MAC','complete_flag','directional_descriptor','vote_vector','n_observed_panel','panel_size',paste0('p_',names(learner_names)),paste0('vote_',names(learner_names)))
 stopifnot(all(required %in% names(x)),!anyDuplicated(x$SPDI),!anyNA(x$complete_flag),all(x$complete_flag %in% 0:1))
 if (!is.null(expected_n)) stopifnot(nrow(x)==expected_n)
 valid <- x$complete_flag==1L
 stopifnot(all(x$n_observed_panel[valid]>=ceiling(.8*x$panel_size[valid])),all(x$V[valid] %in% 0:4),all(x$S_MAC[valid]>=0 & x$S_MAC[valid]<=1),all(grepl('^[01]{4}$',x$vote_vector[valid])))
 expected <- ifelse(x$V==0,'Unanimous B/LB-directed',ifelse(x$V==4,'Unanimous LP/P-directed','Mixed votes'))
 stopifnot(all(x$directional_descriptor[valid]==expected[valid]))
 votes <- x[,paste0('vote_',names(learner_names)),drop=FALSE]
 stopifnot(all(rowSums(votes[valid,,drop=FALSE])==x$V[valid]),all(apply(votes[valid,,drop=FALSE],1,paste0,collapse='')==x$vote_vector[valid]))
 suppressed <- grep('^(p_|vote_)|^(V|Mean4|S_MAC|directional_descriptor)$',names(x),value=TRUE)
 x[!valid,suppressed] <- NA
 x$audit_state <- ifelse(valid,paste0('V',x$V),'Incomplete')
 x
}
load_catalogue <- function(path,expected_n=43679L) prepare_catalogue(read.csv(gzfile(path),stringsAsFactors=FALSE,check.names=FALSE,colClasses=c(vote_vector='character')),expected_n)
filter_catalogue <- function(x,gene='All',state='All',direction='All',query='',rank=FALSE) {
 if(length(gene) && gene!='All') x <- x[x$Gene==gene,,drop=FALSE]
 if(length(state) && state!='All') x <- x[x$audit_state==state,,drop=FALSE]
 if(length(direction) && direction!='All') x <- x[!is.na(x$directional_descriptor) & x$directional_descriptor==direction,,drop=FALSE]
 if(length(query) && nzchar(trimws(query))) {
  cols <- intersect(c('Gene','SPDI','Location','HGVSc','HGVSp','Existing_variation','Feature','MANE_SELECT'),names(x));needle <- tolower(trimws(query));hits <- rep(FALSE,nrow(x))
  for(k in cols) {v <- tolower(x[[k]]);hits <- hits | (!is.na(v) & grepl(needle,v,fixed=TRUE))}
  x <- x[hits,,drop=FALSE]
 }
 if(isTRUE(rank)) x <- x[order(-x$S_MAC,x$SPDI,na.last=TRUE),,drop=FALSE]
 x
}
state_counts <- function(x) c(V0=sum(x$V==0,na.rm=TRUE),Mixed=sum(x$V %in% 1:3),V4=sum(x$V==4,na.rm=TRUE),Incomplete=sum(x$complete_flag!=1L))
write_catalogue <- function(x,file) write.csv(x,file,row.names=FALSE,na='',fileEncoding='UTF-8')
