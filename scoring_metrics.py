import sys

from sets import Set

import pandas as pd

def new_score_card():
    return pd.DataFrame( columns = [ 'File' ,
                                     'Start' , 'End' ,
                                     'Type' , 'Score' ] )

##
## 
##

def evaluate_positions( gold_filename ,
                        score_card ,
                        gold_ss ,
                        test_ss ,
                        ignore_whitespace = False ):
    if( ignore_whitespace ):
        start_key = 'begin_pos_mapped'
        end_key = 'end_pos_mapped'
    else:
        start_key = 'begin_pos'
        end_key = 'end_pos'
    ##
    gold_keys = gold_ss.keys()
    gold_keys.sort( key = int )
    test_keys = test_ss.keys()
    test_keys.sort( key = int )
    last_test_key_index = -1
    matched_test_keys = Set()
    for gold_key in gold_keys:
        ## grab type and end position
        ## TODO - loop over all entries in the dictionary
        gold_type = gold_ss[ gold_key ][ 0 ][ 'type' ]
        gold_start = gold_ss[ gold_key ][ 0 ][ start_key ]
        gold_end = gold_ss[ gold_key ][ 0 ][ end_key ]
        ## Loop through all the test keys after our last matching key
        test_key_index = last_test_key_index + 1
        while( test_key_index < len( test_keys ) ):
            test_key = test_keys[ test_key_index ]
            ## grab type and end position
            test_type = test_ss[ test_key ][ 0 ][ 'type' ]
            test_start = test_ss[ test_key ][ 0 ][ start_key ]
            test_end = test_ss[ test_key ][ 0 ][ end_key ]
            if( gold_start == test_start ):
                ## If the types match...
                if( gold_type == test_type ):
                    ## ... and the end positions match, then we have a
                    ##     perfect match
                    if( gold_end == test_end ):
                        score_card.loc[ score_card.shape[ 0 ] ] = \
                          [ gold_filename , gold_start , gold_end ,
                            gold_type , 'TP' ]
                    elif( gold_end < test_end ):
                        ## If the gold end position is prior to the system
                        ## determined end position, we consider this a
                        ## 'fully contained' match and also count it
                        ## as a win (until we score strict vs. lenient matches)
                        score_card.loc[ score_card.shape[ 0 ] ] = \
                          [ gold_filename , gold_start , gold_end ,
                            gold_type , 'TP' ]
                    else:
                        ## otherwise, we missed some data that needs
                        ## to be captured.  For now, this is also
                        ## a win but will not always count.
                        score_card.loc[ score_card.shape[ 0 ] ] = \
                          [ gold_filename , gold_start , gold_end ,
                            gold_type , 'TP' ]
                else:
                    score_card.loc[ score_card.shape[ 0 ] ] = \
                      [ gold_filename , gold_start , gold_end ,
                        gold_type , 'FN' ]
                    score_card.loc[ score_card.shape[ 0 ] ] = \
                      [ gold_filename , gold_start , test_end ,
                        test_type , 'FP' ]
                ## Everything within this block counts as a match
                ## so we need to update out index tracker and
                ## break out of the loop
                matched_test_keys.add( test_key )
                last_test_key_index = test_key_index
                break
            test_key_index += 1
        ## If these aren't equal, then we didn't find a match
        if( last_test_key_index < test_key_index ):
            score_card.loc[ score_card.shape[ 0 ] ] = \
              [ gold_filename , gold_start , gold_end , gold_type , 'FN' ]
    for test_key in test_keys:
        if( test_key in matched_test_keys ):
            continue
        ## grab type and end position
        test_type = test_ss[ test_key ][ 0 ][ 'type' ]
        test_start = test_ss[ test_key ][ 0 ][ start_key ]
        test_end = test_ss[ test_key ][ 0 ][ end_key ]
        score_card.loc[ score_card.shape[ 0 ] ] = \
          [ gold_filename , test_start , test_end , test_type , 'FP' ]
    ##
    return score_card

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


def add_missing_fields( score_summary ):
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
                            row_name = 'aggregate' , args = args )
    print( args.delim.join( '{}'.format( m ) for m in metrics ) )
    ##
    if( args.by_file or args.by_file_and_type ):
        for filename in file_list:
            this_file = ( score_card[ 'File' ] == filename )
            metrics = norm_summary( score_card[ this_file ][ 'Score' ].value_counts() ,
                                    row_name = filename , args = args )
            print( args.delim.join( '{}'.format( m ) for m in metrics ) )
            if( args.by_file_and_type ):
                unique_types = Set()
                for pattern in gold_config:
                    unique_types.add( pattern[ 'type' ] )
                for unique_type in sorted( unique_types ):
                    this_type = \
                      (  ( score_card[ 'File' ] == filename ) &
                         ( score_card[ 'Type' ] == unique_type ) )
                    metrics = \
                      norm_summary( score_card[ this_type ][ 'Score' ].value_counts() ,
                                    row_name = filename + ' x ' + unique_type ,
                                    args = args )
                    print( args.delim.join( '{}'.format( m ) for m in metrics ) )
    ##
    if( args.by_type ):
        unique_types = Set()
        for pattern in gold_config:
            unique_types.add( pattern[ 'type' ] )
        for unique_type in sorted( unique_types ):
            this_type = ( score_card[ 'Type' ] == unique_type )
            metrics = norm_summary( score_card[ this_type ][ 'Score' ].value_counts() ,
                                    row_name = unique_type ,
                                    args = args )
            print( args.delim.join( '{}'.format( m ) for m in metrics ) )


def print_counts_summary( type_counts , file_list ,
                          test_config ,
                          args ):
    unique_types = Set()
    for pattern in test_config:
        unique_types.add( pattern[ 'type' ] )        
    print( '{}{}{}'.format( '\n#########' ,
                            args.delim ,
                            args.delim.join( '{}'.format( t ) for t in unique_types ) ) )
    ##
    aggregate_type_counts = type_counts[ 'Type' ].value_counts()
    type_matches = []
    for unique_type in sorted( unique_types ):
        if( unique_type in aggregate_type_counts.keys() ):
            type_matches.append( aggregate_type_counts[ unique_type ] )
        else:
            type_matches.append( 0 )
    print( '{}{}{}'.format( 'aggregate' ,
                            args.delim ,
                            args.delim.join( '{}'.format( m ) for m in type_matches ) ) )
    ##
    if( args.by_file ):
        for filename in file_list:
            this_file = ( type_counts[ 'File' ] == filename )
            file_type_counts = type_counts[ this_file ][ 'Type' ].value_counts()
            type_matches = []
            for unique_type in sorted( unique_types ):
                if( unique_type in file_type_counts.keys() ):
                    type_matches.append( file_type_counts[ unique_type ] )
                else:
                    type_matches.append( 0 )
            print( '{}{}{}'.format( filename ,
                                    args.delim ,
                                    args.delim.join( '{}'.format( m ) for m in type_matches ) ) )


