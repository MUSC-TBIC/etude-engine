from __future__ import print_function

import progressbar

import glob
import sys
import os
## TODO - use warnings
import warnings

import re

import numpy as np

import args_and_configs
import scoring_metrics
import text_extraction

#############################################
## helper functions
#############################################

def count_ref_set( test_ns , test_patterns , test_folder ,
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ):
    """
    Count annotation occurrences in the test folder
    """
    type_counts = pd.DataFrame( columns = [ 'File' ,
                                           'Start' , 'End' ,
                                           'Type' , 'Score' ] )
    confusion_matrix = {}
    tests = set([os.path.basename(x) for x in glob.glob( test_folder +
                                                         file_prefix +
                                                         '*' +
                                                         file_suffix )])
    for test_filename in sorted( tests ):
        ## TODO - refactor into separate fuction
        test_ss = \
          text_extraction.extract_annotations( '{}/{}'.format( test_folder ,
                                                               test_filename ) ,
                                               namespaces = test_ns ,
                                               patterns = test_patterns )
        for test_start in test_ss.keys():
            ## grab type and end position
            test_type = test_ss[ test_start ][ 0 ][ 'type' ]
            test_end = test_ss[ test_start ][ 0 ][ 'end_pos' ]
            type_counts.loc[ type_counts.shape[ 0 ] ] = \
              [ test_filename , test_start , test_end ,
                test_type , None ]
    ##
    scoring_metrics.print_counts_summary( type_counts ,
                                          sorted( tests ) ,
                                          test_patterns ,
                                          args )

def collect_files( gold_folder , test_folder ,
                   file_prefix , file_suffix ):
    file_mapping = {}
    match_count = 0
    ##
    golds = set([os.path.basename(x) for x in glob.glob( gold_folder +
                                                         file_prefix +
                                                         '*' +
                                                         file_suffix[ 0 ] )])
    for gold_filename in sorted( golds ):
        if( len( file_suffix ) == 1 ):
            test_filename = gold_filename
        else:
            test_filename = re.sub( file_suffix[ 0 ].lstrip() + '$' ,
                                    file_suffix[ 1 ].lstrip() ,
                                    gold_filename )
        if( os.path.exists( '{}/{}'.format( test_folder ,
                                            test_filename ) ) ):
            match_count += 1
            file_mapping[ gold_filename ] = test_filename
        else:
            ## TODO - log on missing test file
            file_mapping[ gold_filename ] = None
    ##
    return( match_count , file_mapping )


def score_ref_set( gold_ns , gold_patterns , gold_folder ,
                   test_ns , test_patterns , test_folder ,
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ):
    """
    Score the test folder against the gold folder.
    """
    score_card = scoring_metrics.new_score_card()
    
    confusion_matrix = {}
    match_count , file_mapping = collect_files( gold_folder , test_folder ,
                                                file_prefix , file_suffix )
    ##
    if( match_count == 0 ):
        ## Empty dictionaries evaluate to False so testing bool can tell us if
        ## any gold documents exist
        if( bool( file_mapping ) ):
            print( 'ERROR:  No documents found in test directory:  {}'.format( test_folder ) )
        else:
            print( 'ERROR:  No documents found in gold directory:  {}'.format( gold_folder ) )
        return( None )
    ##
    progress = progressbar.ProgressBar( max_value = match_count )
    for gold_filename in progress( sorted( file_mapping.keys() ) ):
        gold_ss = \
          text_extraction.extract_annotations( '{}/{}'.format( gold_folder ,
                                                               gold_filename ) ,
                                               namespaces = gold_ns ,
                                               patterns = gold_patterns )
        test_filename = file_mapping[ gold_filename ]
        if( test_filename == None ):
            test_ss = {}
        else:
            test_ss = \
              text_extraction.extract_annotations( '{}/{}'.format( test_folder ,
                                                                   test_filename ) ,
                                                   namespaces = test_ns ,
                                                   patterns = test_patterns )
        ##
        for gold_start in gold_ss.keys():
            ## grab type and end position
            gold_type = gold_ss[ gold_start ][ 0 ][ 'type' ]
            gold_end = gold_ss[ gold_start ][ 0 ][ 'end_pos' ]
            ##print( '{}'.format( gold_type ) )
            ## Loop through all the gold start positions looking for matches
            if( gold_start in test_ss.keys() ):
                ## grab type and end position
                test_type = test_ss[ gold_start ][ 0 ][ 'type' ]
                test_end = test_ss[ gold_start ][ 0 ][ 'end_pos' ]
                ##print( '{}\t{}'.format( gold_type , test_type ) )
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
            else:
                score_card.loc[ score_card.shape[ 0 ] ] = \
                  [ gold_filename , gold_start , gold_end , gold_type , 'FN' ]
        for test_start in test_ss.keys():
            if( test_start not in gold_ss.keys() ):
                ## grab type and end position
                test_type = test_ss[ test_start ][ 0 ][ 'type' ]
                test_end = test_ss[ test_start ][ 0 ][ 'end_pos' ]
                score_card.loc[ score_card.shape[ 0 ] ] = \
                  [ gold_filename , test_start , test_end , test_type , 'FP' ]
    ##
    scoring_metrics.print_score_summary( score_card ,
                                         sorted( file_mapping.keys() ) ,
                                         gold_patterns , test_patterns ,
                                         args )

if __name__ == "__main__":
    ##
    args = args_and_configs.get_arguments( sys.argv[ 1: ] )
    ## Extract and process the two input file configs
    gold_ns , gold_patterns = \
      args_and_configs.process_config( config_file = args.gold_config ,
                                       score_key = args.score_key )
    test_ns , test_patterns = \
      args_and_configs.process_config( config_file = args.test_config ,
                                       score_key = args.score_key )
    ##
    if( args.count_types ):
        count_ref_set( test_ns = test_ns ,
                       test_patterns = test_patterns ,
                       test_folder = os.path.abspath( args.test_dir ) ,
                       args = args ,
                       file_prefix = args.file_prefix ,
                       file_suffix = args.file_suffix[ len( args.file_suffix ) - 1 ].lstrip() )
    else:
        score_ref_set( gold_ns = gold_ns ,
                       gold_patterns = gold_patterns ,
                       gold_folder = os.path.abspath( args.gold_dir ) ,
                       test_ns = test_ns ,
                       test_patterns = test_patterns ,
                       test_folder = os.path.abspath( args.test_dir ) ,
                       args = args ,
                       file_prefix = args.file_prefix ,
                       file_suffix = args.file_suffix )
