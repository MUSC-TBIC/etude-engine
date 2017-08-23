from __future__ import print_function

import sys
import logging as log

import progressbar

import glob
import os
## TODO - use warnings
import warnings

import re
import json

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
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Count annotation occurrences in the test folder
    """
    type_counts = scoring_metrics.new_score_card()
    confusion_matrix = {}
    tests = set([os.path.basename(x) for x in glob.glob( test_folder +
                                                         file_prefix +
                                                         '*' +
                                                         file_suffix )])
    for test_filename in sorted( tests ):
        ## TODO - refactor into separate fuction
        try:
            test_full_path = '{}/{}'.format( test_folder ,
                                             test_filename )
            test_ss = \
              text_extraction.extract_annotations( test_full_path ,
                                                   namespaces = test_ns ,
                                                   patterns = test_patterns )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_annotations:  {}'.format( e ) )
        for test_start in test_ss.keys():
            ## grab type and end position
            test_type = test_ss[ test_start ][ 0 ][ 'type' ]
            test_end = test_ss[ test_start ][ 0 ][ 'end_pos' ]
            type_counts.loc[ type_counts.shape[ 0 ] ] = \
              [ test_filename , test_start , test_end ,
                test_type , None ]
    ##
    try:
        scoring_metrics.print_counts_summary( type_counts ,
                                              sorted( tests ) ,
                                              test_patterns ,
                                              args )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in print_counts_summary:  {}'.format( e ) )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def collect_files( gold_folder , test_folder ,
                   file_prefix , file_suffix ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
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
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return( match_count , file_mapping )


def count_chars_profile( gold_ns , gold_dd , gold_folder ,
                         test_ns , test_dd , test_folder ,
                         args ,
                         file_prefix = '/' ,
                         file_suffix = '.xml' ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Extract a character profile for each document and corpus as a whole.
    """
    try:
        match_count , file_mapping = collect_files( gold_folder , test_folder ,
                                                    file_prefix , file_suffix )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in collect_files:  {}'.format( e ) )
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
    progress = progressbar.ProgressBar( max_value = match_count ,
                                        redirect_stderr = True )
    for gold_filename in progress( sorted( file_mapping.keys() ) ):
        if( args.gold_out == None ):
            gold_out_file = None
        else:
            ## TODO - add filename translation services
            gold_out_file = '{}/{}'.format( args.gold_out ,
                                               gold_filename )
        ##
        try:
            gold_chars = \
              text_extraction.extract_chars( '{}/{}'.format( gold_folder ,
                                                             gold_filename ) ,
                                             namespaces = gold_ns ,
                                             document_data = gold_dd )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_chars:  {}'.format( e ) )
        test_filename = file_mapping[ gold_filename ]
        if( test_filename == None ):
            test_chars = {}
        else:
            if( args.test_out == None ):
                test_out_file = None
            else:
                ## TODO - add filename translation services
                test_out_file = '{}/{}'.format( args.test_out ,
                                                   test_filename )
            ##
            try:
                test_full_path = '{}/{}'.format( test_folder ,
                                                 test_filename )
                test_chars = \
                  text_extraction.extract_chars( test_full_path ,
                                                 namespaces = test_ns ,
                                                 document_data = test_dd )
            except:
                e = sys.exc_info()[0]
                log.error( 'Uncaught exception in extract_chars:  {}'.format( e ) )
        ##
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def align_tokens(  gold_folder ,
                   test_folder ,
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ):
    """
    Align gold and test documents by token for comparison
    """
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
    progress = progressbar.ProgressBar( max_value = match_count ,
                                        redirect_stderr = True )
    for gold_filename in progress( sorted( file_mapping.keys() ) ):
        if( args.gold_out == None ):
            gold_out_file = None
        else:
            ## TODO - add filename translation services
            gold_out_file = '{}/{}'.format( args.gold_out ,
                                            gold_filename )
        ##
        gold_dictionary = {}
        with open( '{}/{}'.format( gold_folder , gold_filename ) , 'r' ) as fp:
            gold_dictionary = json.load( fp )
        text_extraction.align_tokens_on_whitespace( gold_dictionary ,
                                                    gold_out_file )
        test_filename = file_mapping[ gold_filename ]
        if( test_filename != None ):
            if( args.test_out == None ):
                test_out_file = None
            else:
                ## TODO - add filename translation services
                test_out_file = '{}/{}'.format( args.test_out ,
                                                gold_filename )
            ##
            test_dictionary = {}
            with open( '{}/{}'.format( test_folder ,
                                       test_filename ) , 'r' ) as fp:
                test_dictionary = json.load( fp )
            text_extraction.align_tokens_on_whitespace( test_dictionary ,
                                                        test_out_file )
    ##


def score_ref_set( gold_ns , gold_dd , gold_patterns , gold_folder ,
                   test_ns , test_dd , test_patterns , test_folder ,
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Score the test folder against the gold folder.
    """
    score_card = scoring_metrics.new_score_card()
    
    confusion_matrix = {}
    try:
        match_count , file_mapping = collect_files( gold_folder , test_folder ,
                                                    file_prefix , file_suffix )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in collect_files:  {}'.format( e ) )
    ##
    if( match_count == 0 ):
        ## Empty dictionaries evaluate to False so testing bool can tell us if
        ## any gold documents exist
        if( bool( file_mapping ) ):
            log.error( 'No documents found in test directory:  {}'.format( test_folder ) )
        else:
            log.error( 'No documents found in gold directory:  {}'.format( gold_folder ) )
        return( None )
    ##
    progress = progressbar.ProgressBar( max_value = match_count ,
                                        redirect_stderr = True )
    for gold_filename in progress( sorted( file_mapping.keys() ) ):
        if( args.gold_out == None ):
            gold_out_file = None
        else:
            ## TODO - add filename translation services
            gold_out_file = '{}/{}'.format( args.gold_out ,
                                            gold_filename )
        ##
        try:
            gold_full_path = '{}/{}'.format( gold_folder ,
                                             gold_filename )
            gold_om , gold_ss = \
              text_extraction.extract_annotations( gold_full_path ,
                                                   namespaces = gold_ns ,
                                                   document_data = gold_dd ,
                                                   patterns = gold_patterns ,
                                                   ignore_whitespace = \
                                                     args.ignore_whitespace ,
                                                   out_file = gold_out_file )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_annotations:  {}'.format( e ) )
        test_filename = file_mapping[ gold_filename ]
        if( test_filename == None ):
            test_om = {}
            test_ss = {}
        else:
            if( args.test_out == None ):
                test_out_file = None
            else:
                ## TODO - add filename translation services
                test_out_file = '{}/{}'.format( args.test_out ,
                                                test_filename )
            ##
            test_full_path = '{}/{}'.format( test_folder ,
                                             test_filename )
            try:
                test_om , test_ss = \
                  text_extraction.extract_annotations( test_full_path ,
                                                       namespaces = test_ns ,
                                                       document_data = test_dd ,
                                                       patterns = test_patterns ,
                                                       ignore_whitespace = \
                                                         args.ignore_whitespace ,
                                                       out_file = test_out_file )
            except:
                e = sys.exc_info()[0]
                log.error( 'Uncaught exception in extract_annotations:  {}'.format( e ) )
        ##
        try:
            scoring_metrics.evaluate_positions( gold_filename ,
                                                score_card ,
                                                gold_ss ,
                                                test_ss ,
                                                fuzzy_flag = args.fuzzy_flag ,
                                                ignore_whitespace = args.ignore_whitespace )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in evaluate_positions:  {}'.format( e ) )
    ##
    try:
        scoring_metrics.print_score_summary( score_card ,
                                             file_mapping ,
                                             gold_patterns , test_patterns ,
                                             args )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in print_score_summary:  {}'.format( e ) )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


if __name__ == "__main__":
    ##
    args = args_and_configs.get_arguments( sys.argv[ 1: ] )
    ##
    if args.verbose:
        log.basicConfig( format = "%(levelname)s: %(message)s" ,
                         level = log.DEBUG )
        log.info( "Verbose output." )
        log.debug( "{}".format( args ) )
    else:
        log.basicConfig( format="%(levelname)s: %(message)s" )
    ## Initialize the corpuse settings, values, and metrics file
    ## if it was provided at the command line
    if( args.corpus_out ):
        ## Clean out any previous corpus dictionary, in case it exists from
        ## an old run
        with open( args.corpus_out , 'w' ) as fp:
            json.dump( {} , fp , indent = 4 )
        ## Add a few important arguments
        scoring_metrics.update_output_dictionary( args.corpus_out ,
                                                  [ 'args' ] ,
                                                  [ 'gold_config' ,
                                                    'gold_input' ,
                                                    'gold_out' ,
                                                    'test_config' ,
                                                    'test_input' ,
                                                    'test_out' ,
                                                    'score_key' ,
                                                    'fuzzy_flag' ] ,
                                                  [ args.gold_config ,
                                                    args.gold_input ,
                                                    args.gold_out ,
                                                    args.test_config ,
                                                    args.test_input ,
                                                    args.test_out ,
                                                    args.score_key ,
                                                    args.fuzzy_flag ] )
    ## Extract and process the two input file configs
    try:
        gold_ns , gold_dd , gold_patterns = \
          args_and_configs.process_config( config_file = args.gold_config ,
                                           score_key = args.score_key ,
                                           score_values = args.score_values ,
                                           verbose = args.verbose )
        test_ns , test_dd , test_patterns = \
          args_and_configs.process_config( config_file = args.test_config ,
                                           score_key = args.score_key ,
                                           score_values = args.score_values ,
                                           verbose = args.verbose )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in process_config:  {}'.format( e ) )
    ##
    if( args.count_types ):
        try:
            count_ref_set( test_ns = test_ns ,
                           test_patterns = test_patterns ,
                           test_folder = os.path.abspath( args.test_input ) ,
                           args = args ,
                           file_prefix = args.file_prefix ,
                           file_suffix = args.file_suffix[ len( args.file_suffix ) - 1 ].lstrip() )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in count_ref_set:  {}'.format( e ) )
    elif( args.align_tokens ):
        align_tokens( gold_folder = os.path.abspath( args.gold_input ) ,
                      test_folder = os.path.abspath( args.test_input ) ,
                      args = args ,
                      file_prefix = args.file_prefix ,
                      file_suffix = args.file_suffix )
    else:
        try:
            score_ref_set( gold_ns = gold_ns ,
                           gold_dd = gold_dd ,
                           gold_patterns = gold_patterns ,
                           gold_folder = os.path.abspath( args.gold_input ) ,
                           test_ns = test_ns ,
                           test_dd = test_dd ,
                           test_patterns = test_patterns ,
                           test_folder = os.path.abspath( args.test_input ) ,
                           args = args ,
                           file_prefix = args.file_prefix ,
                           file_suffix = args.file_suffix )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in score_ref_set:  {}'.format( e ) )
