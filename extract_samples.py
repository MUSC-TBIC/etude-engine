import sys
import logging as log

import argparse

import os.path

import json

import re

def initialize_arg_parser():
    parser = argparse.ArgumentParser( description = """
ETUDE (Evaluation Tool for Unstructured Data and Extractions) is a
command line tool for scoring and evaluating unstructured data tagging and
unstructured data extraction.
""" )
    parser.add_argument( '-v' , '--verbose' ,
                         help = "print more information" ,
                         action = "store_true" )

    ##
    parser.add_argument( "-m" , "--metrics" , nargs = '+' ,
                         dest = 'metrics_list' ,
                         default = [ 'FP' , 'FN' ] ,
                         choices = [ 'TP' , 'FP' , 'TN' , 'FN' ] ,
                         help = "List of metrics to return examples for" )

    ## TODO - lstrip hack added to handle suffixes with dashes
    ##   https://stackoverflow.com/questions/16174992/cant-get-argparse-to-read-quoted-string-with-dashes-in-it
    parser.add_argument( "--file-suffix", nargs = 2 ,
                         dest = 'file_suffix' ,
                         default = None ,
                         help="Suffix used for filename matching.  If the file names match between reference and system output, you don't need to provide this argument.  Otherwise, the span of the reference filename that matches the file suffix will be replaced with the contents of the second suffix string (e.g., '001.txt' -> '001.xmi')" )

    parser.add_argument( '--annotation-out' ,
                         dest = 'annotation_out' ,
                         required = True ,
                         help = 'Directory containing a dictionary of extracted annotations' )
    
    parser.add_argument( '--score-card' , required = True ,
                         dest = 'score_card' ,
                         help = "Path to the score card (etude engine output) to extract samples from" )
    
    parser.add_argument( '--left-margin' , default = 40 ,
                         dest = 'left_margin' ,
                         help = "Characters to the left of the annotation to include" )
    
    parser.add_argument( '--right-margin' , default = 60 ,
                         dest = 'right_margin' ,
                         help = "Characters to the right of the annotation to include" )
    
    ##
    return parser

def get_arguments( command_line_args ):
    parser = initialize_arg_parser()
    args = parser.parse_args( command_line_args )
    ##
    return args

def init_args():
    ##
    args = get_arguments( sys.argv[ 1: ] )
    ## Set up logging
    if args.verbose:
        log.basicConfig( format = "%(levelname)s: %(message)s" ,
                         level = log.DEBUG )
        log.info( "Verbose output." )
        log.debug( "{}".format( args ) )
    else:
        log.basicConfig( format="%(levelname)s: %(message)s" )
    ##
    if( args.file_suffix is not None ):
        args.file_suffix[ 0 ] = args.file_suffix[ 0 ].lstrip()
        args.file_suffix[ 1 ] = args.file_suffix[ 1 ].lstrip()
    ##
    try:
        args.left_margin = int( args.left_margin )
    except ValueError:
        log.error( 'Left margin value is not an int' )
    try:
        args.right_margin = int( args.right_margin )
    except ValueError:
        log.error( 'Right margin value is not an int' )
    ##
    return args

if __name__ == "__main__":
    ##
    args = init_args()
    ##
    last_filename = ''
    note_text = ''
    note_max = 0
    offset_mapping = {}
    ##
    with open( args.score_card , 'r' ) as fp:
        fp.readline()
        for line in fp:
            line = line.rstrip()
            cols = re.split( r'\t' , line )
            reference_filename = cols[ 0 ]
            begin_offset_mapped = int( cols[ 1 ] )
            end_offset_mapped = int( cols[ 2 ] )
            type_str = cols[ 3 ]
            pivot_str = cols[ 4 ]
            score_type = cols[ 5 ]
            if( score_type not in args.metrics_list ):
                continue
            if( reference_filename != last_filename ):
                last_filename = reference_filename
                if( args.file_suffix is None ):
                    target_filename = reference_filename
                else:
                    target_filename = re.sub( args.file_suffix[ 0 ] + '$' ,
                                              args.file_suffix[ 1 ] ,
                                              reference_filename )
                with open( os.path.join( args.annotation_out ,
                                         target_filename ) ) as json_data:
                    d = json.load( json_data )
                    note_text = d[ 'raw_content' ]
                    note_max = len( note_text )
                    for key in d[ 'offset_mapping' ]:
                        if( d[ 'offset_mapping' ][ key ] is not None ):
                            offset_mapping[ int( d[ 'offset_mapping' ][ key ] ) ] = int( key )
            if( note_text is not None ):
                begin_offset = offset_mapping[ int( begin_offset_mapped ) ]
                end_offset = min( note_max ,
                                  offset_mapping[ int( end_offset_mapped ) ] + 1 )
                target = note_text[ begin_offset:end_offset ]
                target = re.sub( '[\r\n]+' , ' ' , target )
                left_begin = max( 0 , begin_offset - args.left_margin )
                right_end = min( note_max , end_offset + args.right_margin )
                left_context = note_text[ left_begin:begin_offset ]
                left_context = re.sub( '[\r\n]+' , ' ' , left_context )
                left_context = left_context.ljust( args.left_margin )
                right_context = note_text[ end_offset:right_end ]
                right_context = re.sub( '[\r\n]+' , ' ' , right_context )
                right_context = right_context.rjust( args.right_margin )
                ##    
                print( '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format( target_filename ,
                                                                begin_offset , end_offset ,
                                                                type_str ,
                                                                score_type ,
                                                                left_context ,
                                                                target ,
                                                                right_context ) )
