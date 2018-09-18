from __future__ import print_function

import sys
import logging as log

from tqdm import tqdm

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

def count_ref_set( this_ns , this_dd , this_patterns ,
                   this_folder , 
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ,
                   set_type = None ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Count annotation occurrences in the test folder
    """
    type_counts = scoring_metrics.new_score_card( fuzzy_flags = [ 'counts' ] )
    file_list = set([os.path.basename(x) for x in glob.glob( this_folder +
                                                             file_prefix +
                                                             '*' +
                                                             file_suffix )])
    ##########################
    for this_filename in tqdm( sorted( file_list ) ,
                               file = args.progressbar_file ,
                               disable = args.progressbar_disabled ):
        try:
            this_full_path = '{}/{}'.format( this_folder ,
                                             this_filename )
            this_om , this_ss = \
              text_extraction.extract_annotations( this_full_path ,
                                                   namespaces = this_ns ,
                                                   document_data = this_dd ,
                                                   patterns = this_patterns ,
                                                   out_file = None )
        except NameError , e:
            log.error( 'NameError exception in extract_annotations:  {}'.format( e ) )
        except TypeError , e:
            log.error( 'TypeError exception in extract_annotations:  {}'.format( e ) )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_annotations:  {}'.format( e ) )
        for this_start in this_ss.keys():
            ## loop over all entries sharing the same start position
            ## and grab type and end position
            for this_entry in this_ss[ this_start ]:
                this_type = this_entry[ 'type' ]
                if( this_start == -1 ):
                    this_end = -1
                    sub_type = this_entry[ 'pivot_value' ]
                    ## TODO - don't force the pivot value into the attribute name
                    this_type = '{} = "{}"'.format( this_type , this_entry[ 'pivot_value' ] )
                else:
                    this_end = this_entry[ 'end_pos' ]
                    sub_type = None
                ##
                ##print( '{}\n'.format( this_type ) )
                scoring_metrics.update_score_card( 'Tally' , type_counts , 'counts' ,
                                                   this_filename , this_start , this_end ,
                                                   this_type , pivot_value = sub_type )

    ##
    if( args.csv_out and
        os.path.exists( args.csv_out ) ):
        os.remove( args.csv_out )
    ##
    try:
        scoring_metrics.print_counts_summary( type_counts ,
                                              sorted( file_list ) ,
                                              this_patterns ,
                                              args ,
                                              set_type = set_type )
    except AttributeError , e:
            log.error( 'AttributeError exception in print_counts_summary:  {}'.format( e ) )
    except KeyError , e:
            log.error( 'KeyError exception in print_counts_summary:  {}'.format( e ) )
    except NameError , e:
            log.error( 'NameError exception in print_counts_summary:  {}'.format( e ) )
    except TypeError , e:
            log.error( 'TypeError exception in print_counts_summary:  {}'.format( e ) )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in print_counts_summary:  {}'.format( e ) )
    #########
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def collect_files( reference_folder , test_folder ,
                   file_prefix , file_suffix ,
                   skip_missing_files_flag ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    file_mapping = {}
    match_count = 0
    ##
    reference_filenames = set([os.path.basename(x) for x in glob.glob( reference_folder +
                                                                       file_prefix +
                                                                       '*' +
                                                                       file_suffix[ 0 ] )])
    for reference_filename in sorted( reference_filenames ):
        if( len( file_suffix ) == 1 ):
            test_filename = reference_filename
        else:
            test_filename = re.sub( file_suffix[ 0 ] + '$' ,
                                    file_suffix[ 1 ] ,
                                    reference_filename )
        if( os.path.exists( '{}/{}'.format( test_folder ,
                                            test_filename ) ) ):
            match_count += 1
            file_mapping[ reference_filename ] = test_filename
        else:
            if( skip_missing_files_flag ):
                    log.debug( "Skipping file because no test equivalent:  {} -/-> {}".format( reference_filename ,
                                                                                               test_filename ) )
            else:
                file_mapping[ reference_filename ] = None
    ##
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return( match_count , file_mapping )


def count_chars_profile( reference_ns , reference_dd , reference_folder ,
                         test_ns , test_dd , test_folder ,
                         args ,
                         file_prefix = '/' ,
                         file_suffix = '.xml' ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Extract a character profile for each document and corpus as a whole.
    """
    try:
        match_count , file_mapping = collect_files( reference_folder , test_folder ,
                                                    file_prefix , file_suffix ,
                                                    args.skip_missing_files )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in collect_files:  {}'.format( e ) )
    ##
    if( match_count == 0 ):
        ## Empty dictionaries evaluate to False so testing bool can tell us if
        ## any reference documents exist
        if( bool( file_mapping ) ):
            print( 'ERROR:  No documents found in test directory:  {}'.format( test_folder ) )
        else:
            print( 'ERROR:  No documents found in reference directory:  {}'.format( reference_folder ) )
        return( None )
    ##
    for reference_filename in tqdm( sorted( file_mapping.keys() ) ,
                                    file = args.progressbar_file ,
                                    disable = args.progressbar_disabled ):
        ##
        reference_out_file = generate_out_file( args.reference_out ,
                                                reference_filename )
        ##
        try:
            reference_chars = \
              text_extraction.extract_chars( '{}/{}'.format( reference_folder ,
                                                             reference_filename ) ,
                                             namespaces = reference_ns ,
                                             document_data = reference_dd )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_chars:  {}'.format( e ) )
        test_filename = file_mapping[ reference_filename ]
        if( test_filename == None ):
            test_chars = {}
        else:
            ##
            test_out_file = generate_out_file( args.test_out ,
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


def align_tokens(  reference_folder ,
                   test_folder ,
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ):
    """
    Align reference and test documents by token for comparison
    """
    match_count , file_mapping = collect_files( reference_folder , test_folder ,
                                                file_prefix , file_suffix ,
                                                args.skip_missing_files )
    ##
    if( match_count == 0 ):
        ## Empty dictionaries evaluate to False so testing bool can tell us if
        ## any reference documents exist
        if( bool( file_mapping ) ):
            print( 'ERROR:  No documents found in test directory:  {}'.format( test_folder ) )
        else:
            print( 'ERROR:  No documents found in reference directory:  {}'.format( reference_folder ) )
        return( None )
    ##
    for reference_filename in tqdm( sorted( file_mapping.keys() ) ,
                                    file = args.progressbar_file ,
                                    disable = args.progressbar_disabled ):
        ##
        reference_out_file = generate_out_file( args.reference_out ,
                                                reference_filename )
        ##
        reference_dictionary = {}
        with open( '{}/{}'.format( reference_folder , reference_filename ) , 'r' ) as fp:
            reference_dictionary = json.load( fp )
        text_extraction.align_tokens_on_whitespace( reference_dictionary ,
                                                    reference_out_file )
        test_filename = file_mapping[ reference_filename ]
        if( test_filename != None ):
            ##
            test_out_file = generate_out_file( args.test_out ,
                                               reference_filename )
            ##
            test_dictionary = {}
            with open( '{}/{}'.format( test_folder ,
                                       test_filename ) , 'r' ) as fp:
                test_dictionary = json.load( fp )
            text_extraction.align_tokens_on_whitespace( test_dictionary ,
                                                        test_out_file )
    ##


def get_file_mapping( reference_folder , test_folder ,
                      file_prefix , file_suffix ,
                      skip_missing_files_flag ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Create mapping between folders to see which files in each set need to be compared
    """
    try:
        match_count , file_mapping = collect_files( reference_folder , test_folder ,
                                                    file_prefix , file_suffix ,
                                                    skip_missing_files_flag )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in collect_files:  {}'.format( e ) )
    ##
    if( match_count == 0 ):
        ## Empty dictionaries evaluate to False so testing bool can tell us if
        ## any reference documents exist
        if( bool( file_mapping ) ):
            log.error( 'No documents found in test directory:  {}'.format( test_folder ) )
        else:
            log.error( 'No documents found in reference directory:  {}'.format( reference_folder ) )
        return( None )
    ##
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return( file_mapping )


def create_output_folders( reference_out , test_out ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Create output folders for saving the results of our analysis
    """
    ##########################
    ## Reference folders
    if( reference_out != None and
        not os.path.exists( reference_out ) ):
        log.warn( 'Creating reference output folder because it does not exist:  {}'.format( reference_out ) )
        try:
            os.makedirs( reference_out )
        except OSError as e:
            log.error( 'OSError caught while trying to create reference output folder:  {}'.format( e ) )
        except IOError as e:
            log.error( 'IOError caught while trying to create reference output folder:  {}'.format( e ) )
    ##########################
    ## Test (system output) folders
    if( test_out != None and
        not os.path.exists( test_out ) ):
        log.warn( 'Creating test output folder because it does not exist:  {}'.format( test_out ) )
        try:
            os.makedirs( test_out )
        except OSError as e:
            log.error( 'OSError caught while trying to create test output folder:  {}'.format( e ) )
        except IOError as e:
            log.error( 'IOError caught while trying to create test output folder:  {}'.format( e ) )
    #########
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def generate_out_file( output_dir , input_filename ):
    """
    Generate a well-formed full file path for writing output stats
    """
    if( output_dir == None ):
        return( None )
    else:
        ## TODO - replace this and all path generation strings with
        ##        OS generic version
        return( '{}/{}'.format( output_dir ,
                                input_filename ) )


def score_ref_set( reference_ns , reference_dd , reference_patterns , reference_folder ,
                   test_ns , test_dd , test_patterns , test_folder ,
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    """
    Score the system output (test) folder against the reference folder.
    """
    score_card = scoring_metrics.new_score_card( fuzzy_flags = \
                                                 args.fuzzy_flags )
    ##
    confusion_matrix = {}
    ##########################
    file_mapping = get_file_mapping( reference_folder , test_folder ,
                                     file_prefix , file_suffix ,
                                     args.skip_missing_files )
    if( file_mapping == None ):
        ## There was a problem mapping files between directories so abort
        return( None )
    ##########################
    create_output_folders( args.reference_out , args.test_out )
    ##########################
    for reference_filename in tqdm( sorted( file_mapping.keys() ) ,
                                    file = args.progressbar_file ,
                                    disable = args.progressbar_disabled ):
        ##
        reference_out_file = generate_out_file( args.reference_out ,
                                                reference_filename )
        ##
        try:
            reference_full_path = '{}/{}'.format( reference_folder ,
                                                  reference_filename )
            reference_om , reference_ss = \
              text_extraction.extract_annotations( reference_full_path ,
                                                   namespaces = reference_ns ,
                                                   document_data = reference_dd ,
                                                   patterns = reference_patterns ,
                                                   skip_chars = args.skip_chars ,
                                                   out_file = reference_out_file )
        except TypeError , e:
            log.error( 'TypeError exception in extract_annotations:  {}'.format( e ) )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_annotations:  {}'.format( e ) )
        test_filename = file_mapping[ reference_filename ]
        if( test_filename == None ):
            test_om = {}
            test_ss = {}
        else:
            ##
            test_out_file = generate_out_file( args.test_out ,
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
                                                       skip_chars = \
                                                         args.skip_chars ,
                                                       out_file = test_out_file )
            except TypeError , e:
                log.error( 'TypeError exception in extract_annotations:  {}'.format( e ) )
            except:
                e = sys.exc_info()[0]
                log.error( 'Uncaught exception in extract_annotations:  {}'.format( e ) )
        ##
        try:
            for fuzzy_flag in args.fuzzy_flags:
                if( args.skip_chars == None ):
                    ignore_chars = False
                else:
                    ignore_chars = True
                scoring_metrics.evaluate_positions( reference_filename ,
                                                    confusion_matrix ,
                                                    score_card ,
                                                    reference_ss ,
                                                    test_ss ,
                                                    fuzzy_flag = fuzzy_flag ,
                                                    use_mapped_chars = \
                                                      ignore_chars ,
                                                    scorable_attributes = \
                                                      args.scorable_attributes )
        except UnboundLocalError , e:
            log.error( 'UnboundLocalError exception in evaluate_positions:  {}'.format( e ) )
        except NameError , e:
            log.error( 'NameError exception in evaluate_positions:  {}'.format( e ) )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in evaluate_positions:  {}'.format( e ) )
    ##
    if( args.csv_out and
        os.path.exists( args.csv_out ) ):
        os.remove( args.csv_out )
    ##
    # scoring_metrics.print_counts_summary_shell( confusion_matrix ,
    #                                             file_mapping ,
    #                                             reference_patterns , test_patterns ,
    #                                             args = args )
    scoring_metrics.print_confusion_matrix_shell( confusion_matrix ,
                                                  file_mapping ,
                                                  reference_patterns , test_patterns ,
                                                  args = args )
    scoring_metrics.print_score_summary_shell( score_card ,
                                               file_mapping ,
                                               reference_patterns , test_patterns ,
                                               args = args )
    #########
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def init_args():
    ##
    args = args_and_configs.get_arguments( sys.argv[ 1: ] )
    ## Set up logging
    if args.verbose:
        log.basicConfig( format = "%(levelname)s: %(message)s" ,
                         level = log.DEBUG )
        log.info( "Verbose output." )
        log.debug( "{}".format( args ) )
    else:
        log.basicConfig( format="%(levelname)s: %(message)s" )
    ## Configure progressbar peformance
    if( args.progressbar_output == 'none' ):
        args.progressbar_disabled = True
        args.progressbar_file = None
    else:
        args.progressbar_disabled = False
        if( args.progressbar_output == 'stderr' ):
            args.progressbar_file = sys.stderr
        elif( args.progressbar_output == 'stdout' ):
            args.progressbar_file = sys.stdout
    ## Resolve conflicts between --ignore-whitespace, --heed-whitespace,
    ## and --ignore-regex flags.  Essentially, if we set something in
    ## skip_chars, use that.  Otherwise, if we tripped --ignore_whitespace
    ## then set skip_chars accordingly
    if( args.ignore_whitespace and
        args.skip_chars == None ):
        args.skip_chars = '[\s]'
    ## lstrip hack added to handle prefixes and suffixes with dashes
    ##   https://stackoverflow.com/questions/16174992/cant-get-argparse-to-read-quoted-string-with-dashes-in-it
    args.file_prefix = args.file_prefix.lstrip()
    args.file_suffix[ 0 ] = args.file_suffix[ 0 ].lstrip()
    if( len( args.file_suffix ) == 2 ):
        args.file_suffix[ 1 ] = args.file_suffix[ 1 ].lstrip()
    ## Initialize the list of annotation attributes to score
    args.attributes_list = []
    args.scorable_attributes = []
    if( isinstance( args.attributes_string , basestring ) ):
        for attribute_key in args.attributes_string.split( ',' ):
            ## Strip off any extra whitespace before processing
            attribute_key = attribute_key.strip()
            attribute_kernel = attribute_key.split( '/' )
            last = len( attribute_kernel ) - 1
            args.attributes_list.append( [ attribute_kernel[ 0 ] ,
                                           attribute_kernel[ last ] ] )
    ## Initialize the corpuse settings, values, and metrics file
    ## if it was provided at the command line
    if( args.corpus_out ):
        ## Clean out any previous corpus dictionary, in case it exists from
        ## an old run
        with open( args.corpus_out , 'w' ) as fp:
            json.dump( {} , fp , sort_keys = True , indent = 4 )
        ## Add a few important arguments
        scoring_metrics.update_output_dictionary( args.corpus_out ,
                                                  [ 'args' ] ,
                                                  [ 'reference_config' ,
                                                    'reference_input' ,
                                                    'reference_out' ,
                                                    'test_config' ,
                                                    'test_input' ,
                                                    'test_out' ,
                                                    'score_key' ,
                                                    'fuzzy_flags' ] ,
                                                  [ args.reference_config ,
                                                    args.reference_input ,
                                                    args.reference_out ,
                                                    args.test_config ,
                                                    args.test_input ,
                                                    args.test_out ,
                                                    args.score_key ,
                                                    args.fuzzy_flags ] )
    return args

if __name__ == "__main__":
    ##
    args = init_args()
    ## Extract and process the two input file configs
    if( args.reference_input ):
        try:
            reference_ns , reference_dd , reference_patterns = \
              args_and_configs.process_config( config_file = args.reference_config ,
                                               score_key = args.score_key ,
                                               score_values = args.score_values ,
                                               collapse_all_patterns = args.collapse_all_patterns ,
                                               verbose = args.verbose )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in process_config for reference config:  {}'.format( e ) )
        if( reference_patterns == [] ):
            log.error( 'No reference patterns extracted from config.  Bailing out now.' )
            exit( 1 )
    if( args.test_input ):
        try:
            test_ns , test_dd , test_patterns = \
              args_and_configs.process_config( config_file = args.test_config ,
                                               score_key = args.score_key ,
                                               score_values = args.score_values ,
                                               collapse_all_patterns = args.collapse_all_patterns ,
                                               verbose = args.verbose )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in process_config for system output config:  {}'.format( e ) )
        if( test_patterns == [] ):
            log.error( 'No test patterns extracted from config.  Bailing out now.' )
            exit( 1 )
    if( args.reference_input and args.test_input ):
        try:
            reference_patterns , test_patterns = \
              args_and_configs.align_patterns( reference_patterns , test_patterns )
            if( len( reference_patterns ) == 0 ):
                log.error( 'Zero annotation patterns found in reference config after filtering against system output config.' )
                exit( 1 )
            if( len( test_patterns ) == 0 ):
                log.error( 'Zero annotation patterns found in system output config after filtering against reference config.' )
                exit( 1 )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in align_patterns:  {}'.format( e ) )
    ##
    if( args.attributes_string is not None ):
        ## TODO - filter the scorable attributes based on just a single
        ##        reference or test input pattern base
        if( args.reference_input and args.test_input ):
            try:
                unique_reference_attributes = \
                  args_and_configs.unique_attributes( reference_patterns )
                unique_test_attributes = \
                  args_and_configs.unique_attributes( test_patterns )
            except AttributeError as e :
                log.error( 'AttributeError in unique_attributes:  {}'.format( e ) )
            except TypeError as e :
                log.error( 'TypeError in unique_attributes:  {}'.format( e ) )
            try:
                if( args.attributes_list == [] ):
                    ## No attributes explicitly listed so we use the intersection
                    ## of listed attributes
                    for attribute in sorted( list( unique_reference_attributes &
                                                   unique_test_attributes ) ):
                        args.scorable_attributes.append( [ attribute , attribute ] )
                else:
                    ## A list type means that a filtered list of attributes were provided
                    ## as arguments to the command line
                    for attribute_pair in args.attributes_list:
                        if( attribute_pair[ 0 ] in unique_reference_attributes and
                            attribute_pair[ 1 ] in unique_test_attributes ):
                            args.scorable_attributes.append( attribute_pair )
                if( len( args.scorable_attributes ) == 0 ):
                    log.error( 'Zero annotation attributes match between the reference and system pattern definitions. Correct your configs or provide mappings between attribute spellings.' )
                    exit( 1 )
            except TypeError as e :
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log.error( 'TypeError in scorable attribute creation (ln {}):  {}'.format( exc_tb.tb_lineno , e ) )
    ##
    if( args.align_tokens ):
        align_tokens( reference_folder = os.path.abspath( args.reference_input ) ,
                      test_folder = os.path.abspath( args.test_input ) ,
                      args = args ,
                      file_prefix = args.file_prefix ,
                      file_suffix = args.file_suffix )
    else:
        ## TODO - make a more efficient loop that will count and/or score in a single pass
        ##        rather than doing a full double pass
        if( args.print_counts ):
            if( args.reference_input ):
                try:
                    count_ref_set( this_ns = reference_ns ,
                                   this_dd = reference_dd ,
                                   this_patterns = reference_patterns ,
                                   this_folder = os.path.abspath( args.reference_input ) ,
                                   args = args ,
                                   file_prefix = args.file_prefix ,
                                   file_suffix = args.file_suffix[ len( args.file_suffix ) - 1 ] ,
                                   set_type = 'reference' )
                except AttributeError , e:
                    log.error( 'AttributeError exception in count_ref_set for reference output corpus:  {}'.format( e ) )
                except KeyError, e:
                    log.error( 'KeyError in count_ref_set for reference output corpus:  {}'.format( e ) )
                except NameError, e:
                    log.error( 'NameError in count_ref_set for reference output corpus:  {}'.format( e ) )
                except TypeError, e:
                    log.error( 'TypeError in count_ref_set for reference output corpus:  {}'.format( e ) )
                except:
                    e = sys.exc_info()[0]
                    log.error( 'Uncaught exception in count_ref_set for reference output corpus:  {}'.format( e ) )
            ##
            if( args.test_input ):
                try:
                    count_ref_set( this_ns = test_ns ,
                                   this_dd = test_dd ,
                                   this_patterns = test_patterns ,
                                   this_folder = os.path.abspath( args.test_input ) ,
                                   args = args ,
                                   file_prefix = args.file_prefix ,
                                   file_suffix = args.file_suffix[ len( args.file_suffix ) - 1 ] ,
                                   set_type = 'test' ) 
                except AttributeError , e:
                    log.error( 'AttributeError exception in count_ref_set for reference output corpus:  {}'.format( e ) )
                except KeyError, e:
                    log.error( 'KeyError in count_ref_set for system output corpus:  {}'.format( e ) )
                except NameError, e:
                    log.error( 'NameError in count_ref_set for system output corpus:  {}'.format( e ) )
                except TypeError, e:
                    log.error( 'TypeError in count_ref_set for system output corpus:  {}'.format( e ) )
                except:
                    e = sys.exc_info()[0]
                    log.error( 'Uncaught exception in count_ref_set for system output corpus:  {}'.format( e ) )

        ##
        if( args.print_confusion_matrix or args.print_metrics ):
            try:
                score_ref_set( reference_ns = reference_ns ,
                               reference_dd = reference_dd ,
                               reference_patterns = reference_patterns ,
                               reference_folder = os.path.abspath( args.reference_input ) ,
                               test_ns = test_ns ,
                               test_dd = test_dd ,
                               test_patterns = test_patterns ,
                               test_folder = os.path.abspath( args.test_input ) ,
                               args = args ,
                               file_prefix = args.file_prefix ,
                               file_suffix = args.file_suffix )
            except NameError, e:
                log.error( 'NameError in score_ref_set:  {}'.format( e ) )
            except:
                e = sys.exc_info()[0]
                log.error( 'Uncaught exception in score_ref_set:  {}'.format( e ) )
