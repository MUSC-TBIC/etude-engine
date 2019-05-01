import os
import sys
import re
import tempfile

import json

import args_and_configs
import scoring_metrics
import text_extraction

from pytest import approx
from pandas.testing import assert_frame_equal

#############################################
## Test helper functions
#############################################

def initialize_perfect_track1_score_card():
    score_card = scoring_metrics.new_score_card()
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'DRUG-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ALCOHOL-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ENGLISH' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'MAKES-DECISIONS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ABDOMINAL' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'MAJOR-DIABETES' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ADVANCED-CAD' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'MI-6MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'KETO-1YR' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'DIETSUPP-2MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ASP-FOR-MI' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'HBA1C' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'CREATININE' , 'not met' , 'TP' ]
    ##
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'DRUG-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ALCOHOL-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ENGLISH' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'MAKES-DECISIONS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ABDOMINAL' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'MAJOR-DIABETES' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ADVANCED-CAD' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'MI-6MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'KETO-1YR' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'DIETSUPP-2MOS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ASP-FOR-MI' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'HBA1C' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'CREATININE' , 'not met' , 'TP' ]
    ##
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'DRUG-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ALCOHOL-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ENGLISH' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'MAKES-DECISIONS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ABDOMINAL' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'MAJOR-DIABETES' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ADVANCED-CAD' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'MI-6MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'KETO-1YR' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'DIETSUPP-2MOS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ASP-FOR-MI' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'HBA1C' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'CREATININE' , 'met' , 'TP' ]
    return score_card


def initialize_track1_score_card_with_errors():
    score_card = scoring_metrics.new_score_card()
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'DRUG-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ALCOHOL-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ENGLISH' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'MAKES-DECISIONS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ABDOMINAL' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'MAJOR-DIABETES' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ADVANCED-CAD' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'MI-6MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'KETO-1YR' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'DIETSUPP-2MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'ASP-FOR-MI' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'HBA1C' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '103.xml' , -1 , -1 , 'CREATININE' , 'not met' , 'TP' ]
    ##
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'DRUG-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ALCOHOL-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ENGLISH' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'MAKES-DECISIONS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ABDOMINAL' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'MAJOR-DIABETES' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ADVANCED-CAD' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'MI-6MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'KETO-1YR' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'DIETSUPP-2MOS' , 'met' , 'FN' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'DIETSUPP-2MOS' , 'not met' , 'FP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'ASP-FOR-MI' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'HBA1C' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'CREATININE' , 'not met' , 'FN' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '203.xml' , -1 , -1 , 'CREATININE' , 'met' , 'FP' ]
    ##
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'DRUG-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ALCOHOL-ABUSE' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ENGLISH' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'MAKES-DECISIONS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ABDOMINAL' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'MAJOR-DIABETES' , 'met' , 'FN' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'MAJOR-DIABETES' , 'not met' , 'FP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ADVANCED-CAD' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'MI-6MOS' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'KETO-1YR' , 'not met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'DIETSUPP-2MOS' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'ASP-FOR-MI' , 'met' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'HBA1C' , 'not met' , 'FN' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'HBA1C' , 'met' , 'FP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ '303.xml' , -1 , -1 , 'CREATININE' , 'met' , 'TP' ]
    return score_card


def initialize_for_track1():
    command_line_args = [ '--reference-input' , 'tests/data/n2c2_2018_track-1_reference' ,
                          '--test-input' , 'tests/data/n2c2_2018_track-1_test' ,
                          '--empty-value' , '0.0' ]
    args = args_and_configs.get_arguments( command_line_args )
    ## TODO - we are usurping the test for this done within init_args to make
    ##        the test more protable, for now.
    args.empty_value = float( args.empty_value )
    file_mapping = { '103.xml': '103.xml' , '203.xml': '203.xml' , '303.xml': '303.xml' }
    return( args , file_mapping )


#############################################
## Test print_score_summary()
#############################################

def test_perfect_track1_output( capsys ):
    score_card = initialize_perfect_track1_score_card()
    args , file_mapping = initialize_for_track1()
    ##
    scoring_metrics.print_2018_n2c2_track1( score_card ,
                                            file_mapping ,
                                            args )
    track1_out, err = capsys.readouterr()
    track1_out = track1_out.strip()
    ##
    expected_values = [
        [ '*******************************************' , 'TRACK' , '1' , '********************************************' ] ,
        [ '------------' , 'met' , '-------------' , '------' , 'not' , 'met' , '-------' , '--' , 'overall' , '---' ] ,
        [ 'Prec.' , 'Rec.' , 'Speci.' , 'F(b=1)' , 'Prec.' , 'Rec.' , 'F(b=1)' , 'F(b=1)' , 'AUC' ] ,
        [ 'Abdominal' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Advanced-cad' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Alcohol-abuse' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ 'Asp-for-mi' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Creatinine' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Dietsupp-2mos' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Drug-abuse' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ 'English' , 1.0000 , 1.0000 , 0.0000 , 1.0000 , 0.0000 , 0.0000 , 0.0000 , 0.5000 , 0.5000 ] ,
        [ 'Hba1c' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ 'Keto-1yr' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ 'Major-diabetes' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Makes-decisions' , 1.0000 , 1.0000 , 0.0000 , 1.0000 , 0.0000 , 0.0000 , 0.0000 , 0.5000 , 0.5000 ] ,
        [ 'Mi-6mos' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ '------------------------------' , '----------------------' , '--------------' ] ,
        [ 'Overall' , '(micro)' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Overall' , '(macro)' , 0.6154 , 0.6154 , 0.8462 , 0.6154 , 0.8462 , 0.8462 , 0.8462 , 0.7308 , 0.7308 ] ,
        [ '' ] ,
        [ '3' , 'files' , 'found' ] ]
    ##
    track1_values = []
    for track1_line in track1_out.split( "\n" ):
        track1_line = track1_line.strip()
        track1_values.append( re.split( r' +' , track1_line ) )
    for track1_line, expected_line in zip( track1_values , expected_values ):
        for tmp_val, expected_val in zip( track1_line , expected_line ):
            ## The mixture of str and float values requires us to
            ## make a type check first...
            if( isinstance( expected_val , str ) ):
                assert tmp_val == expected_val
            elif( expected_val is None or
                  tmp_val == 'None' ):
                ## ...if either are None, then both must be None
                assert expected_val is None
                assert tmp_val == 'None'
            else:
                ## ...followed by an float conversion mapping to
                ## an approximate equality due to rounding differences
                ## between Py2 and Py3
                assert float( tmp_val ) == approx( expected_val )


def test_track1_output_with_errors( capsys ):
    score_card = initialize_track1_score_card_with_errors()
    args , file_mapping = initialize_for_track1()
    ##
    scoring_metrics.print_2018_n2c2_track1( score_card ,
                                            file_mapping ,
                                            args )
    track1_out, err = capsys.readouterr()
    track1_out = track1_out.strip()
    ##
    expected_values = [
        [ '*******************************************' , 'TRACK' , '1' , '********************************************' ] ,
        [ '------------' , 'met' , '-------------' , '------' , 'not' , 'met' , '-------' , '--' , 'overall' , '---' ] ,
        [ 'Prec.' , 'Rec.' , 'Speci.' , 'F(b=1)' , 'Prec.' , 'Rec.' , 'F(b=1)' , 'F(b=1)' , 'AUC' ] ,
        [ 'Abdominal' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Advanced-cad' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Alcohol-abuse' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ 'Asp-for-mi' , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 , 1.0000 ] ,
        [ 'Creatinine' , 0.5000 , 1.0000 , 0.5000 , 0.6667 , 1.0000 , 0.5000 , 0.6667 , 0.6667 , 0.7500 ] ,
        [ 'Dietsupp-2mos' , 1.0000 , 0.5000 , 1.0000 , 0.6667 , 0.5000 , 1.0000 , 0.6667 , 0.6667 , 0.7500 ] ,
        [ 'Drug-abuse' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ 'English' , 1.0000 , 1.0000 , 0.0000 , 1.0000 , 0.0000 , 0.0000 , 0.0000 , 0.5000 , 0.5000 ] ,
        [ 'Hba1c' , 0.0000 , 0.0000 , 0.6667 , 0.0000 , 1.0000 , 0.6667 , 0.8000 , 0.4000 , 0.3333 ] ,
        [ 'Keto-1yr' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ 'Major-diabetes' , 1.0000 , 0.5000 , 1.0000 , 0.6667 , 0.5000 , 1.0000 , 0.6667 , 0.6667 , 0.7500 ] ,
        [ 'Makes-decisions' , 1.0000 , 1.0000 , 0.0000 , 1.0000 , 0.0000 , 0.0000 , 0.0000 , 0.5000 , 0.5000 ] ,
        [ 'Mi-6mos' , 0.0000 , 0.0000 , 1.0000 , 0.0000 , 1.0000 , 1.0000 , 1.0000 , 0.5000 , 0.5000 ] ,
        [ '------------------------------' , '----------------------' , '--------------' ] ,
        [ 'Overall' , '(micro)' , 0.8750 , 0.8750 , 0.9130 , 0.8750 , 0.9130 , 0.9130 , 0.9130 , 0.8940 , 0.8940 ] ,
        [ 'Overall' , '(macro)' , 0.5769 , 0.5385 , 0.7821 , 0.5385 , 0.7692 , 0.7821 , 0.7538 , 0.6462 , 0.6603 ] ,
        [ '' ] ,
        [ '3' , 'files' , 'found' ] ]
    ##
    track1_values = []
    for track1_line in track1_out.split( "\n" ):
        track1_line = track1_line.strip()
        track1_values.append( re.split( r' +' , track1_line ) )
    for track1_line, expected_line in zip( track1_values , expected_values ):
        for tmp_val, expected_val in zip( track1_line , expected_line ):
            ## The mixture of str and float values requires us to
            ## make a type check first...
            if( isinstance( expected_val , str ) ):
                assert tmp_val == expected_val
            elif( expected_val is None or
                  tmp_val == 'None' ):
                ## ...if either are None, then both must be None
                assert expected_val is None
                assert tmp_val == 'None'
            else:
                ## ...followed by an float conversion mapping to
                ## an approximate equality due to rounding differences
                ## between Py2 and Py3
                assert float( tmp_val ) == approx( expected_val )
