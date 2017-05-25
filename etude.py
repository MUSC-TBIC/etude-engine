from __future__ import print_function

import argparse
import ConfigParser

import glob
import os
## TODO - use warnings
import warnings

import re
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

import scoring_metrics

def extract_annotations_kernel( ingest_file ,
                                annotation_path ,
                                tag_name ,
                                begin_attribute = None ,
                                end_attribute = None ,
                                text_attribute = None ,
                                default_score = 'FN' ):
    strict_starts = {}
    ##
    tree = ET.parse( ingest_file )
    root = tree.getroot()
    ##
    for annot in root.findall( annotation_path ):
        if( begin_attribute != None ):
            begin_pos = annot.get( begin_attribute )
        if( end_attribute != None ):
            end_pos = annot.get( end_attribute )
        if( text_attribute == None ):
            raw_text = annot.text
        else:
            raw_text = annot.get( text_attribute )
        new_entry = dict( end_pos = end_pos ,
                          raw_text = raw_text ,
                          type = tag_name ,
                          score = default_score )
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = [ new_entry ]
        ##print( '\t{}\t{}\t{}'.format( begin_pos , end_pos , raw_text ) )
    ## 
    return strict_starts

def extract_annotations( ingest_file ,
                         patterns ):
    annotations = {}
    for pattern in patterns:
        annotations.update( 
            extract_annotations_kernel( ingest_file ,
                                        annotation_path = pattern[ 'xpath' ] ,
                                        tag_name = pattern[ 'type' ] ,
                                        begin_attribute = pattern[ 'begin_attr' ] ,
                                        end_attribute = pattern[ 'end_attr' ] ) )
    return annotations


def score_ref_set( gold_config , gold_folder ,
                   test_config , test_folder ,
                   args ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ):
    """
    Score the test folder against the gold folder.
    """
    score_card = pd.DataFrame( columns = [ 'File' ,
                                           'Start' , 'End' ,
                                           'Type' , 'Score' ] )
    confusion_matrix = {}
    golds = set([os.path.basename(x) for x in glob.glob( gold_folder +
                                                         file_prefix +
                                                         '*' +
                                                         file_suffix )])
    for gold_filename in sorted( golds ):
        ## TODO - parameterize this (optional) substitution
        test_filename = re.sub( 'xml$' , r'txt' , gold_filename )
        ## TODO - refactor into separate fuction
        gold_ss = extract_annotations( '{}/{}'.format( gold_folder ,
                                                       gold_filename ) ,
                                       patterns = gold_config )
        test_ss = extract_annotations( '{}/{}'.format( test_folder ,
                                                       test_filename ) ,
                                       patterns = test_config )
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
                                         sorted( golds ) ,
                                         gold_config , test_config ,
                                         args )

    
def process_config( config_file ):
    config = ConfigParser.ConfigParser()
    config.read( config_file )
    annotations = []
    for sect in config.sections():
        if( config.has_option( sect , 'XPath' ) and
            config.has_option( sect , 'Begin Attr' ) and
            config.has_option( sect , 'End Attr' ) ):
            display_name = '{} ({})'.format( sect.strip() ,
                                             config.get( sect , 'Short Name' ) )
            annotations.append( dict( type = sect.strip() ,
                                      xpath = config.get( sect , 'XPath' ) ,
                                      display_name = display_name ,
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

    parser.add_argument("-d", nargs = '?' ,
                        dest = 'delim' ,
                        default = '\t' ,
                        help="Delimiter used in all output streams" )

    parser.add_argument( '--by-file' , dest = 'by_file' ,
                         help = "Print metrics by file" ,
                         action = "store_true" )
    
    parser.add_argument( '--by-type' , dest = 'by_type' ,
                         help = "Print metrics by annotation type" ,
                         action = "store_true" )

    parser.add_argument("--gold-config", nargs = '?' ,
                        dest = 'gold_config' ,
                        default = 'i2b2_2016_track-1.conf' ,
                        help="Configuration file that describes the gold format" )
    parser.add_argument("--test-config", nargs = '?' ,
                        dest = 'test_config' ,
                        default = 'CAS_XMI.conf' ,
                        help="Configuration file that describes the test format" )

    parser.add_argument("--file-prefix", nargs = '?' ,
                        dest = 'file_prefix' ,
                        default = '/' ,
                        help="Prefix used for filename matching" )
    parser.add_argument("--file-suffix", nargs = '?' ,
                        dest = 'file_suffix' ,
                        default = '.xml' ,
                        help="Suffix used for filename matching" )

    args = parser.parse_args()
    ## Extract and process the two input file configs
    gold_patterns = process_config( config_file = args.gold_config )
    test_patterns = process_config( config_file = args.test_config )
    
    score_ref_set( gold_config = gold_patterns ,
                   gold_folder = os.path.abspath( args.gold_dir ) ,
                   test_config = test_patterns ,
                   test_folder = os.path.abspath( args.test_dir ) ,
                   args = args ,
                   file_prefix = args.file_prefix ,
                   file_suffix = args.file_suffix )
