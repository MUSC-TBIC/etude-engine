from __future__ import print_function

import argparse

import glob
import os
## TODO - use warnings
import warnings

import re
import xml.etree.ElementTree as ET

import pandas as pd


def extract_annotations_kernel( ingest_file ,
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
    for annot in root.findall( tag_name ):
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
                          type = 'Dates and Times' ,
                          score = default_score )
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = ( new_entry )
        ##print( '\t{}\t{}\t{}'.format( begin_pos , end_pos , raw_text ) )
    ## 
    return strict_starts

def extract_annotations( ingest_file ,
                         type = 'i2b2_2016_track-1' ):
    if( type == 'i2b2_2016_track-1' ):
        return extract_annotations_kernel( ingest_file ,
                                           tag_name = './TAGS/DATE' ,
                                           begin_attribute = 'start' ,
                                           end_attribute = 'end' ,
                                           text_attribute = 'text' )
    elif( type == 'CAS XMI' ):
        return extract_annotations_kernel( ingest_file ,
                                           tag_name = './/org.apache.uima.tutorial.DateAnnot' ,
                                           begin_attribute = 'begin' ,
                                           end_attribute = 'end' ,
                                           default_score = 'FP' )
        

def norm_summary( score_summary ):
    score_types = score_summary.keys()
    ## First, we want to make sure that all score types are represented
    ## in the summary series.
    if( 'TP' not in score_types ):
        score_summary[ 'TP' ] = 0
    if( 'FP' not in score_types ):
        score_summary[ 'FP' ] = 0
    if( 'TN' not in score_types ):
        score_summary[ 'TN' ] = 0
    if( 'FN' not in score_types ):
        score_summary[ 'FN' ] = 0
    return score_summary


def score_ref_set( gold_folder , test_folder ,
                   file_prefix = '/' ,
                   file_suffix = '.xml' ,
                   verbose = False ):
    """
    Score the test folder against the gold folder.
    """
    score_card = pd.DataFrame( columns = [ 'File' ,
                                           'Start' , 'End' ,
                                           'Type' , 'Score' ] )
    golds = set([os.path.basename(x) for x in glob.glob( gold_folder +
                                                         file_prefix +
                                                         '*' +
                                                         file_suffix )])
    tests = set([os.path.basename(x) for x in glob.glob( test_folder +
                                                         file_prefix +
                                                         '*' +
                                                         file_suffix )])
    ## TODO - refactor score printing to a separate function
    ## TODO - add scores grouped by type
    ## TODO - allow tab, column, arbitrary separators in print
    print( '\n{}\t{}\t{}\t{}\t{}\n'.format( 'Filename' ,
                                            'TP' ,
                                            'FP' ,
                                            'TN' ,
                                            'FN' ) )
    for gold_filename in sorted( golds ):
        ## TODO - parameterize this (optional) substitution
        test_filename = re.sub( 'xml$' , r'txt' , gold_filename )
        ## TODO - refactor into separate fuction
        gold_ss = extract_annotations( '{}/{}'.format( gold_folder ,
                                                       gold_filename ) ,
                                       type = 'i2b2_2016_track-1' )
        test_ss = extract_annotations( '{}/{}'.format( test_folder ,
                                                       test_filename ) ,
                                       type = 'CAS XMI' )
        for gold_start in gold_ss.keys():
            if( gold_start in test_ss.keys() ):
                score_card.loc[ score_card.shape[ 0 ] ] = \
                  [ gold_filename , gold_start , '' , '' , 'TP' ]
            else:
                score_card.loc[ score_card.shape[ 0 ] ] = \
                  [ gold_filename , gold_start , '' , '' , 'FN' ]
        for test_start in test_ss.keys():
            if( test_start not in gold_ss.keys() ):
                score_card.loc[ score_card.shape[ 0 ] ] = \
                  [ gold_filename , gold_start , '' , '' , 'FP' ]
        if( verbose ):
            ## TODO - make this per file
            this_file = ( score_card[ 'File' ] == gold_filename )
            score_summary = norm_summary( score_card[ this_file ][ 'Score' ].value_counts() )
            print( '{}\t{}\t{}\t{}\t{}'.format( gold_filename ,
                                                score_summary[ 'TP' ] ,
                                                score_summary[ 'FP' ] ,
                                                score_summary[ 'TN' ] ,
                                                score_summary[ 'FN' ] ) )
    ##
    score_summary = norm_summary( score_card[ 'Score' ].value_counts() )
    if( verbose ):
        print( '' )
    print( 'aggregate\t{}\t{}\t{}\t{}\n'.format( score_summary[ 'TP' ] ,
                                                 score_summary[ 'FP' ] ,
                                                 score_summary[ 'TN' ] ,
                                                 score_summary[ 'FN' ] ) )
            

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
    
    args = parser.parse_args()
    
    score_ref_set( os.path.abspath( args.gold_dir ) ,
                   os.path.abspath( args.test_dir ) ,
                   verbose = args.verbose )
