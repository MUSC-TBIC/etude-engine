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
                                                             'Type' , 'Pivot' , 'Score' ] )
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
        try:
            annotation_start = int( annotation_start )
        except ValueError:
            log.debug( 'Annotation start position could not be converted to int.  Treating as a string:  {}'.format( annotation_start ) )
    except KeyError as e:
        log.warn( 'Could not access annotation start key.  Skipping entry.' )
        return None , None , None
    try:
        annotation_end = annotation_entry[ end_key ]
        try:
            annotation_end = int( annotation_end )
        except ValueError:
            log.debug( 'Annotation end position could not be converted to int.  Treating as a string:  {}'.format( annotation_end ) )
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


def update_confusion_matrix( confusion_matrix , fuzzy_flag ,
                             ref_type , test_type ):
    ##########################
    ## Before we touch a cell
    ## in the confusion matrix,
    ## we need to make sure that
    ## the full path to it exists
    if( fuzzy_flag not in confusion_matrix ):
        confusion_matrix[ fuzzy_flag ] = {}
    ##
    if( ref_type not in confusion_matrix[ fuzzy_flag ] ):
        confusion_matrix[ fuzzy_flag ][ ref_type ] = {}
    ##
    if( test_type not in confusion_matrix[ fuzzy_flag ][ ref_type ] ):
        confusion_matrix[ fuzzy_flag ][ ref_type ][ test_type ] = 0
    ##########################
    ## Update the correct cell
    ## of the confusion matrix
    confusion_matrix[ fuzzy_flag ][ ref_type ][ test_type ] += 1


def update_score_card( condition , score_card , fuzzy_flag ,
                       filename , start_pos , end_pos , type , pivot_value = None ,
                       ref_annot = None , test_annot = None ):
    score_card[ fuzzy_flag ].loc[ score_card[ fuzzy_flag ].shape[ 0 ] ] = \
      [ filename , start_pos , end_pos ,
        type , pivot_value , condition ]


def exact_comparison_runner( reference_filename , confusion_matrix , score_card , 
                             reference_annot ,
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
        return( False , test_entries )
    ## Loop through all the test annotations
    ## that haven't been matched yet
    test_leftovers = []
    matched_flag = False
    for test_annot in test_entries:
        ## TODO - nesting comparisons, multiple overlaps
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
            ## an invalid annotation
            continue
        if( reference_start == test_start and
            reference_end == test_end ):
            matched_flag = True
            update_confusion_matrix( confusion_matrix , fuzzy_flag , reference_type , test_type )
            ## If the types match...
            if( reference_type == test_type ):
                ## ... and the end positions match, then we have a
                ##     perfect match
                update_score_card( 'TP' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type ,
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
            else:
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
                update_score_card( 'FP' , score_card , fuzzy_flag ,
                                   reference_filename , test_start , test_end ,
                                   test_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
        else:
            test_leftovers.append( test_annot )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return( matched_flag , test_leftovers )


def fully_contained_comparison_runner( reference_filename , confusion_matrix , score_card , 
                                       reference_annot ,
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
        return( False , test_entries )
    ## Loop through all the test annotations
    ## that haven't been matched yet
    test_leftovers = []
    matched_flag = False
    for test_annot in test_entries:
        ## TODO - nesting comparisons, multiple overlaps
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
            ## an invalid annotation
            continue
        if( ( test_start == 'SOF' or
              test_start <= reference_start ) and
            ( test_end == 'EOF' or
              reference_end <= test_end ) ):
            matched_flag = True
            update_confusion_matrix( confusion_matrix , fuzzy_flag , reference_type , test_type )
            ## If the types match...
            if( reference_type == test_type ):
                update_score_card( 'TP' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
            else:
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
                update_score_card( 'FP' , score_card , fuzzy_flag ,
                                   reference_filename , test_start , test_end ,
                                   test_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
        else:
            test_leftovers.append( test_annot )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return( matched_flag , test_leftovers )


def partial_comparison_runner( reference_filename , confusion_matrix , score_card , 
                               reference_annot ,
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
        return( False , test_entries )
    ## Loop through all the test annotations
    ## that haven't been matched yet
    test_leftovers = []
    matched_flag = False
    for test_annot in test_entries:
        ## TODO - nesting comparisons, multiple overlaps
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
            ## an invalid annotation
            continue
        if( ( ( reference_start == 'SOF' or
                reference_start <= test_start ) and
              ( reference_end == 'EOF' or
                reference_end > test_start ) ) or
            ( ( reference_start == 'SOF' or
                reference_start < test_end ) and
              ( reference_end == 'EOF' or
                reference_end >= test_end ) ) ):
            matched_flag = True
            update_confusion_matrix( confusion_matrix , fuzzy_flag , reference_type , test_type )
            ## If the types match...
            if( reference_type == test_type ):
                update_score_card( 'TP' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
            else:
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
                update_score_card( 'FP' , score_card , fuzzy_flag ,
                                   reference_filename , test_start , test_end ,
                                   test_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = test_annot )
        else:
            test_leftovers.append( test_annot )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return( matched_flag , test_leftovers )


def reference_annot_comparison_runner( reference_filename , confusion_matrix , score_card , 
                                       reference_annot , 
                                       test_entries ,
                                       start_key , end_key ,
                                       fuzzy_flag ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    reference_matched, test_leftovers = exact_comparison_runner( reference_filename ,
                                                                 confusion_matrix ,
                                                                 score_card , 
                                                                 reference_annot ,
                                                                 test_entries ,
                                                                 start_key , end_key ,
                                                                 fuzzy_flag )
    if( fuzzy_flag == 'exact' or
        reference_matched ):
        return( reference_matched , test_leftovers )
    reference_matched, test_leftovers = fully_contained_comparison_runner( reference_filename ,
                                                                           confusion_matrix ,
                                                                           score_card , 
                                                                           reference_annot ,
                                                                           test_leftovers ,
                                                                           start_key , end_key ,
                                                                           fuzzy_flag )
    if( fuzzy_flag == 'fully-contained' or
        reference_matched ):
        return( reference_matched , test_leftovers )
    reference_matched , test_leftovers = partial_comparison_runner( reference_filename ,
                                                                    confusion_matrix ,
                                                                    score_card , 
                                                                    reference_annot ,
                                                                    test_leftovers ,
                                                                    start_key , end_key ,
                                                                    fuzzy_flag )
    return( reference_matched , test_leftovers )


def evaluate_positions( reference_filename ,
                        confusion_matrix ,
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
    ## In case there are no reference_entries, initialize test_leftovers
    ## as the full list of test_entries
    test_leftovers = test_entries
    ##
    for reference_annot in reference_entries:
        reference_matched , test_leftovers = \
          reference_annot_comparison_runner( reference_filename , confusion_matrix , score_card ,
                                             reference_annot ,
                                             test_entries ,
                                             start_key , end_key ,
                                             fuzzy_flag )
        test_entries = test_leftovers
        if( not reference_matched ):
            ## grab type and end position
            reference_type , reference_start , reference_end = \
              get_annotation_from_base_entry( reference_annot ,
                                              start_key ,
                                              end_key )
            if( reference_type != None ):
                update_confusion_matrix( confusion_matrix , fuzzy_flag , reference_type , '*FN*' )
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type , 
                                   ref_annot = reference_annot ,
                                   test_annot = None )
    ## any remaining entries in the reference set are FNs
    for test_annot in test_leftovers:
        ## grab type and end position
        test_type , test_start , test_end = \
          get_annotation_from_base_entry( test_annot ,
                                          start_key ,
                                          end_key )
        if( test_type == None ):
            continue
        update_confusion_matrix( confusion_matrix , fuzzy_flag , '*FP*' , test_type )
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
        return None


def precision( tp , fp ):
    if( fp + tp > 0 ):
        return tp / float( fp + tp )
    else:
        return None


def recall( tp , fn ):
    if( fn + tp > 0 ):
        return tp / float( fn + tp )
    else:
        return None


def specificity( tn , fn ):
    if( tn + fn > 0 ):
        return tn / float( tn + fn )
    else:
        return None


def f_score( p , r , beta = 1 ):
    if( p != None and r != None and p + r > 0 ):
        return ( 1 + ( beta**2 ) ) * ( p * r ) / \
            ( ( ( beta**2 ) * p ) + r )
    else:
        return None


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
                    fuzzy_flag , metrics ,
                    delimiter_prefix , delimiter ,
                    stdout_flag , csv_out_filename ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    row_content = delimiter.join( '{}'.format( m ) for m in metrics )
    if( len( class_data ) == 1 ):
        row_name = class_data[ 0 ]
    elif( len( class_data ) == 2 ):
        row_name = class_data[ 1 ]
    elif( len( class_data ) == 4 ):
        row_name = '{} x {}'.format( class_data[ 1 ] ,
                                     class_data[ 3 ] )
    if( stdout_flag ):
        print( '{}{}{}{}'.format( delimiter_prefix , row_name , delimiter , row_content ) )
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
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def print_counts_summary( score_card , file_list ,
                          config_patterns , 
                          args ,
                          set_type ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## TODO - refactor score printing to a separate function
    ## TODO - add scores grouped by type
    if( args.write_score_cards ):
        if( set_type == 'reference' ):
            if( args.reference_out == None ):
                log.warn( 'I could not write the reference counts score_card to disk:  --write-score-cards set but no --reference-out set' )
            else:
                score_card[ 'counts' ].to_csv( '{}/{}'.format( args.reference_out ,
                                                               'counts_score_card.csv' ) ,
                                               sep = '\t' ,
                                               encoding = 'utf-8' ,
                                               index = False )
        elif( set_type == 'test' ):
            if( args.test_out == None ):
                log.warn( 'I could not write the test counts score_card to disk:  --write-score-cards set but no --test-out set' )
            else:
                score_card[ 'counts' ].to_csv( '{}/{}'.format( args.test_out ,
                                                               'counts_score_card.csv' ) ,
                                               sep = '\t' ,
                                               encoding = 'utf-8' ,
                                               index = False )
    ##
    metrics_header_line = \
      args.delim.join( '{}'.format( m ) for m in [ 'n' ] )
    if( args.print_counts ):
        print( '\n{}{}{}{}'.format( args.delim_prefix ,
                                    'counts' ,
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
    metrics = [ score_card[ 'counts' ][ 'Score' ].value_counts()[ 'Tally' ] ]
    output_metrics( [ 'Total' ] ,
                    'counts' , metrics ,
                    args.delim_prefix , args.delim ,
                    args.print_counts , args.csv_out )
    ##
    file_aggregate_metrics = None
    non_empty_files = 0
    for filename in file_list:
        this_file = ( score_card[ 'counts' ][ 'File' ] == filename )
        file_value_counts = score_card[ 'counts' ][ this_file ][ 'Score' ].value_counts()
        ## TODO - add flag to only print non-zero entries
        if( len( file_value_counts ) == 0 ):
            metrics = [ 0 ]
        else:
            metrics = [ file_value_counts[ 'Tally' ] ]
        if( args.by_file or args.by_file_and_type ):
            output_metrics( [ 'File' , filename ] ,
                            'counts' , metrics ,
                            args.delim_prefix , args.delim ,
                            args.print_counts , args.csv_out )
        ##
        unique_types = Set()
        for pattern in config_patterns:
            unique_types.add( pattern[ 'type' ] )
        for unique_type in sorted( unique_types ):
            this_type = \
              (  ( score_card[ 'counts' ][ 'File' ] == filename ) &
                 ( score_card[ 'counts' ][ 'Type' ] == unique_type ) )
            type_value_counts = \
              score_card[ 'counts' ][ this_type ][ 'Score' ].value_counts()
            ## TODO - add flag to only print non-zero entries
            if( len( type_value_counts ) == 0 ):
                metrics = [ 0 ]
            else:
                metrics = [ type_value_counts[ 'Tally' ] ]
            if( args.by_file_and_type ):
                output_metrics( [ 'File' , filename , 'Type' , unique_type ] ,
                                'counts' , metrics ,
                                args.delim_prefix , args.delim ,
                                args.print_counts , args.csv_out )
    ##
    unique_types = Set()
    type_aggregate_metrics = None
    non_empty_types = 0
    for pattern in config_patterns:
        if( 'pivot_attr' in pattern.keys() ):
            ## TODO - pull this fron the config file
            for pivot_value in [ 'met' , 'not met' ]: ##pattern[ 'pivot_values' ]:
                this_type = '{} = "{}"'.format( pattern[ 'type' ] , pivot_value )
                unique_types.add( this_type )
        else:
            unique_types.add( pattern[ 'type' ] )
    for unique_type in sorted( unique_types ):
        this_type = ( score_card[ 'counts' ][ 'Type' ] == unique_type )
        type_value_counts = score_card[ 'counts' ][ this_type ][ 'Score' ].value_counts()
        ## TODO - add flag to only print non-zero entries
        if( len( type_value_counts ) == 0 ):
            metrics = [ 0 ]
        else:
            metrics = [ type_value_counts[ 'Tally' ] ]
        if( args.by_type or args.by_type_and_file ):
            output_metrics( [ 'Type' , unique_type ] ,
                            'counts' , metrics ,
                            args.delim_prefix , args.delim ,
                            args.print_counts , args.csv_out )
        ##
        for filename in file_list:
            this_file = \
              (  ( score_card[ 'counts' ][ 'File' ] == filename ) &
                 ( score_card[ 'counts' ][ 'Type' ] == unique_type ) )
            file_value_counts = \
              score_card[ 'counts' ][ this_file ][ 'Score' ].value_counts()
            ## TODO - add flag to only print non-zero entries
            if( len( file_value_counts ) == 0 ):
                metrics = [ 0 ]
            else:
                metrics = [ file_value_counts[ 'Tally' ] ]
            if( args.by_type_and_file ):
                output_metrics( [ 'Type' , unique_type ,
                                 'File' , filename ] ,
                                'counts' , metrics ,
                                args.delim_prefix , args.delim ,
                                args.print_counts , args.csv_out )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def print_confusion_matrix_shell( confusion_matrix ,
                                  file_mapping ,
                                  reference_patterns , test_patterns ,
                                  args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    try:
        for fuzzy_flag in args.fuzzy_flags:
            print_confusion_matrix( confusion_matrix ,
                                    file_mapping ,
                                    reference_patterns , test_patterns ,
                                    fuzzy_flag = fuzzy_flag ,
                                    args = args )
    except KeyError , e:
        log.error( 'KeyError exception in print_confusion_matrix:  {}'.format( e ) )
    except NameError , e:
        log.error( 'NameError exception in print_confusion_matrix:  {}'.format( e ) )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in print_confusion_matrix:  {}'.format( e ) )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def print_confusion_matrix( confusion_matrix ,
                            file_mapping ,
                            reference_config , test_config ,
                            fuzzy_flag ,
                            args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    file_list = sorted( file_mapping.keys() )
    unique_ref_types = Set()
    unique_test_types = Set()
    unique_ref_types.add( '*FP*' )
    unique_test_types.add( '*FN*' )
    for pattern in reference_config:
        unique_ref_types.add( pattern[ 'type' ] )
        unique_test_types.add( pattern[ 'type' ] )
    type_header_line = \
      args.delim.join( '{}'.format( m ) for m in sorted( unique_ref_types ) )
    if( args.print_confusion_matrix ):
        print( '\n{}{}{}{}'.format( args.delim_prefix ,
                                    fuzzy_flag ,
                                    args.delim ,
                                    type_header_line ) )
    ## Fill in any missing values
    for ref_type in sorted( unique_ref_types ):
        if( ref_type not in confusion_matrix[ fuzzy_flag ] ):
            confusion_matrix[ fuzzy_flag ][ ref_type ] = {}
        for test_type in sorted( unique_test_types ):
            if( test_type not in confusion_matrix[ fuzzy_flag ][ ref_type ] ):
                confusion_matrix[ fuzzy_flag ][ ref_type ][ test_type ] = ''
    ##
    for test_type in sorted( unique_test_types ):
        type_counts = \
          args.delim.join( '{}'.format( confusion_matrix[ fuzzy_flag ][ ref_type ][ test_type ] ) for ref_type in sorted( unique_ref_types ) )
        if( args.print_confusion_matrix ):
            print( '{}{}{}{}'.format( args.delim_prefix ,
                                      test_type ,
                                      args.delim ,
                                      type_counts ) )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def print_score_summary_shell( score_card , file_mapping ,
                               reference_config , test_config ,
                               args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    try:
        for fuzzy_flag in args.fuzzy_flags:
            print_score_summary( score_card ,
                                 file_mapping ,
                                 reference_config , test_config ,
                                 fuzzy_flag = fuzzy_flag ,
                                 args = args )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in print_score_summary:  {}'.format( e ) )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def print_score_summary( score_card , file_mapping ,
                         reference_config , test_config ,
                         fuzzy_flag ,
                         args ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## TODO - refactor score printing to a separate function
    ## TODO - add scores grouped by type
    if( args.write_score_cards ):
        if( args.reference_out == None and
            args.test_out == None ):
            log.warn( 'I could not write the metrics score_card to disk:  --write-score-cards set but neither --reference-out nor --test-out set' )
        else:
            if( args.reference_out ):
                score_card[ fuzzy_flag ].to_csv( '{}/{}{}{}'.format( args.reference_out ,
                                                                   'metrics_' ,
                                                                   fuzzy_flag ,
                                                                   '_score_card.csv' ) ,
                                               sep = '\t' ,
                                               encoding = 'utf-8' ,
                                               index = False )
            if( args.test_out ):
                score_card[ fuzzy_flag ].to_csv( '{}/{}{}{}'.format( args.test_out ,
                                                                   'metrics_' ,
                                                                   fuzzy_flag ,
                                                                   '_score_card.csv' ) ,
                                               sep = '\t' ,
                                               encoding = 'utf-8' ,
                                               index = False )
    ##
    file_list = sorted( file_mapping.keys() )
    ##
    metrics_header_line = \
      args.delim.join( '{}'.format( m ) for m in args.metrics_list )
    if( args.print_metrics ):
        print( '\n{}{}{}{}'.format( args.delim_prefix ,
                                    fuzzy_flag ,
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
                    fuzzy_flag , metrics ,
                    args.delim_prefix , args.delim ,
                    args.print_metrics , args.csv_out )
    ##
    if( args.corpus_out ):
        update_output_dictionary( args.corpus_out ,
                                  [ 'metrics' ,
                                    fuzzy_flag ,
                                    'micro-average' ] ,
                                  args.metrics_list ,
                                  metrics )
    ##
    file_aggregate_metrics = []
    non_empty_metrics = []
    for i in range( len( args.metrics_list ) ):
        file_aggregate_metrics.append( 0 )
        non_empty_metrics.append( 0 )
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
                            fuzzy_flag , metrics ,
                            args.delim_prefix , args.delim ,
                            args.print_metrics , args.csv_out )
            ## Only update macro-average if some annotation in this file exists
            ## in either reference or system output
            for i in range( len( metrics ) ):
                if( metrics[ i ] != None ):
                    non_empty_metrics[ i ] += 1
                    file_aggregate_metrics[ i ] += metrics[ i ]
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
                                fuzzy_flag , metrics ,
                                args.delim_prefix , args.delim ,
                                args.print_metrics , args.csv_out )
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
    macro_averaged_metrics = []
    for key , value , non_empty_count in zip( args.metrics_list ,
                                              file_aggregate_metrics ,
                                              non_empty_metrics ):
        if( non_empty_count == 0 ):
            macro_averaged_metrics.append( args.empty_value )
        elif( key == 'TP' or
              key == 'FP' or
              key == 'FN' or
              key == 'TN' ):
            macro_averaged_metrics.append( value )
        else:
            macro_averaged_metrics.append( value / non_empty_count )
    if( args.by_file or args.by_file_and_type ):
        output_metrics( [ 'macro-averages' , 'macro-average by file' ] ,
                        fuzzy_flag , macro_averaged_metrics ,
                        args.delim_prefix , args.delim ,
                        args.print_metrics , args.csv_out )
    if( args.corpus_out ):
        update_output_dictionary( args.corpus_out ,
                                  [ 'metrics' ,
                                    fuzzy_flag ,
                                    'macro-averages' , 'file' ] ,
                                  args.metrics_list ,
                                  macro_averaged_metrics[ 1: ] )
    ##
    unique_types = Set()
    type_aggregate_metrics = []
    non_empty_metrics = []
    for i in range( len( args.metrics_list ) ):
        type_aggregate_metrics.append( 0 )
        non_empty_metrics.append( 0 )
    for pattern in reference_config:
        if( 'pivot_attr' in pattern.keys() ):
            ## TODO - pull this fron the config file
            for pivot_value in [ 'met' , 'not met' ]: ##pattern[ 'pivot_values' ]:
                this_type = '{} = "{}"'.format( pattern[ 'type' ] , pivot_value )
                unique_types.add( this_type )
        else:
            unique_types.add( pattern[ 'type' ] )
    for unique_type in sorted( unique_types ):
        this_type = ( score_card[ fuzzy_flag ][ 'Type' ] == unique_type )
        type_value_counts = score_card[ fuzzy_flag ][ this_type ][ 'Score' ].value_counts()
        metrics = norm_summary( type_value_counts ,
                                args = args )
        if( args.by_type or args.by_type_and_file ):
            output_metrics( [ 'Type' , unique_type ] ,
                            fuzzy_flag , metrics ,
                            args.delim_prefix , args.delim ,
                            args.print_metrics , args.csv_out )
            ## Only update macro-average if some of this type exist
            ## in either reference or system output
            for i in range( len( metrics ) ):
                if( metrics[ i ] != None ):
                    non_empty_metrics[ i ] += 1
                    type_aggregate_metrics[ i ] += metrics[ i ]
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
                                fuzzy_flag , metrics ,
                                args.delim_prefix , args.delim ,
                                args.print_metrics , args.csv_out )
    macro_averaged_metrics = []
    for key , value , non_empty_count in zip( args.metrics_list ,
                                              type_aggregate_metrics ,
                                              non_empty_metrics ):
        if( non_empty_count == 0 ):
            macro_averaged_metrics.append( args.empty_value )
        elif( key == 'TP' or
              key == 'FP' or
              key == 'FN' or
              key == 'TN' ):
            macro_averaged_metrics.append( value )
        else:
            macro_averaged_metrics.append( value / non_empty_count )
    if( args.by_type or args.by_type_and_file ):
        output_metrics( [ 'macro-averages' , 'macro-average by type' ] ,
                        fuzzy_flag , macro_averaged_metrics ,
                        args.delim_prefix , args.delim ,
                        args.print_metrics , args.csv_out )
    if( args.corpus_out ):
        update_output_dictionary( args.corpus_out ,
                                  [ 'metrics' ,
                                    fuzzy_flag ,
                                    'macro-averages' , 'type' ] ,
                                  args.metrics_list ,
                                  macro_averaged_metrics )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
