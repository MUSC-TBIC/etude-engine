import sys
import logging as log

import re

import argparse
import ConfigParser

def initialize_arg_parser():
    parser = argparse.ArgumentParser( description = """
ETUDE (Evaluation Tool for Unstructured Data and Extractions) is a
command line tool for scoring and evaluating unstructured data tagging and
unstructured data extraction.
""" )
    parser.add_argument( '-v' , '--verbose' ,
                         help = "print more information" ,
                         action = "store_true" )

    parser.add_argument( '--progressbar-output' ,
                         dest = 'progressbar_output' ,
                         default = 'stderr' ,
                         choices = [ 'stderr' , 'stdout' , 'none' ] ,
                         help = "Pipe the progress bar to stderr, stdout, or neither" )
    
    ## TODO -
    ## --sample % of files to randomly sample from
    ## --head X grab the first files from the directory
    ## --tail Y grab the last files from the directory
    ## --file-pattern "" regex pattern fed to glob for selecting files
    ##                   (maybe call this --file-filter?)
    
    parser.add_argument( '--reference-input' , default = None ,
                         dest = "reference_input",
                         help = "Directory containing reference reference set" )
    parser.add_argument( '--test-input' , default = None ,
                        dest = "test_input",
                        help = "Directory containing reference set to score" )

    ## TODO - add special hook for include all metrics
    parser.add_argument( "-m" , "--metrics" , nargs = '+' ,
                         dest = 'metrics_list' ,
                         default = [ 'TP' , 'FP' , 'TN' , 'FN' ] ,
                         choices = [ 'TP' , 'FP' , 'TN' , 'FN' ,
                                     'Precision' ,
                                     'Recall' , 'Sensitivity' ,
                                     'Specificity' ,
                                     'Accuracy' ,
                                     'F1' ] ,
                         help = "List of metrics to return, in order" )
    
    parser.add_argument( '--empty-value' ,
                         dest = 'empty_value' ,
                         default = '' ,
                         help = "Value to print when metrics are undefined or values are null" )

    parser.add_argument( "--fuzzy-match-flags" , nargs = "+" ,
                         dest = 'fuzzy_flags' ,
                         default = [ 'exact' ] ,
                         choices = [ 'exact' , 'fully-contained' , 'partial' ] ,
                         help = "List of strictness levels to use in matching offsets." )

    parser.add_argument( "-d" , "--delim" , 
                        dest = 'delim' ,
                        default = '\t' ,
                        help="Delimiter used in all output streams" )

    parser.add_argument( "--delim-prefix" , 
                        dest = 'delim_prefix' ,
                        default = '' ,
                        help="Prefix string printed before each line in the output streams" )

    parser.add_argument( '--by-file' , dest = 'by_file' ,
                         help = "Print metrics by file" ,
                         action = "store_true" )
    parser.add_argument( '--by-file-and-type' , dest = 'by_file_and_type' ,
                         help = "Print metrics by type nested within file" ,
                         action = "store_true" )
    
    parser.add_argument( '--by-type' , dest = 'by_type' ,
                         help = "Print metrics by annotation type" ,
                         action = "store_true" )
    parser.add_argument( '--by-type-and-file' , dest = 'by_type_and_file' ,
                         help = "Print metrics by file nested within annotation type" ,
                         action = "store_true" )

    parser.add_argument( "--reference-config", 
                         dest = 'reference_config' ,
                         default = 'config/i2b2_2016_track-1.conf' ,
                         help = 'Configuration file that describes the reference format' )
    parser.add_argument("--test-config", 
                        dest = 'test_config' ,
                        default = 'config/i2b2_2016_track-1.conf' ,
                        help="Configuration file that describes the test format" )

    parser.add_argument("--score-key", 
                        dest = 'score_key' ,
                        default = 'Short Name' ,
                        help="Configuration file key used as the join key for matching patterns in scoring" )

    parser.add_argument("--score-values", nargs = '+' ,
                        dest = 'score_values' ,
                        default = [ '.*' ] ,
                        help="List of values associated with the score key to count in scoring" )

    parser.add_argument( '--collapse-all-patterns' ,
                         help = "Treat all patterns extracted as of the same type" ,
                         action = "store_true" )

    parser.add_argument("--file-prefix", 
                        dest = 'file_prefix' ,
                        default = '/' ,
                        help="Prefix used for filename matching" )
    ## TODO - lstrip hack added to handle suffixes with dashes
    ##   https://stackoverflow.com/questions/16174992/cant-get-argparse-to-read-quoted-string-with-dashes-in-it
    parser.add_argument("--file-suffix", nargs = '+' ,
                        dest = 'file_suffix' ,
                        default = [ '.xml' ] ,
                        help="Suffix used for filename matching.  You can provide a second argument if the test file suffixes don't match the reference file suffixes. The span of the reference filename that matches the file suffix will be replaced with the contents of the second suffix string.  This replacement is useful when the reference and test differ in terms of file endings (e.g., '001.txt' -> '001.xmi')" )

    parser.add_argument( '--reference-out' ,
                         dest = 'reference_out' ,
                         default = None ,
                         help = 'When provided, write the dictionary of extracted reference annotations to disk in this directory' )
    
    parser.add_argument( '--test-out' ,
                         dest = 'test_out' ,
                         default = None ,
                         help = 'When provided, write the dictionary of extracted test annotations to disk in this directory' )
    
    parser.add_argument( '--corpus-out' ,
                         dest = 'corpus_out' ,
                         default = None ,
                         help = 'When provided, write the dictionary of extracted corpus metrics to disk in this file (JSON)' )
    
    parser.add_argument( '--csv-out' ,
                         dest = 'csv_out' ,
                         default = None ,
                         help = 'When provided, write the dictionary of extracted corpus metrics to disk in this file (Uses -d delimiter)' )
    
    parser.add_argument( '--print-counts' , default = False ,
                         dest = 'print_counts' ,
                         help = "Print to stdout the count of annotation types in each file" ,
                         action = "store_true" )
    
    parser.add_argument( '--no-counts' ,
                         dest = 'print_counts' ,
                         help = "Suppress the count of annotation types in each file" ,
                         action = "store_false" )
    
    parser.add_argument( '--print-confusion-matrix' , default = False ,
                         dest = 'print_confusion_matrix' ,
                         help = "Print to stdout the confusion matrix between annotation types" ,
                         action = "store_true" )
    
    parser.add_argument( '--write-score-cards' , default = False ,
                         dest = 'write_score_cards' ,
                         help = "Write to disk the internal data structure used for counting annotations" ,
                         action = "store_true" )
    
    parser.add_argument( '--no-confusion-matrix' ,
                         dest = 'print_confusion_matrix' ,
                         help = "Suppress the confusion matrix between annotation types" ,
                         action = "store_false" )
    
    parser.add_argument( '--print-metrics' , default = True ,
                         dest = 'print_metrics' ,
                         help = "Print to stdout the metrics (provided via --metrics-list) scored" ,
                         action = "store_true" )

    parser.add_argument( '--no-metrics' ,
                         dest = 'print_metrics' ,
                         help = "Suppress the metrics (provided via --metrics-list) scored" ,
                         action = "store_false" )

    parser.add_argument( '--align-tokens' ,
                         dest = 'align_tokens' ,
                         help = "Generate a token-aligned corpus" ,
                         action = "store_true" )

    parser.add_argument( '--ignore-whitespace' ,
                         default = True ,
                         dest = 'ignore_whitespace' ,
                         help = "Create an offset mapping from the raw document that ignores whitespaces in the offset index (Turned on by default; the counter argument to --heed-whitespace)" ,
                         action = "store_true" )
    
    parser.add_argument( '--skip-chars' ,
                         dest = 'skip_chars' ,
                         default = None ,
                         help = "A configurable variant of --ignore-whitespace. The provided regex determines all characters to be ignored in the offset indices." )
    
    parser.add_argument( '--heed-whitespace' ,
                         dest = 'ignore_whitespace' ,
                         help = "Include all whitespace in the offset mapping from the raw document (the counter argument to --ignore-whitespace)" ,
                         action = "store_false" )

    parser.add_argument( '--skip-missing-files' ,
                         default = True ,
                         dest = 'skip_missing_files' ,
                         help = "Don't analyze or score a reference file if the equivalent system output file is missing (Turned on by default; the counter argument to --score-missing-files)" ,
                         action = "store_true" )
    
    parser.add_argument( '--score-missing-files' ,
                         dest = 'skip_missing_files' ,
                         help = "Score all reference files even if the equivalent system output file can't be found (the counter argument to --skip-missing-files)" ,
                         action = "store_false" )
    ##
    return parser


def get_arguments( command_line_args ):
    parser = initialize_arg_parser()
    args = parser.parse_args( command_line_args )
    if( args.print_counts and
        args.reference_input is None and
        args.test_input is None ):
        parser.error( "At least one of --reference-input and --test-input are required when using --print-counts." )
    if( ( args.print_metrics or args.print_confusion_matrix ) and
        ( args.reference_input is None or args.test_input is None ) ):
        parser.error( "Both --reference-input and --test-input are required for printing metrics and printing a confusion matrix." )
    ##
    return args

def extract_namespaces( namespaces ,
                        config , sect ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    for ns , value in config.items( sect ):
        namespaces[ ns ] = value
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return namespaces


def extract_document_data( document_data ,
                           config , sect ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( config.has_option( sect , 'Format' ) ):
        document_data[ 'format' ] = config.get( sect , 'Format' )
    else:
        document_data[ 'format' ] = 'Unknown'
    if( config.has_option( sect , 'Content XPath' ) ):
        if( config.has_option( sect , 'Content Attribute' ) ):
            document_data[ 'tag_xpath' ] = config.get( sect ,
                                                       'Content XPath' )
            document_data[ 'content_attribute' ] = config.get( sect ,
                                                               'Content Attribute' )
        else:
            document_data[ 'cdata_xpath' ] = config.get( sect ,
                                                         'Content XPath' )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return document_data


def extract_xpath_patterns( annotations ,
                            config , sect ,
                            display_name ,
                            key_value ,
                            score_values ,
                            collapse_all_patterns = False ,
                            verbose = False ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## Loop through all the provided score_values to see if any
    ## provided values match the currently extracted value
    for score_value in score_values:
        if( re.search( score_value , key_value ) ):
            if( collapse_all_patterns ):
                type_value = 'All Patterns'
            else:
                type_value = key_value
            pattern_entry = dict( type = type_value ,
                                  long_name = sect.strip() ,
                                  xpath = config.get( sect , 'XPath' ) ,
                                  display_name = display_name ,
                                  short_name = config.get( sect ,
                                                           'Short Name' ) ,
                                  begin_attr = config.get( sect ,
                                                           'Begin Attr' ) ,
                                  end_attr = config.get( sect ,
                                                         'End Attr' ) ,
                                  optional_attributes = [] )
            if( config.has_option( sect , 'Opt Attr' ) ):
                optional_attributes = config.get( sect , 'Opt Attr' )
                pattern_entry[ 'optional_attributes' ] = \
                  optional_attributes.split( ',' )
            annotations.append( pattern_entry )
            break
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def extract_delimited_patterns( annotations ,
                                config , sect ,
                                display_name ,
                                key_value ,
                                score_values ,
                                verbose = False ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## Loop through all the provided score_values to see if any
    ## provided values match the currently extracted value
    for score_value in score_values:
        if( re.search( score_value , key_value ) ):
            annotations.append( dict( type = key_value ,
                                      long_name = sect.strip() ,
                                      delimiter = config.get( sect ,
                                                              'Delimiter' ) ,
                                      display_name = display_name ,
                                      short_name = config.get( sect ,
                                                               'Short Name' ) ) )
            break
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def extract_brat_patterns( annotations ,
                           config , sect ,
                           display_name ,
                           key_value ,
                           score_values ,
                           verbose = False ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ## Loop through all the provided score_values to see if any
    ## provided values match the currently extracted value
    for score_value in score_values:
        if( re.search( score_value , key_value ) ):
            pattern_entry = dict( type = key_value ,
                                  long_name = sect.strip() ,
                                  type_prefix = config.get( sect ,
                                                            'Type Prefix' ) ,
                                  display_name = display_name ,
                                  short_name = config.get( sect ,
                                                           'Short Name' ) )
            if( config.has_option( sect , 'Opt Attr' ) ):
                optional_attributes = config.get( sect , 'Opt Attr' )
                pattern_entry[ 'optional_attributes' ] = \
                  optional_attributes.split( ',' )
            annotations.append( pattern_entry )
            break
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def extract_patterns( annotations ,
                      config , sect ,
                      score_key ,
                      score_values ,
                      collapse_all_patterns = False ,
                      verbose = False ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( collapse_all_patterns ):
        display_name = 'All Patterns'
    else:
        display_name = '{} ({})'.format( sect.strip() ,
                                         config.get( sect , 'Short Name' ) )
    if( score_key == 'Long Name' or
        score_key == 'Section' ):
        key_value = sect.strip()
    else:
        key_value = config.get( sect , score_key )
    if( config.has_option( sect , 'XPath' ) and
        config.has_option( sect , 'Begin Attr' ) and
        config.has_option( sect , 'End Attr' ) ):
        try:
            extract_xpath_patterns( annotations ,
                                    config , sect ,
                                    display_name ,
                                    key_value ,
                                    score_values ,
                                    collapse_all_patterns ,
                                    verbose )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_xpath_patterns:  {}'.format( e ) )
    elif( config.has_option( sect , 'Delimiter' ) ):
        extract_delimited_patterns( annotations ,
                                    config , sect ,
                                    display_name ,
                                    key_value ,
                                    score_values ,
                                    verbose )
    elif( config.has_option( sect , 'Type Prefix' ) ):
        extract_brat_patterns( annotations ,
                               config , sect ,
                               display_name ,
                               key_value ,
                               score_values ,
                               verbose )        
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def process_config( config_file ,
                    score_key ,
                    score_values ,
                    collapse_all_patterns = False ,
                    verbose = False ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    annotations = []
    namespaces = {}
    document_data = {}
    config = ConfigParser.ConfigParser()
    try:
        config.read( config_file )
    except ConfigParser.MissingSectionHeaderError , e:
        log.error( 'Unable to continue due to malformed section header(s):  {}'.format( e ) )
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return namespaces , document_data , annotations
    for sect in config.sections():
        if( sect.strip() == 'XML Namespaces' ):
            namespaces = extract_namespaces( namespaces ,
                                             config ,
                                             sect )
        elif( sect.strip() == 'Document Data' ):
            document_data = extract_document_data( document_data ,
                                                   config ,
                                                   sect )
        else:
            extract_patterns( annotations ,
                              config , sect ,
                              score_key ,
                              score_values ,
                              collapse_all_patterns = collapse_all_patterns ,
                              verbose = verbose )
    verbose_msg = 'Values defined by the config \'{}\':\n' + \
                  '\tns\t=\t{}\n' + \
                  '\tdocument data\t=\t{}\n' + \
                  '\tpatterns\t=\t{}\n'
    log.debug( verbose_msg.format( config_file ,
                                   namespaces ,
                                   document_data ,
                                   annotations ) )
    ##
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return namespaces , document_data , annotations


def align_patterns( reference_patterns , test_patterns ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    filtered_ref = []
    filtered_test = []
    for ref_pattern in reference_patterns:
        match_flag = False
        for test_pattern in test_patterns:
            if( test_pattern[ 'type' ] == ref_pattern[ 'type' ] ):
                match_flag = True
                filtered_ref.append( ref_pattern )
                break
        if( match_flag == False ):
            log.warn( 'Could not find system output pattern matching type \'{}\' from reference config'.format( ref_pattern[ 'type' ] ) )
    for test_pattern in test_patterns:
        match_flag = False
        for ref_pattern in reference_patterns:
            if( test_pattern[ 'type' ] == ref_pattern[ 'type' ] ):
                match_flag = True
                filtered_test.append( test_pattern )
                break
        if( match_flag == False ):
            log.warn( 'Could not find reference pattern matching type \'{}\' from system output config'.format( test_pattern[ 'type' ] ) )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return filtered_ref , filtered_test
