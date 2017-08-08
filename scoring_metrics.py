import sys
import logging as log

from sets import Set

import pandas as pd

def new_score_card():
    return pd.DataFrame( columns = [ 'File' ,
                                     'Start' , 'End' ,
                                     'Type' , 'Score' ] )

def get_annotation_from_base_entry( annotation_entry ,
                                    start_key ,
                                    end_key ):
    try:
        annotation_type = annotation_entry[ 'type' ]
    except KeyError as e:
        log.warn( 'Could not access annotation type.  Skipping entry.' )
        return None , None , None
    try:
        annotation_start = annotation_entry[ start_key ]
    except KeyError as e:
        log.warn( 'Could not access annotation type.  Skipping entry.' )
        return None , None , None
    try:
        annotation_end = annotation_entry[ end_key ]
    except KeyError as e:
        log.warn( 'Could not access annotation type.  Skipping entry.' )
        return None , None , None
    log.debug( '{} ( {} - {} )'.format( annotation_type ,
                                        annotation_start ,
                                        annotation_end ) )
    return annotation_type , annotation_start , annotation_end


##
## 
##

def evaluate_positions( gold_filename ,
                        score_card ,
                        gold_ss ,
                        test_ss ,
                        ignore_whitespace = False ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( ignore_whitespace ):
        start_key = 'begin_pos_mapped'
        end_key = 'end_pos_mapped'
    else:
        start_key = 'begin_pos'
        end_key = 'end_pos'
    ##
    log.debug( 'Anchoring positions at \'{}\' and \'{}\''.format( start_key ,
                                                                  end_key ) )
    gold_keys = gold_ss.keys()
    if( len( gold_keys ) == 0 ):
        log.debug( 'Zero gold keys in strict starts dictionary' )
    else:
        gold_keys.sort( key = int )
        log.debug( '{} gold keys ranging from {} to {}'.format( len( gold_keys ) ,
                                                                gold_keys[ 0 ] ,
                                                                gold_keys[ -1 ] ) )
    ##
    test_keys = test_ss.keys()
    if( len( test_keys ) == 0 ):
        log.debug( 'Zero test keys in strict starts dictionary' )
    else:
        test_keys.sort( key = int )
        log.debug( '{} test keys ranging from {} to {}'.format( len( test_keys ) ,
                                                                test_keys[ 0 ] ,
                                                                test_keys[ -1 ] ) )
    ##
    last_test_key_index = -1
    matched_test_keys = Set()
    for gold_key in gold_keys:
        ## TODO - loop over all entries in the dictionary
        log.debug( 'These keys:  {}'.format( gold_ss[ gold_key ] ) )
        ## grab type and end position
        gold_type , gold_start , gold_end = \
          get_annotation_from_base_entry( gold_ss[ gold_key ][ 0 ] ,
                                          start_key ,
                                          end_key )
        if( gold_type == None ):
            continue
        ## Loop through all the test keys after our last matching key
        test_key_index = last_test_key_index + 1
        while( test_key_index < len( test_keys ) ):
            test_key = test_keys[ test_key_index ]
            ## grab type and end position
            test_type , test_start , test_end = \
              get_annotation_from_base_entry( test_ss[ test_key ][ 0 ] ,
                                              start_key ,
                                              end_key )
            if( test_type == None ):
                test_key_index += 1
                continue
            ##
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
        test_type , test_start , test_end = \
          get_annotation_from_base_entry( test_ss[ test_key ][ 0 ] ,
                                          start_key ,
                                          end_key )
        if( test_type == None ):
            continue
        score_card.loc[ score_card.shape[ 0 ] ] = \
          [ gold_filename , test_start , test_end , test_type , 'FP' ]
    ##
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
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
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    score_types = score_summary.keys()
    if( 'TP' not in score_types ):
        score_summary[ 'TP' ] = 0.0
    if( 'FP' not in score_types ):
        score_summary[ 'FP' ] = 0.0
    if( 'TN' not in score_types ):
        score_summary[ 'TN' ] = 0.0
    if( 'FN' not in score_types ):
        score_summary[ 'FN' ] = 0.0
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return score_summary


def norm_summary( score_summary , row_name , args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
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
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return metrics


def update_output_dictionary( gold_out_file ,
                              metrics_keys ,
                              metrics_values ):
    return None


def print_score_summary( score_card , file_mapping ,
                         gold_config , test_config ,
                         args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## TODO - refactor score printing to a separate function
    ## TODO - add scores grouped by type
    file_list = sorted( file_mapping.keys() )
    print( '{}{}{}'.format( '\n#########' ,
                            args.delim ,
                            args.delim.join( '{}'.format( m ) for m in args.metrics_list ) ) )
    ##
    metrics = norm_summary( score_card[ 'Score' ].value_counts() ,
                            row_name = 'aggregate' , args = args )
    print( args.delim.join( '{}'.format( m ) for m in metrics ) )
    ##
    args.test_out == None
    for filename in file_list:
        this_file = ( score_card[ 'File' ] == filename )
        metrics = norm_summary( score_card[ this_file ][ 'Score' ].value_counts() ,
                                row_name = filename , args = args )
        if( args.by_file or args.by_file_and_type ):
            print( args.delim.join( '{}'.format( m ) for m in metrics ) )
        if( args.gold_out ):
            gold_out_file = '{}/{}'.format( args.gold_out ,
                                            filename )
            update_output_dictionary( gold_out_file ,
                                      args.metrics_list ,
                                      metrics )
        if( args.test_out ):
            test_out_file = '{}/{}'.format( args.test_out ,
                                            file_mapping[ filename ] )
            update_output_dictionary( gold_out_file ,
                                      args.metrics_list ,
                                      metrics )
        ##
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
            if( args.by_file_and_type ):
                print( args.delim.join( '{}'.format( m ) for m in metrics ) )
            if( args.gold_out ):
                gold_out_file = '{}/{}'.format( args.gold_out ,
                                                filename )
                update_output_dictionary( gold_out_file ,
                                          args.metrics_list ,
                                          metrics )
            if( args.test_out ):
                test_out_file = '{}/{}'.format( args.test_out ,
                                                file_mapping[ filename ] )
                update_output_dictionary( gold_out_file ,
                                          args.metrics_list ,
                                          metrics )
    ##
    unique_types = Set()
    for pattern in gold_config:
        unique_types.add( pattern[ 'type' ] )
    for unique_type in sorted( unique_types ):
        this_type = ( score_card[ 'Type' ] == unique_type )
        metrics = norm_summary( score_card[ this_type ][ 'Score' ].value_counts() ,
                                row_name = unique_type ,
                                args = args )
        if( args.by_type or args.by_type_and_file ):
            print( args.delim.join( '{}'.format( m ) for m in metrics ) )
        ##
        for filename in file_list:
            this_file = \
              (  ( score_card[ 'File' ] == filename ) &
                 ( score_card[ 'Type' ] == unique_type ) )
            metrics = \
              norm_summary( score_card[ this_file ][ 'Score' ].value_counts() ,
                            row_name = unique_type + ' x ' + filename ,
                            args = args )
            if( args.by_type_and_file ):
                print( args.delim.join( '{}'.format( m ) for m in metrics ) )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def print_counts_summary( type_counts , file_mapping ,
                          test_config ,
                          args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    file_list = sorted( file_mapping.keys() )
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
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


