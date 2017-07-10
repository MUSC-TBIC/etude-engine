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

    ## TODO -
    ## --sample % of files to randomly sample from
    ## --head X grab the first files from the directory
    ## --tail Y grab the last files from the directory
    ## --file-pattern "" regex pattern fed to glob for selecting files
    ##                   (maybe call this --file-filter?)
    
    parser.add_argument( '--gold-input' , required = True ,
                        dest = "gold_input",
                        help = "Directory containing gold reference set" )
    parser.add_argument( '--test-input' , required = True ,
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

    parser.add_argument("-d", 
                        dest = 'delim' ,
                        default = '\t' ,
                        help="Delimiter used in all output streams" )

    parser.add_argument( '--by-file' , dest = 'by_file' ,
                         help = "Print metrics by file" ,
                         action = "store_true" )
    
    parser.add_argument( '--by-type' , dest = 'by_type' ,
                         help = "Print metrics by annotation type" ,
                         action = "store_true" )

    parser.add_argument("--gold-config", 
                        dest = 'gold_config' ,
                        default = 'config/i2b2_2016_track-1.conf' ,
                        help="Configuration file that describes the gold format" )
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

    parser.add_argument("--file-prefix", 
                        dest = 'file_prefix' ,
                        default = '/' ,
                        help="Prefix used for filename matching" )
    ## TODO - lstrip hack added to handle suffixes with dashes
    ##   https://stackoverflow.com/questions/16174992/cant-get-argparse-to-read-quoted-string-with-dashes-in-it
    parser.add_argument("--file-suffix", nargs = '+' ,
                        dest = 'file_suffix' ,
                        default = [ '.xml' ] ,
                        help="Suffix used for filename matching.  You can provide a second argument if the test file suffixes don't match the gold file suffixes. The span of the gold filename that matches the file suffix will be replaced with the contents of the second suffix string.  This replacement is useful when the gold and test differ in terms of file endings (e.g., '001.txt' -> '001.xmi')" )

    parser.add_argument( '--gold-out' ,
                         dest = 'gold_out' ,
                         default = None ,
                         help = 'When provided, write the dictionary of extracted gold annotations to disk in this directory' )
    
    parser.add_argument( '--test-out' ,
                         dest = 'test_out' ,
                         default = None ,
                         help = 'When provided, write the dictionary of extracted test annotations to disk in this directory' )
    
    parser.add_argument( '-c' , '--count-types' ,
                         dest = 'count_types' ,
                         help = "Count pattern types in each test file" ,
                         action = "store_true" )
    
    parser.add_argument( '--ignore-whitespace' ,
                         default = True ,
                         dest = 'ignore_whitespace' ,
                         help = "Create a offset mapping from the raw document that ignores whitespaces in the offset index (Turned on by default; the counter argument to --count-whitespace)" ,
                         action = "store_true" )
    
    parser.add_argument( '--heed-whitespace' ,
                         dest = 'ignore_whitespace' ,
                         help = "Include all whitespace in the offset mapping from the raw document (the counter argument to --ignore-whitespace" ,
                         action = "store_false" )
    ##
    return parser


def get_arguments( command_line_args ):
    parser = initialize_arg_parser()
    args = parser.parse_args( command_line_args )
    ##
    if( args.verbose ):
        print( '{}'.format( args ) )
    ##
    return args

def extract_namespaces( namespaces ,
                        config , sect ):
    for ns , value in config.items( sect ):
        namespaces[ ns ] = value
    return namespaces


def extract_document_data( document_data ,
                           config , sect ):
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
    return document_data


def extract_patterns( annotations ,
                      config , sect ,
                      score_key ,
                      score_values ):
    if( config.has_option( sect , 'XPath' ) and
        config.has_option( sect , 'Begin Attr' ) and
        config.has_option( sect , 'End Attr' ) ):
        display_name = '{} ({})'.format( sect.strip() ,
                                         config.get( sect , 'Short Name' ) )
        if( score_key == 'Long Name' or
            score_key == 'Section' ):
            key_value = sect.strip()
        else:
            key_value = config.get( sect , score_key )
        ## Loop through all the provided score_values to see if any
        ## provided values match the currently extracted value
        for score_value in score_values:
            if( re.search( score_value , key_value ) ):
                annotations.append( dict( type = key_value ,
                                          long_name = sect.strip() ,
                                          xpath = config.get( sect , 'XPath' ) ,
                                          display_name = display_name ,
                                          short_name = config.get( sect ,
                                                                   'Short Name' ) ,
                                          begin_attr = config.get( sect ,
                                                                   'Begin Attr' ) ,
                                          end_attr = config.get( sect ,
                                                                 'End Attr' ) ) )
                break
    elif( config.has_option( sect , 'Delimiter' ) ):
        display_name = '{} ({})'.format( sect.strip() ,
                                         config.get( sect , 'Short Name' ) )
        if( score_key == 'Long Name' or
            score_key == 'Section' ):
            key_value = sect.strip()
        else:
            key_value = config.get( sect , score_key )
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
    return annotations


def process_config( config_file ,
                    score_key ,
                    score_values ):
    config = ConfigParser.ConfigParser()
    config.read( config_file )
    annotations = []
    namespaces = {}
    document_data = {}
    for sect in config.sections():
        if( sect.strip() == 'XML Namespaces' ):
            namespaces = extract_namespaces( namespaces , config , sect )
        elif( sect.strip() == 'Document Data' ):
            document_data = extract_document_data( document_data , config , sect )
        else:
            annotations = extract_patterns( annotations ,
                                            config , sect ,
                                            score_key ,
                                            score_values )
    ##
    return namespaces , document_data , annotations
