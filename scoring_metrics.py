import os
import sys
import logging as log

import json

from sets import Set

import pandas as pd

def new_score_card( fuzzy_flags = [ 'exact' ] ):
    score_card = {}
    for fuzzy_flag in fuzzy_flags:
        score_card[ fuzzy_flag ] = pd.DataFrame( columns = [ 'File' ,
                                                             'Start' , 'End' ,
                                                             'Type' , 'Score' ] )
    return score_card

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
        log.warn( 'Could not access annotation start key.  Skipping entry.' )
        return None , None , None
    try:
        annotation_end = annotation_entry[ end_key ]
    except KeyError as e:
        log.warn( 'Could not access annotation end key.  Skipping entry.' )
        return None , None , None
    log.debug( '{} ( {} - {} )'.format( annotation_type ,
                                        annotation_start ,
                                        annotation_end ) )
    return annotation_type , annotation_start , annotation_end


##
## 
##

def flatten_ss_dictionary( ss_dictionary ,
                           category = '(unknown)' ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    all_keys = ss_dictionary.keys()
    if( len( all_keys ) == 0 ):
        log.debug( 'Zero {} keys in strict starts dictionary'.format( category ) )
    else:
        all_keys.sort( key = int )
        log.debug( '{} {} keys ranging from {} to {}'.format( len( all_keys ) ,
                                                              category ,
                                                              all_keys[ 0 ] ,
                                                              all_keys[ -1 ] ) )
    ##
    flat_entries = []
    for this_key in all_keys:
        for annot_index in range( len( ss_dictionary[ this_key ] ) ):
            flat_entries.append( ss_dictionary[ this_key ][ annot_index ] )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return flat_entries


def update_score_card( condition , score_card , fuzzy_flag ,
                       filename , start_pos , end_pos , type ,
                       ref_annot = None , test_annot = None ):
    score_card[ fuzzy_flag ].loc[ score_card[ fuzzy_flag ].shape[ 0 ] ] = \
      [ filename , start_pos , end_pos ,
        type , condition ]


def reference_annot_comparison_runner( score_card , reference_filename ,
                                       reference_annot , reference_leftovers ,
                                       test_entries ,
                                       start_key , end_key ,
                                       fuzzy_flag ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## grab type and end position
    reference_type , reference_start , reference_end = \
      get_annotation_from_base_entry( reference_annot ,
                                      start_key ,
                                      end_key )
    if( reference_type == None ):
        ## If we couldn't extract a type, consider this
        ## an invalid annotations    
        return test_entries
    ## Loop through all the test annotations
    ## that haven't been matched yet
    test_leftovers = []
    matched_flag = False
    for test_annot in test_entries:
        if( matched_flag ):
            test_leftovers.append( test_annot )
            continue
        ## grab type and end position
        test_type , test_start , test_end = \
          get_annotation_from_base_entry( test_annot ,
                                          start_key ,
                                          end_key )
        if( test_type == None ):
            ## If we couldn't extract a type, consider this
            ## an invalid annotations
            continue
        ##
        if( reference_start == test_start ):
            ## If the types match...
            if( reference_type == test_type ):
                ## ... and the end positions match, then we have a
                ##     perfect match
                if( reference_end == test_end ):
                    update_score_card( 'TP' , score_card , fuzzy_flag ,
                                       reference_filename , reference_start , reference_end ,
                                       reference_type , reference_annot , test_annot )
                elif( test_end == 'EOF' or
                      reference_end < test_end ):
                    ## If the reference end position is prior to the system
                    ## determined end position, we consider this a
                    ## 'fully contained' match and also count it
                    ## as a win (until we score strict vs. lenient matches)
                    if( fuzzy_flag == 'exact' ):
                        update_score_card( 'FN' , score_card , fuzzy_flag ,
                                       reference_filename , reference_start , reference_end ,
                                       reference_type , reference_annot , test_annot )
                        update_score_card( 'FP' , score_card , fuzzy_flag ,
                                           reference_filename , test_start , test_end ,
                                           test_type , reference_annot , test_annot )
                    else:
                        update_score_card( 'TP' , score_card , fuzzy_flag ,
                                           reference_filename , reference_start , reference_end ,
                                           reference_type , reference_annot , test_annot )
                else:
                    ## otherwise, we missed some data that needs
                    ## to be captured.  For now, this is also
                    ## a win but will not always count.
                    if( fuzzy_flag == 'partial' ):
                        update_score_card( 'TP' , score_card , fuzzy_flag ,
                                           reference_filename , reference_start , reference_end ,
                                           reference_type , reference_annot , test_annot )
                    else:
                        update_score_card( 'FN' , score_card , fuzzy_flag ,
                                       reference_filename , reference_start , reference_end ,
                                       reference_type , reference_annot , test_annot )
                        update_score_card( 'FP' , score_card , fuzzy_flag ,
                                           reference_filename , test_start , test_end ,
                                           test_type , reference_annot , test_annot )
            else:
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , reference_annot , test_annot )
                update_score_card( 'FP' , score_card , fuzzy_flag ,
                                   reference_filename , test_start , test_end ,
                                   test_type , reference_annot , test_annot )
            ## Everything within this block counts as a match
            ## so we need to remove the current test_annot from
            ## the list of possible matches in the future and
            ## break out of the loop
            matched_flag = True
        elif( fuzzy_flag != 'exact' and
              reference_end == test_end ):
            ## The end offsets AND types may match...
            if( reference_type == test_type ):
                ##
                if( reference_start > test_start ):
                    ## If the reference start position is after the system
                    ## determined start position, we consider this a
                    ## 'fully contained' match and also count it
                    ## as a win
                    update_score_card( 'TP' , score_card , fuzzy_flag ,
                                       reference_filename , reference_start , reference_end ,
                                       reference_type , reference_annot , test_annot )
                else:
                    ## otherwise, we missed some data that needs
                    ## to be captured.  This is a partial win.
                    if( fuzzy_flag == 'partial' ):
                        update_score_card( 'TP' , score_card , fuzzy_flag ,
                                           reference_filename , reference_start , reference_end ,
                                           reference_type , reference_annot , test_annot )
                    else:
                        update_score_card( 'FN' , score_card , fuzzy_flag ,
                                           reference_filename , reference_start , reference_end ,
                                           reference_type , reference_annot , test_annot )
                        update_score_card( 'FP' , score_card , fuzzy_flag ,
                                           reference_filename , test_start , test_end ,
                                           test_type , reference_annot , test_annot )
            else:
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , reference_annot , test_annot )
                update_score_card( 'FP' , score_card , fuzzy_flag ,
                                   reference_filename , test_start , test_end ,
                                   test_type , reference_annot , test_annot )
            ## Everything within this block counts as a match
            ## so we need to remove the current test_annot from
            ## the list of possible matches in the future and
            ## break out of the loop
            matched_flag = True
        elif( fuzzy_flag != 'exact' and
              ( test_start == 'SOF' or test_start < reference_start ) and
              ( test_end == 'EOF' or test_end > reference_end ) and
              reference_type == test_type ):
            update_score_card( 'TP' , score_card , fuzzy_flag ,
                               reference_filename , reference_start , reference_end ,
                               reference_type , reference_annot , test_annot )
            ## Everything within this block counts as a match
            ## so we need to remove the current test_annot from
            ## the list of possible matches in the future and
            ## break out of the loop
            matched_flag = True
        elif( fuzzy_flag == 'partial' and
              ( ( ( test_end == 'EOF' or test_end <= reference_end ) and
                  test_end > reference_start ) or
                ( ( test_start == 'SOF' or test_start >= reference_start ) and
                  test_start < reference_end ) ) and
              reference_type == test_type ):
            update_score_card( 'TP' , score_card , fuzzy_flag ,
                               reference_filename , reference_start , reference_end ,
                               reference_type , reference_annot , test_annot )
            ## Everything within this block counts as a match
            ## so we need to remove the current test_annot from
            ## the list of possible matches in the future and
            ## break out of the loop
            matched_flag = True
        else:
            test_leftovers.append( test_annot )
    if( not matched_flag ):
        reference_leftovers.append( reference_annot )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return test_leftovers


def evaluate_positions( reference_filename ,
                        score_card ,
                        reference_ss ,
                        test_ss ,
                        fuzzy_flag = 'exact' ,
                        use_mapped_chars = False ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( use_mapped_chars ):
        start_key = 'begin_pos_mapped'
        end_key = 'end_pos_mapped'
    else:
        start_key = 'begin_pos'
        end_key = 'end_pos'
    ##
    log.debug( 'Anchoring positions at \'{}\' and \'{}\''.format( start_key ,
                                                                  end_key ) )
    reference_entries = flatten_ss_dictionary( reference_ss , 'reference' )
    test_entries = flatten_ss_dictionary( test_ss , 'test' )
    ##
    reference_leftovers = []
    test_leftovers = test_entries
    for reference_annot in reference_entries:
        test_leftovers = \
          reference_annot_comparison_runner( score_card , reference_filename ,
                                             reference_annot , reference_leftovers ,
                                             test_entries ,
                                             start_key , end_key ,
                                             fuzzy_flag )
        test_entries = test_leftovers
    ## any remaining entries in the reference set are FNs
    for reference_annot in reference_leftovers:
        ## grab type and end position
        reference_type , reference_start , reference_end = \
          get_annotation_from_base_entry( reference_annot ,
                                          start_key ,
                                          end_key )
        update_score_card( 'FN' , score_card , fuzzy_flag ,
                           reference_filename , reference_start , reference_end ,
                           reference_type , reference_annot , None )
    for test_annot in test_leftovers:
        ## grab type and end position
        test_type , test_start , test_end = \
          get_annotation_from_base_entry( test_annot ,
                                          start_key ,
                                          end_key )
        if( test_type == None ):
            continue
        update_score_card( 'FP' , score_card , fuzzy_flag ,
                           reference_filename , test_start , test_end ,
                           test_type , None , test_annot )
    ##
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )

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


def norm_summary( score_summary , args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## Source for definitions:
    ## -- https://en.wikipedia.org/wiki/Precision_and_recall#Definition_.28classification_context.29
    ##
    ## First, we want to make sure that all score types are represented
    ## in the summary series.
    add_missing_fields( score_summary )
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
    metrics = []
    for metric in args.metrics_list:
        metrics.append( score_summary[ metric ] )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return metrics


def recursive_deep_key_value_pair( dictionary , path , key , value ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( len( path ) == 0 ):
        dictionary[ key ] = value
    else:
        pop_path = path[ 0 ]
        if( pop_path not in dictionary.keys() ):
            dictionary[ pop_path ] = {}
        dictionary[ pop_path ] = recursive_deep_key_value_pair( dictionary[ pop_path ] ,
                                                                path[ 1: ] ,
                                                                key ,
                                                                value )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return dictionary


def update_output_dictionary( out_file ,
                              metric_type ,
                              metrics_keys ,
                              metrics_values ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( os.path.exists( out_file ) ):
        try:
            with open( out_file , 'r' ) as fp:
                file_dictionary = json.load( fp )
        except ValueError , e:
            log.error( 'I can\'t update the output dictionary \'{}\'' + \
                       'because I had a problem loading it into memory:  ' + \
                       '{}'.format( out_file ,
                                    e ) )
            log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
            return
    else:
        file_dictionary = {}
    for key , value in zip( metrics_keys , metrics_values ):
        file_dictionary = recursive_deep_key_value_pair( file_dictionary ,
                                                         metric_type ,
                                                         key ,
                                                         value )
    with open( out_file , 'w' ) as fp:
        json.dump( file_dictionary , fp ,
                   indent = 4 )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )

def update_csv_output( csv_out_filename , delimiter ,
                       row_content ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    with open( csv_out_filename , 'a' ) as fp:
        fp.write( '{}\n'.format( delimiter.join( row_content ) ) )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )

def output_metrics( class_data ,
                    fuzzy_flag , metrics , delimiter , csv_out_filename ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    row_content = delimiter.join( '{}'.format( m ) for m in metrics )
    if( len( class_data ) == 1 ):
        row_name = class_data[ 0 ]
    elif( len( class_data ) == 2 ):
        row_name = class_data[ 1 ]
    elif( len( class_data ) == 4 ):
        row_name = '{} x {}'.format( class_data[ 1 ] ,
                                     class_data[ 3 ] )
    print( '{}{}{}'.format( row_name , delimiter , row_content ) )
    ##
    if( csv_out_filename ):
        full_row = [ fuzzy_flag ]
        for n in range( 0 , 4 ):
            if( n >= len( class_data ) ):
                full_row.append( '' )
            else:
                full_row.append( class_data[ n ] )
        full_row.append( row_content )
        update_csv_output( csv_out_filename , delimiter ,
                           full_row )
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )

def print_score_summary( score_card , file_mapping ,
                         reference_config , test_config ,
                         fuzzy_flag ,
                         args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## TODO - refactor score printing to a separate function
    ## TODO - add scores grouped by type
    file_list = sorted( file_mapping.keys() )
    metrics_header_line = \
      args.delim.join( '{}'.format( m ) for m in args.metrics_list )
    print( '\n{}{}{}'.format( fuzzy_flag ,
                              args.delim ,
                              metrics_header_line ) )
    if( args.csv_out and
        not os.path.exists( args.csv_out ) ):
        update_csv_output( args.csv_out , args.delim ,
                           [ 'FuzzyFlag' ,
                             'ClassType' , 'Class' ,
                             'SubClassType' , 'SubClass' ,
                             metrics_header_line ] )
    ##
    metrics = norm_summary( score_card[ fuzzy_flag ][ 'Score' ].value_counts() ,
                            args = args )
    output_metrics( [ 'micro-average' ] ,
                    fuzzy_flag , metrics , args.delim , args.csv_out )
    ##
    if( args.corpus_out ):
        update_output_dictionary( args.corpus_out ,
                                  [ 'metrics' ,
                                    fuzzy_flag ,
                                    'micro-average' ] ,
                                  args.metrics_list ,
                                  metrics )
    ##
    file_aggregate_metrics = None
    non_empty_files = 0
    for filename in file_list:
        if( args.corpus_out ):
            update_output_dictionary( args.corpus_out ,
                                      [ 'file-mapping' ] ,
                                      [ filename ] ,
                                      [ file_mapping[ filename ] ] )
        this_file = ( score_card[ fuzzy_flag ][ 'File' ] == filename )
        file_value_counts = score_card[ fuzzy_flag ][ this_file ][ 'Score' ].value_counts()
        metrics = norm_summary( file_value_counts , args = args )
        if( args.by_file or args.by_file_and_type ):
            output_metrics( [ 'File' , filename ] ,
                            fuzzy_flag , metrics , args.delim , args.csv_out )
            ## Only update macro-average if some annotation in this file exists
            ## in either reference or system output
            if( sum( file_value_counts ) > 0 ):
                non_empty_files += 1
                if( file_aggregate_metrics == None ):
                    file_aggregate_metrics = metrics
                else:
                    file_aggregate_metrics = \
                      [ sum( pair ) for pair in zip( file_aggregate_metrics ,
                                                     metrics ) ]
        if( args.reference_out ):
            out_file = '{}/{}'.format( args.reference_out ,
                                       filename )
            update_output_dictionary( out_file ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'micro-average' ] ,
                                      args.metrics_list ,
                                      metrics )
        if( args.test_out and file_mapping[ filename ] != None ):
            out_file = '{}/{}'.format( args.test_out ,
                                       file_mapping[ filename ] )
            update_output_dictionary( out_file ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'micro-average' ] ,
                                      args.metrics_list ,
                                      metrics )
        ##
        unique_types = Set()
        for pattern in reference_config:
            unique_types.add( pattern[ 'type' ] )
        for unique_type in sorted( unique_types ):
            this_type = \
              (  ( score_card[ fuzzy_flag ][ 'File' ] == filename ) &
                 ( score_card[ fuzzy_flag ][ 'Type' ] == unique_type ) )
            type_value_counts = \
              score_card[ fuzzy_flag ][ this_type ][ 'Score' ].value_counts()
            metrics = \
              norm_summary( type_value_counts ,
                            args = args )
            if( args.by_file_and_type ):
                output_metrics( [ 'File' , filename , 'Type' , unique_type ] ,
                                fuzzy_flag , metrics , args.delim , args.csv_out )
            if( args.reference_out ):
                out_file = '{}/{}'.format( args.reference_out ,
                                           filename )
                update_output_dictionary( out_file ,
                                          [ 'metrics' ,
                                            fuzzy_flag ,
                                            'by-type' , unique_type ] ,
                                          args.metrics_list ,
                                          metrics )
            if( args.test_out and file_mapping[ filename ] != None ):
                out_file = '{}/{}'.format( args.test_out ,
                                           file_mapping[ filename ] )
                update_output_dictionary( out_file ,
                                          [ 'metrics' ,
                                            fuzzy_flag ,
                                            'by-type' , unique_type ] ,
                                          args.metrics_list ,
                                          metrics )
    if( non_empty_files > 0 ):
        macro_averaged_metrics = []
        for key , value in zip( args.metrics_list , file_aggregate_metrics ):
            if( key == 'TP' or
                key == 'FP' or
                key == 'FN' or
                key == 'FP' ):
                macro_averaged_metrics.append( value )
            else:
                macro_averaged_metrics.append( value / non_empty_files )
        if( args.by_file or args.by_file_and_type ):
            output_metrics( [ 'macro-averages' , 'macro-average by file' ] ,
                            fuzzy_flag , macro_averaged_metrics ,
                            args.delim , args.csv_out )
        if( args.corpus_out ):
            update_output_dictionary( args.corpus_out ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'macro-averages' , 'file' ] ,
                                      args.metrics_list ,
                                      macro_averaged_metrics[ 1: ] )
    ##
    unique_types = Set()
    type_aggregate_metrics = None
    non_empty_types = 0
    for pattern in reference_config:
        unique_types.add( pattern[ 'type' ] )
    for unique_type in sorted( unique_types ):
        this_type = ( score_card[ fuzzy_flag ][ 'Type' ] == unique_type )
        type_value_counts = score_card[ fuzzy_flag ][ this_type ][ 'Score' ].value_counts()
        metrics = norm_summary( type_value_counts ,
                                args = args )
        if( args.by_type or args.by_type_and_file ):
            output_metrics( [ 'Type' , unique_type ] ,
                            fuzzy_flag , metrics , args.delim , args.csv_out )
            ## Only update macro-average if some of this type exist
            ## in either reference or system output
            if( sum( type_value_counts ) > 0 ):
                non_empty_types += 1
                if( type_aggregate_metrics == None ):
                    type_aggregate_metrics = metrics
                else:
                    type_aggregate_metrics = \
                      [ sum( pair ) for pair in zip( type_aggregate_metrics ,
                                                     metrics ) ]
        if( args.corpus_out ):
            update_output_dictionary( args.corpus_out ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'by-type' , unique_type ] ,
                                      args.metrics_list ,
                                      metrics )
        ##
        for filename in file_list:
            this_file = \
              (  ( score_card[ fuzzy_flag ][ 'File' ] == filename ) &
                 ( score_card[ fuzzy_flag ][ 'Type' ] == unique_type ) )
            file_value_counts = \
              score_card[ fuzzy_flag ][ this_file ][ 'Score' ].value_counts()
            metrics = \
              norm_summary( file_value_counts ,
                            args = args )
            if( args.by_type_and_file ):
                output_metrics( [ 'Type' , unique_type ,
                                  'File' , filename ] ,
                                fuzzy_flag , metrics , args.delim , args.csv_out )
    if( non_empty_types > 0 ):
        macro_averaged_metrics = []
        for key , value in zip( args.metrics_list , type_aggregate_metrics ):
            if( key == 'TP' or
                key == 'FP' or
                key == 'FN' or
                key == 'FP' ):
                macro_averaged_metrics.append( value )
            else:
                macro_averaged_metrics.append( value / non_empty_types )
        if( args.by_type or args.by_type_and_file ):
            output_metrics( [ 'macro-averages' , 'macro-average by type' ] ,
                            fuzzy_flag , macro_averaged_metrics ,
                            args.delim , args.csv_out )
        if( args.corpus_out ):
            update_output_dictionary( args.corpus_out ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'macro-averages' , 'type' ] ,
                                      args.metrics_list ,
                                      macro_averaged_metrics )
    ##
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
    print( '{}{}{}'.format( 'micro-average' ,
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


