import os
import sys
import logging as log

import re

try:
    set
except NameError:
    from sets import Set as set

import argparse
import configparser

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

    parser.add_argument( '--pretty-print' ,
                         dest = 'pretty_print' ,
                         help = "Round floats and remove decimals from integers" ,
                         action = "store_true" )
    
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
                                     'F1' , 'F2' , 'F0.5' , 'F' ] ,
                         help = "List of metrics to return, in order" )
    parser.add_argument( "--f-beta-values" , nargs = '+' ,
                         dest = 'f_beta_values' ,
                         default = [] ,
                         help = "List of beta values to use in calculating the F-score. This list is only used when 'F' is a given metric." )
    
    parser.add_argument( '--empty-value' ,
                         dest = 'empty_value' ,
                         default = None ,
                         help = "Value to print when metrics are undefined or values are null" )

    parser.add_argument( "--fuzzy-match-flags" , nargs = "+" ,
                         dest = 'fuzzy_flags' ,
                         default = [ 'exact' ] ,
                         choices = [ 'exact' , 'fully-contained' , 'partial' ,
                                     'start' ,
                                     'end' ,
                                     'doc-property' ] ,
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
    parser.add_argument( '--by-type-and-attribute' , dest = 'by_type_and_attribute' ,
                         help = "Print metrics by attribute nested within annotation type" ,
                         action = "store_true" )
    parser.add_argument( '--by-type-and-file' , dest = 'by_type_and_file' ,
                         help = "Print metrics by file nested within annotation type" ,
                         action = "store_true" )
    
    parser.add_argument( '--by-attribute' , dest = 'by_attribute' ,
                         help = "Print metrics by annotation attribute" ,
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

    parser.add_argument("--score-attributes", nargs = '?' ,
                        dest = 'attributes_string' ,
                        default = None , ## When --score-attributes is not present
                        const = [] ,     ## When --score-attributes is provided but no attributes listed
                        help="List of annotation attributes to evaluate in addition to type" )
    
    parser.add_argument("--score-normalization", nargs = '?' ,
                        dest = 'normalization_string' ,
                        default = None , ## When --score-normalization is not present
                        const = [] ,     ## When --score-normalization is provided but no engines listed
                        help="List of normalization engines to evaluate in addition to type" )
    parser.add_argument("--normalization-file", #nargs = 1 ,
                        dest = 'normalization_file' ,
                        default = None ,
                        help="A tab-delimited, two-column file containing normalization strings that should be treated as equivalent for the purposes of scoring" )

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
    
    ## TODO - make it easy to load / reference these special print functions
    ##        from separate files
    parser.add_argument( "--print-custom" , nargs = '+' ,
                         dest = 'print_custom' ,
                         default = [ ] ,
                         choices = [ '2018 n2c2 track 1' ] ,
                         help = "Use one of any custom output print functions.  Usually, these are created to replicate the output of a different tool." )

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
    if( 'start' in args.fuzzy_flags and
        len( args.fuzzy_flags ) > 1 ):
        parser.error( "Using the fuzzy match flag 'start' is not compatible with other flags." )
    if( 'end' in args.fuzzy_flags and
        len( args.fuzzy_flags ) > 1 ):
        parser.error( "Using the fuzzy match flag 'end' is not compatible with other flags." )
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
    """
    Add handling for any special document-level data fields
    """
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
    elif( config.has_option( sect , 'Content JSONPath' ) ):
        document_data[ 'content_jsonpath' ] = config.get( sect ,
                                                          'Content JSONPath' )
    if( config.has_option( sect , 'Normalization Engines' ) ):
        engines_string = config.get( sect , 'Normalization Engines' )
        engines_split = engines_string.split( ',' )
        if( isinstance( engines_split , str ) ):
            document_data[ 'normalization_engines' ] = [ engines_split ]
        else:
            document_data[ 'normalization_engines' ] = engines_split
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


def extract_xpath_spanless_patterns( annotations ,
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
                                  pivot_attr = config.get( sect ,
                                                           'Pivot Attr' ) ,
                                  parity = config.get( sect ,
                                                       'Parity' ) ,
                                  optional_attributes = [] )
            if( pattern_entry[ 'parity' ] not in [ 'First' , 'Last' ,
                                                   'Unique' , 'Any' ] ):
                log.warn( '{} {} ( {} , {} )'.format( 
                    'Unexpected setting for annotation parity.' ,
                    'This may have unpredictable consequences:' ,
                    pattern_entry[ 'long_name' ] ,
                    pattern_entry[ 'parity' ] ) )
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
                                  delimiter = config.get( sect ,
                                                          'Delimiter' ) ,
                                  display_name = display_name ,
                                  short_name = config.get( sect ,
                                                           'Short Name' ) ,
                                  optional_attributes = [] )
            if( config.has_option( sect , 'Opt Col' ) ):
                ## TODO - hard-coded for special CSV files
                pattern_entry[ 'optional_attributes' ] = \
                  [ 'affirmed' , 'negated' , 'possible' ]

            if( config.get( sect , 'Delimiter' ) == "," ):
                pattern_entry[ 'begin_attr' ] = config.get( sect ,
                                                            'Begin Col' ) ,
                pattern_entry[ 'end_attr' ] = config.get( sect ,
                                                          'End Col' ) ,
                ## TODO - support span column
                ## pattern_entry[ '' ] = config.get( sect , 'Text Col' )                
            annotations.append( pattern_entry )
            break
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def extract_brat_patterns( annotations ,
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
            ## Used for text bound annotation if using a different
            ## score key rather than short name.  This will give
            ## the option of checking for the key_value in files and
            ## if not, will check for the line_type in files.
            if( key_value != 'Short Name' ):
                pattern_entry = dict( type = type_value ,
                                      line_type = config.get( sect ,
                                                              'Short Name') ,
                                      long_name = sect.strip() ,
                                      type_prefix = config.get( sect ,
                                                                'Type Prefix') ,
                                      short_name = config.get( sect ,
                                                               'Short Name') ,
                                      optional_attributes = [] )
            else:
                pattern_entry = dict( type = type_value ,
                                      long_name = sect.strip() ,
                                      type_prefix = config.get( sect ,
                                                                'Type Prefix' ) ,
                                      display_name = display_name ,
                                      short_name = config.get( sect ,
                                                               'Short Name' ) ,
                                      optional_attributes = [] )
            if( config.has_option( sect , 'Opt Attr' ) ):
                optional_attributes = config.get( sect , 'Opt Attr' )
                pattern_entry[ 'optional_attributes' ] = \
                  optional_attributes.split( ',' )
            annotations.append( pattern_entry )
            break
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def extract_semeval_patterns( annotations ,
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
                                  display_name = display_name ,
                                  short_name = config.get( sect ,
                                                           'Short Name' ) ,
                                  optional_attributes = [] )
            if( config.has_option( sect , 'Opt Attr' ) ):
                optional_attributes = config.get( sect , 'Opt Attr' )
                pattern_entry[ 'optional_attributes' ] = \
                  optional_attributes.split( ',' )
            annotations.append( pattern_entry )
            break
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def extract_json_patterns( annotations ,
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
                                  jsonpath = config.get( sect , 'JSONPath' ) ,
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


def extract_patterns( annotations ,
                      config , sect ,
                      score_key ,
                      score_values ,
                      collapse_all_patterns = False ,
                      verbose = False ):
    """Iterates over each config section not handled by
    extract_namespaces() or extract_document_data() and pulls out the
    pattern-level configuration details.
    """
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    ####
    if( score_key == 'Long Name' or
        score_key == 'Section' ):
        key_value = sect.strip()
        display_name = key_value
    else:
        ## Skip any entry missing the score_key we're interested in
        if( not config.has_option( sect , score_key ) ):
            log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
            return
        ##
        key_value = config.get( sect , score_key )
        display_name = '{} ({})'.format( sect.strip() ,
                                         config.get( sect , score_key ) )
    ## Overwrite the display_name with a general title if we're collapsing all patterns
    if( collapse_all_patterns ):
        display_name = 'All Patterns'
    ####
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
    elif( config.has_option( sect , 'XPath' ) and
          config.has_option( sect , 'Pivot Attr' ) ):
        try:
            extract_xpath_spanless_patterns( annotations ,
                                             config , sect ,
                                             display_name ,
                                             key_value ,
                                             score_values ,
                                             collapse_all_patterns ,
                                             verbose )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_xpath_spanless_patterns:  {}'.format( e ) )
    elif( config.has_option( sect , 'Delimiter' ) ):
        extract_delimited_patterns( annotations ,
                                    config , sect ,
                                    display_name ,
                                    key_value ,
                                    score_values ,
                                    collapse_all_patterns ,
                                    verbose )
    elif( config.has_option( sect , 'Type Prefix' ) ):
        extract_brat_patterns( annotations ,
                               config , sect ,
                               display_name ,
                               key_value ,
                               score_values ,
                               collapse_all_patterns ,
                               verbose )
    elif( config.has_option( sect , 'JSONPath' ) ):
        extract_json_patterns( annotations ,
                               config , sect ,
                               display_name ,
                               key_value ,
                               score_values ,
                               collapse_all_patterns ,
                               verbose )        
    else:
        extract_semeval_patterns( annotations ,
                                  config , sect ,
                                  display_name ,
                                  key_value ,
                                  score_values ,
                                  collapse_all_patterns ,
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
    config = configparser.ConfigParser()
    config.optionxform = str
    if( not os.path.exists( config_file ) ):
        log.error( 'Config file is missing or unreadable:  {}'.format( config_file ) )
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return namespaces , document_data , annotations
    try:
        config.read( config_file )
    except configparser.MissingSectionHeaderError as e:
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


def process_normalization_file( normalization_file ):
    norm_synonyms = {}
    if( normalization_file is None ):
        return norm_synonyms
    with open( normalization_file , 'r' ) as fp:
        for line in fp:
            line = line.rstrip( '\n' )
            terms = line.split( '\t' )
            lhs = terms[ 0 ]
            norm_synonyms[ lhs ] = terms
    return norm_synonyms


def align_patterns( reference_patterns , 
                    test_patterns ,
                    collapse_all_patterns ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    filtered_ref = []
    filtered_test = []
    for ref_pattern in reference_patterns:
        ## TODO - distinguish between collapsing all patterns blindly
        ## and still filtering the two patterns before collapsing all
        ## together
        match_flag = False
        for test_pattern in test_patterns:
            if( test_pattern[ 'type' ] == ref_pattern[ 'type' ] ):
                match_flag = True
                filtered_ref.append( ref_pattern )
                break
        if( match_flag == False ):
            log.warning( 'Could not find system output pattern matching type \'{}\' from reference config'.format( ref_pattern[ 'type' ] ) )
    for test_pattern in test_patterns:
        match_flag = False
        for ref_pattern in reference_patterns:
            if( test_pattern[ 'type' ] == ref_pattern[ 'type' ] ):
                match_flag = True
                filtered_test.append( test_pattern )
                break
        if( match_flag == False ):
            log.warning( 'Could not find reference pattern matching type \'{}\' from system output config'.format( test_pattern[ 'type' ] ) )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return filtered_ref , filtered_test

def unique_attributes( patterns ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    filtered_attributes = set()
    for pattern in patterns:
        ## Skip this pattern if there are no listed attributes
        if( 'optional_attributes' not in pattern ):
            continue
        for attribute in pattern[ 'optional_attributes' ]:
            filtered_attributes.add( attribute )
    return( filtered_attributes )
