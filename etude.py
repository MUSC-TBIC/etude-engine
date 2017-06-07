from __future__ import print_function

import argparse
import ConfigParser
import progressbar

import glob
import os
## TODO - use warnings
import warnings

import re
import xml.etree.ElementTree as ET

import numpy as np

import scoring_metrics
import text_extraction
    
def count_ref_set( test_config , test_folder ,
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
                                               patterns = test_config )
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
                                          test_config ,
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


def score_ref_set( gold_config , gold_folder ,
                   test_config , test_folder ,
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
        ## Empty dictionaries evaluate to False so testing bool can tell us if any gold
        ## documents exist
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
                                               patterns = gold_config )
        test_filename = file_mapping[ gold_filename ]
        if( test_filename == None ):
            test_ss = {}
        else:
            test_ss = \
              text_extraction.extract_annotations( '{}/{}'.format( test_folder ,
                                                                   test_filename ) ,
                                                   patterns = test_config )
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
                                         gold_config , test_config ,
                                         args )

    
def process_config( config_file ,
                    score_key ):
    config = ConfigParser.ConfigParser()
    config.read( config_file )
    annotations = []
    for sect in config.sections():
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
    ##
    return annotations

if __name__ == "__main__":
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
    
    parser.add_argument("gold_dir",
                        help="Directory containing gold reference set")
    parser.add_argument("test_dir",
                        help="Directory containing reference set to score")

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
                        default = 'config/CAS_XMI.conf' ,
                        help="Configuration file that describes the test format" )

    parser.add_argument("--score-key", 
                        dest = 'score_key' ,
                        default = 'Short Name' ,
                        help="Configuration file key used as the join key for matching patterns in scoring" )

    parser.add_argument("--file-prefix", 
                        dest = 'file_prefix' ,
                        default = '/' ,
                        help="Prefix used for filename matching" )
    ## TODO - lstrip hack added to handle suffixes with dashes
    ##   https://stackoverflow.com/questions/16174992/cant-get-argparse-to-read-quoted-string-with-dashes-in-it
    parser.add_argument("--file-suffix", nargs = '+' ,
                        dest = 'file_suffix' ,
                        default = '.xml' ,
                        help="Suffix used for filename matching.  You can provide a second argument if the test file suffixes don't match the gold file suffixes. The span of the gold filename that matches the file suffix will be replaced with the contents of the second suffix string.  This replacement is useful when the gold and test differ in terms of file endings (e.g., '001.txt' -> '001.xmi')" )
    
    parser.add_argument( '-c' , '--count-types' ,
                         dest = 'count_types' ,
                         help = "Count pattern types in each test file" ,
                         action = "store_true" )

    args = parser.parse_args()
    if( args.verbose ):
        print( '{}'.format( args ) )
    ## Extract and process the two input file configs
    gold_patterns = process_config( config_file = args.gold_config ,
                                    score_key = args.score_key )
    test_patterns = process_config( config_file = args.test_config ,
                                    score_key = args.score_key )

    if( args.count_types ):
        count_ref_set( test_config = test_patterns ,
                       test_folder = os.path.abspath( args.test_dir ) ,
                       args = args ,
                       file_prefix = args.file_prefix ,
                       file_suffix = args.file_suffix[ len( args.file_suffix ) - 1 ].lstrip() )
    else:
        score_ref_set( gold_config = gold_patterns ,
                       gold_folder = os.path.abspath( args.gold_dir ) ,
                       test_config = test_patterns ,
                       test_folder = os.path.abspath( args.test_dir ) ,
                       args = args ,
                       file_prefix = args.file_prefix ,
                       file_suffix = args.file_suffix )
