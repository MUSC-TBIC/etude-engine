import pandas as pd

def new_score_card():
    return pd.DataFrame( columns = [ 'File' ,
                                     'Start' , 'End' ,
                                     'Type' , 'Score' ] )

##
## All functions related to printing and calculating scoring metrics
##

def accuracy( tp , fp , tn , fn ):
    if( tp + fp + tn + fn > 0 ):
        return ( tp + tn ) / float( tp + fp + tn + fn )
    else:
        return 0.0


def precision( tp , fp ):
    if( fp + tp > 0 ):
        return tp / float( fp + tp )
    else:
        return 0.0


def recall( tp , fn ):
    if( fn + tp > 0 ):
        return tp / float( fn + tp )
    else:
        return 0.0


def specificity( tn , fn ):
    if( tn + fn > 0 ):
        return tn / float( tn + fn )
    else:
        return 0.0


def f_score( p , r , beta = 1 ):
    if( p + r > 0 ):
        return ( 1 + ( beta**2 ) ) * ( p * r ) / \
            ( ( ( beta**2 ) * p ) + r )
    else:
        return 0.0


def add_missing_types( score_summary ):
    score_types = score_summary.keys()
    if( 'TP' not in score_types ):
        score_summary[ 'TP' ] = 0.0
    if( 'FP' not in score_types ):
        score_summary[ 'FP' ] = 0.0
    if( 'TN' not in score_types ):
        score_summary[ 'TN' ] = 0.0
    if( 'FN' not in score_types ):
        score_summary[ 'FN' ] = 0.0
    return score_summary


def norm_summary( score_summary , row_name , args ):
    ## Source for definitions:
    ## -- https://en.wikipedia.org/wiki/Precision_and_recall#Definition_.28classification_context.29
    ##
    ## First, we want to make sure that all score types are represented
    ## in the summary series.
    score_summary = add_missing_fields( score_summary )
    ## True Positive Rate (TPR),
    ## Sensitivity,
    ## Recall,
    ## Probability of Detection
    if( 'Recall' in args.metrics_list or
        'F1' in args.metrics_list ):
        score_summary[ 'Recall' ] = recall( tp = score_summary[ 'TP' ] ,
                                            fn = score_summary[ 'FN' ] )
    if( 'Sensitivity' in args.metrics_list ):
        score_summary[ 'Sensitivity' ] = recall( tp = score_summary[ 'TP' ] ,
                                                 fn = score_summary[ 'FN' ] )
    ## Positive Predictive Value (PPV),
    ## Precision
    if( 'Precision' in args.metrics_list or
        'F1' in args.metrics_list ):
        score_summary[ 'Precision' ] = precision( tp = score_summary[ 'TP' ] ,
                                                  fp = score_summary[ 'FP' ] )
    ## True Negative Rate (TNR),
    ## Specificity (SPC) 
    if( 'Specificity' in args.metrics_list ):
        score_summary[ 'Specificity' ] = specificity( tn = score_summary[ 'TN' ] ,
                                                      fn = score_summary[ 'FN' ] )
    ## Accuracy
    if( 'Accuracy' in args.metrics_list ):
        score_summary[ 'Accuracy' ] = accuracy( tp = score_summary[ 'TP' ] ,
                                                fp = score_summary[ 'FP' ] ,
                                                tn = score_summary[ 'TN' ] ,
                                                fn = score_summary[ 'FN' ] )
    ##
    if( 'F1' in args.metrics_list ):
        score_summary[ 'F1' ] = f_score( p = score_summary[ 'Precision' ] ,
                                         r = score_summary[ 'Recall' ] )
    ##
    metrics = [ row_name ]
    for metric in args.metrics_list:
        metrics.append( score_summary[ metric ] )
    return metrics


def print_score_summary( score_card , file_list ,
                         gold_config , test_config ,
                         args ):
    ## TODO - refactor score printing to a separate function
    ## TODO - add scores grouped by type
    print( '{}{}{}'.format( '\n#########' ,
                            args.delim ,
                            args.delim.join( '{}'.format( m ) for m in args.metrics_list ) ) )
    ##
    metrics = norm_summary( score_card[ 'Score' ].value_counts() ,
                            'aggregate' , args )
    print( args.delim.join( '{}'.format( m ) for m in metrics ) )
    ##
    if( args.by_file ):
        for filename in file_list:
            this_file = ( score_card[ 'File' ] == filename )
            metrics = norm_summary( score_card[ this_file ][ 'Score' ].value_counts() ,
                                    filename , args )
            print( args.delim.join( '{}'.format( m ) for m in metrics ) )

    if( args.by_type ):
        for pattern in gold_config:
            this_type = ( score_card[ 'Type' ] == pattern[ 'type' ] )
            metrics = norm_summary( score_card[ this_type ][ 'Score' ].value_counts() ,
                                    pattern[ 'display_name' ] , args )
            print( args.delim.join( '{}'.format( m ) for m in metrics ) )

