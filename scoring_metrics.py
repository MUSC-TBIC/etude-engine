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
                       ref_annot = None , test_annot = None ,
                       scorable_attributes = None ):
    score_card[ fuzzy_flag ].loc[ score_card[ fuzzy_flag ].shape[ 0 ] ] = \
      [ filename , start_pos , end_pos ,
        type , pivot_value , condition ]
    if( condition != 'TP' or scorable_attributes == None ):
        return
    for attribute in scorable_attributes:
        ## Skip entries for which the attribute wasn't extracted in
        ## either the ref or system annotation
        if( attribute not in ref_annot.keys() or
            attribute not in test_annot.keys() ):
            continue
        if( ref_annot[ attribute ] == test_annot[ attribute ] ):
            if( ref_annot[ attribute ] == 'true' ):
                score_card[ fuzzy_flag ].loc[ score_card[ fuzzy_flag ].shape[ 0 ] ] = \
                    [ filename , start_pos , end_pos ,
                      type , attribute , 'TP' ]
            else:
                score_card[ fuzzy_flag ].loc[ score_card[ fuzzy_flag ].shape[ 0 ] ] = \
                    [ filename , start_pos , end_pos ,
                      type , attribute , 'TN' ]
        elif( ref_annot[ attribute ] == 'true' ):
            score_card[ fuzzy_flag ].loc[ score_card[ fuzzy_flag ].shape[ 0 ] ] = \
                [ filename , start_pos , end_pos ,
                  type , attribute , 'FN' ]
        else:
            score_card[ fuzzy_flag ].loc[ score_card[ fuzzy_flag ].shape[ 0 ] ] = \
                [ filename , start_pos , end_pos ,
                  type , attribute , 'FP' ]


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
                                   test_annot = test_annot ,
                                   ## TODO - replace with passed variable
                                   scorable_attributes = [ 'conditional' , 'generic' , 'historical' ,
                                                           'negated' , 'not_patient' , 'uncertain' ] )
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


def end_comparison_runner( reference_filename , confusion_matrix , score_card , 
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
        if( reference_end == test_end or
            ( reference_end != 'EOF' and
              test_end != 'EOF' and
              reference_end >= test_end - 1 and
              reference_end <= test_end + 1 ) ):
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
    ## End offset matching is special and gets run alone
    if( fuzzy_flag == 'end' ):
        reference_matched, test_leftovers = end_comparison_runner( reference_filename ,
                                                                   confusion_matrix ,
                                                                   score_card , 
                                                                   reference_annot ,
                                                                   test_entries ,
                                                                   start_key , end_key ,
                                                                   fuzzy_flag )
        return( reference_matched , test_leftovers )
    ## The other three types of matching care compatible and can be
    ## run together
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

def document_level_annot_comparison_runner( reference_filename , confusion_matrix , score_card , 
                                            reference_annot , 
                                            test_entries ,
                                            fuzzy_flag ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ##
    reference_type = reference_annot[ 'type' ]
    reference_pivot_value = reference_annot[ 'pivot_value' ]
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
        ##
        test_type = test_annot[ 'type' ]
        test_pivot_value = test_annot[ 'pivot_value' ]
        if( test_type == None ):
            ## If we couldn't extract a type, consider this
            ## an invalid annotation
            continue
        if( reference_type == test_type ):
            matched_flag = True
            this_type = '{} = "{}"'.format( reference_type , reference_pivot_value )
            that_type = '{} = "{}"'.format( test_type , test_pivot_value )
            update_confusion_matrix( confusion_matrix , fuzzy_flag , this_type , that_type )
            ## If the pivot_values match...
            if( reference_pivot_value == test_pivot_value ):
                update_score_card( 'TP' , score_card , fuzzy_flag ,
                                   reference_filename , -1 , -1 ,
                                   this_type , pivot_value = reference_pivot_value )
            else:
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , -1 , -1 ,
                                   this_type , pivot_value = reference_pivot_value )
                update_score_card( 'FP' , score_card , fuzzy_flag ,
                                   reference_filename , -1 , -1 ,
                                   that_type , pivot_value = test_pivot_value )
        else:
            test_leftovers.append( test_annot )
    return( matched_flag , test_leftovers )


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
    reference_entries_doc_level = []
    test_entries_doc_level = []
    ##
    for reference_annot in reference_entries:
        ## grab type and end position
        reference_type , reference_start , reference_end = \
              get_annotation_from_base_entry( reference_annot ,
                                              start_key ,
                                              end_key )
        if( reference_start == -1 ):
            ## A start_key of -1 means that this an a document level
            ## annotation and should be scored elsewhere
            reference_entries_doc_level.append( reference_annot )
            continue
        reference_matched , test_leftovers = \
          reference_annot_comparison_runner( reference_filename , confusion_matrix , score_card ,
                                             reference_annot ,
                                             test_entries ,
                                             start_key , end_key ,
                                             fuzzy_flag )
        test_entries = test_leftovers
        if( not reference_matched ):
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
        if( test_start == -1 ):
            ## A start_key of -1 means that this an a document level
            ## annotation and should be scored elsewhere
            test_entries_doc_level.append( test_annot )
            continue
        update_confusion_matrix( confusion_matrix , fuzzy_flag , '*FP*' , test_type )
        update_score_card( 'FP' , score_card , fuzzy_flag ,
                           reference_filename , test_start , test_end ,
                           test_type , None , test_annot )
    ##
    ## When there are document level annotations, we loop over the entries
    ## again to score them using a different algorithm
    test_entries = test_entries_doc_level
    test_leftovers = test_entries
    for reference_annot in reference_entries_doc_level:
        reference_matched , test_leftovers = \
          document_level_annot_comparison_runner( reference_filename , confusion_matrix , score_card ,
                                                  reference_annot ,
                                                  test_entries ,
                                                  fuzzy_flag )
        test_entries = test_leftovers
        if( not reference_matched ):
            ## grab type and end position
            reference_type = reference_annot[ 'type' ]
            reference_pivot = reference_annot[ 'pivot_value' ]
            this_type = '{} = "{}"'.format( reference_type , reference_pivot )
            if( reference_type != None ):
                update_confusion_matrix( confusion_matrix , fuzzy_flag , reference_type , '*FN*' )
                update_score_card( 'FN' , score_card , fuzzy_flag ,
                                   reference_filename , reference_start , reference_end ,
                                   reference_type ,
                                   pivot_value = reference_pivot ,
                                   ref_annot = reference_annot ,
                                   test_annot = None )
    ## any remaining entries in the reference set are FNs
    for test_annot in test_leftovers:
        ##
        test_type = test_annot[ 'type' ]
        test_pivot = test_annot[ 'pivot_value' ]
        if( test_type == None ):
            continue
        that_type = '{} = "{}"'.format( test_type , test_pivot )        
        update_confusion_matrix( confusion_matrix , fuzzy_flag , '*FP*' , that_type )
        update_score_card( 'FP' , score_card , fuzzy_flag ,
                           reference_filename , -1 , -1 ,
                           that_type , pivot_value = test_pivot ,
                           ref_annot = None , test_annot = test_annot )
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
                   sort_keys = True , indent = 4 )
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
                    stdout_flag , csv_out_filename ,
                    pretty_print_flag ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( len( class_data ) == 1 ):
        row_name = class_data[ 0 ]
    elif( len( class_data ) == 2 ):
        row_name = class_data[ 1 ]
    elif( len( class_data ) == 4 ):
        row_name = '{} x {}'.format( class_data[ 1 ] ,
                                     class_data[ 3 ] )
    ##
    row_content = delimiter.join( '{}'.format( m ) for m in metrics )
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
    if( stdout_flag ):
        if( not pretty_print_flag ) :
            print( '{}{}{}{}'.format( delimiter_prefix , row_name , delimiter , row_content ) )
        else:
            pretty_row = '{0}{1:30s}'.format( delimiter_prefix , row_name )
            for i in range( 0 , len( metrics ) ):
                if( metrics[ i ] is None ):
                    pretty_row = '{}{}{:9s}'.format( pretty_row , delimiter ,
                                                     '' )
                elif( metrics[ i ] == 0 ):
                    pretty_row = '{}{}{:9d}'.format( pretty_row , delimiter ,
                                                     0 )
                elif( metrics[ i ] == int( metrics[ i ] ) ):
                    pretty_row = '{}{}{:9d}'.format( pretty_row , delimiter ,
                                                      int( metrics[ i ] ) )
                else:
                    pretty_row = '{}{}{:9.4f}'.format( pretty_row , delimiter ,
                                                       metrics[ i ] )
            print( pretty_row )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def get_unique_types( config ):
    unique_types = Set()
    for pattern in config:
        if( 'pivot_attr' in pattern.keys() ):
            ## TODO - pull this fron the config file
            for pivot_value in [ 'met' , 'not met' ]: ##pattern[ 'pivot_values' ]:
                this_type = '{} = "{}"'.format( pattern[ 'type' ] , pivot_value )
                unique_types.add( this_type )
        else:
            unique_types.add( pattern[ 'type' ] )
    ##
    return( unique_types )


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
                    args.print_counts , args.csv_out ,
                    args.pretty_print )
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
                            args.print_counts , args.csv_out ,
                            args.pretty_print )
        ##
        if( args.by_file_and_type ):
            unique_types = get_unique_types( config_patterns )
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
                output_metrics( [ 'File' , filename , 'Type' , unique_type ] ,
                                'counts' , metrics ,
                                args.delim_prefix , args.delim ,
                                args.print_counts , args.csv_out ,
                                args.pretty_print )
    ##
    unique_types = get_unique_types( config_patterns )
    type_aggregate_metrics = None
    non_empty_types = 0
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
                            args.print_counts , args.csv_out ,
                            args.pretty_print )
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
                                args.print_counts , args.csv_out ,
                                args.pretty_print )
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
    except TypeError , e :
        log.error( 'TypeError in print_score_summary:  {}'.format( e ) )
    except NameError , e :
        log.error( 'NameError in print_score_summary:  {}'.format( e ) )
    except AttributeError , e :
        log.error( 'AttributeError in print_score_summary:  {}'.format( e ) )
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
    ################
    ## major classes to loop over
    file_list = sorted( file_mapping.keys() )
    unique_types = get_unique_types( reference_config )
    unique_pivots = [ 'conditional' , 'generic' , 'historical' ,
                      'negated' , 'not_patient' , 'uncertain' ] #TODO - get_unique_attributes( reference_config )
    #########################################
    ## by file
    #########################################
    metrics_header_line = \
      args.delim.join( '{}'.format( m ) for m in args.metrics_list )
    if( args.csv_out and
        not os.path.exists( args.csv_out ) ):
        update_csv_output( args.csv_out , args.delim ,
                           [ 'FuzzyFlag' ,
                             'ClassType' , 'Class' ,
                             'SubClassType' , 'SubClass' ,
                             metrics_header_line ] )
    max_table_width = 0
    if( args.print_metrics ):
        if( not args.pretty_print ):
            print( '\n{}{}{}{}'.format( args.delim_prefix ,
                                        fuzzy_flag ,
                                        args.delim ,
                                        metrics_header_line ) )
        else:
            pretty_row = '{0}{1:^30s}'.format( args.delim_prefix , fuzzy_flag )
            for m in args.metrics_list:
                if( len( m ) > 9 ):
                    m = m[:9]
                pretty_row = '{}{}{:^9s}'.format( pretty_row , args.delim , m )
            ## TODO - table width is inaccurate when \t occurs anywhere in the --delim
            max_table_width = len( pretty_row )
            print( "\n" + pretty_row )
            print( "=" * max_table_width )
    ##
    pivotless_entries = ( score_card[ fuzzy_flag ][ 'Pivot' ].isnull() )
    metrics = norm_summary( score_card[ fuzzy_flag ][ pivotless_entries ][ 'Score' ].value_counts() ,
                            args = args )
    output_metrics( [ 'micro-average' ] ,
                    fuzzy_flag , metrics ,
                    args.delim_prefix , args.delim ,
                    args.print_metrics , args.csv_out ,
                    args.pretty_print )
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
    if( args.by_file or args.by_file_and_type ):
        for filename in file_list:
            if( args.corpus_out ):
                update_output_dictionary( args.corpus_out ,
                                          [ 'file-mapping' ] ,
                                          [ filename ] ,
                                          [ file_mapping[ filename ] ] )
                this_file = ( ( score_card[ fuzzy_flag ][ 'Pivot' ].isnull() ) &
                              ( score_card[ fuzzy_flag ][ 'File' ] == filename ) )
                file_value_counts = score_card[ fuzzy_flag ][ this_file ][ 'Score' ].value_counts()
                metrics = norm_summary( file_value_counts , args = args )
                if( args.by_file or args.by_file_and_type ):
                    output_metrics( [ 'File' , filename ] ,
                                    fuzzy_flag , metrics ,
                                    args.delim_prefix , args.delim ,
                                    args.print_metrics , args.csv_out ,
                                    args.pretty_print )
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
            for unique_type in sorted( unique_types ):
                this_type = \
                  (  ( score_card[ fuzzy_flag ][ 'Pivot' ].isnull() ) &
                     ( score_card[ fuzzy_flag ][ 'File' ] == filename ) &
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
                                    args.print_metrics , args.csv_out ,
                                    args.pretty_print )
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
                            args.print_metrics , args.csv_out ,
                            args.pretty_print )
        if( args.corpus_out ):
            update_output_dictionary( args.corpus_out ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'macro-averages' , 'file' ] ,
                                      args.metrics_list ,
                                      macro_averaged_metrics[ 1: ] )
    #########################################
    ## by type
    #########################################
    if( args.by_type or args.by_type_and_file ):
        unique_types = get_unique_types( reference_config )
        type_aggregate_metrics = []
        non_empty_metrics = []
        for i in range( len( args.metrics_list ) ):
            type_aggregate_metrics.append( 0 )
            non_empty_metrics.append( 0 )
        for unique_type in sorted( unique_types ):
            this_type = ( ( score_card[ fuzzy_flag ][ 'Pivot' ].isnull() ) &
                          ( score_card[ fuzzy_flag ][ 'Type' ] == unique_type ) )
            type_value_counts = score_card[ fuzzy_flag ][ this_type ][ 'Score' ].value_counts()
            metrics = norm_summary( type_value_counts ,
                                    args = args )
            if( args.by_type or args.by_type_and_file ):
                output_metrics( [ 'Type' , unique_type ] ,
                                fuzzy_flag , metrics ,
                                args.delim_prefix , args.delim ,
                                args.print_metrics , args.csv_out ,
                                args.pretty_print )
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
            #################################
            ## by type and file
            #################################
            if( args.by_type_and_file ):
                for filename in file_list:
                    this_file = \
                      (  ( score_card[ fuzzy_flag ][ 'Pivot' ].isnull() ) &
                         ( score_card[ fuzzy_flag ][ 'File' ] == filename ) &
                         ( score_card[ fuzzy_flag ][ 'Type' ] == unique_type ) )
                    file_value_counts = \
                      score_card[ fuzzy_flag ][ this_file ][ 'Score' ].value_counts()
                    metrics = \
                      norm_summary( file_value_counts ,
                                    args = args )
                    output_metrics( [ 'Type' , unique_type ,
                                      'File' , filename ] ,
                                    fuzzy_flag , metrics ,
                                    args.delim_prefix , args.delim ,
                                    args.print_metrics , args.csv_out ,
                                    args.pretty_print )
            #################################
            ## by type and attribute
            #################################
            if( args.by_type_and_attribute ):
                for unique_pivot in sorted( unique_pivots ):
                    this_pivot = \
                      (  ( score_card[ fuzzy_flag ][ 'Pivot' ] == unique_pivot ) &
                         ( score_card[ fuzzy_flag ][ 'Type' ] == unique_type ) )
                    pivot_value_counts = \
                      score_card[ fuzzy_flag ][ this_pivot ][ 'Score' ].value_counts()
                    metrics = \
                      norm_summary( pivot_value_counts ,
                                    args = args )
                    output_metrics( [ 'Type' , unique_type ,
                                      'Pivot' , unique_pivot ] ,
                                    fuzzy_flag , metrics ,
                                    args.delim_prefix , args.delim ,
                                    args.print_metrics , args.csv_out ,
                                    args.pretty_print )
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
                            args.print_metrics , args.csv_out ,
                            args.pretty_print )
        if( args.corpus_out ):
            update_output_dictionary( args.corpus_out ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'macro-averages' , 'type' ] ,
                                      args.metrics_list ,
                                      macro_averaged_metrics )
    #########################################
    ## by attribute
    #########################################
    if( args.by_attribute ):
        pivot_aggregate_metrics = []
        non_empty_metrics = []
        for i in range( len( args.metrics_list ) ):
            pivot_aggregate_metrics.append( 0 )
            non_empty_metrics.append( 0 )
        for unique_pivot in sorted( unique_pivots ):
            this_pivot = ( ( score_card[ fuzzy_flag ][ 'Pivot' ] == unique_pivot ) )
            pivot_value_counts = score_card[ fuzzy_flag ][ this_pivot ][ 'Score' ].value_counts()
            metrics = norm_summary( pivot_value_counts ,
                                    args = args )
            output_metrics( [ 'Pivot' , unique_pivot ] ,
                            fuzzy_flag , metrics ,
                            args.delim_prefix , args.delim ,
                            args.print_metrics , args.csv_out ,
                            args.pretty_print )
            ## Only update macro-average if some of this pivot exist
            ## in either reference or system output
            for i in range( len( metrics ) ):
                if( metrics[ i ] != None ):
                    non_empty_metrics[ i ] += 1
                    pivot_aggregate_metrics[ i ] += metrics[ i ]
            if( args.corpus_out ):
                update_output_dictionary( args.corpus_out ,
                                          [ 'metrics' ,
                                            fuzzy_flag ,
                                            'by-pivot' , unique_pivot ] ,
                                          args.metrics_list ,
                                          metrics )
            ##
            ## TODO - by pivot by file
            ## TODO - by pivot by type
        macro_averaged_metrics = []
        for key , value , non_empty_count in zip( args.metrics_list ,
                                                  pivot_aggregate_metrics ,
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
        if( len( unique_pivots ) > 0 ):
            output_metrics( [ 'macro-averages' , 'macro-average by pivot' ] ,
                            fuzzy_flag , macro_averaged_metrics ,
                            args.delim_prefix , args.delim ,
                            args.print_metrics , args.csv_out ,
                            args.pretty_print )
        if( args.corpus_out ):
            update_output_dictionary( args.corpus_out ,
                                      [ 'metrics' ,
                                        fuzzy_flag ,
                                        'macro-averages' , 'pivot' ] ,
                                      args.metrics_list ,
                                      macro_averaged_metrics )
    #########
    log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
