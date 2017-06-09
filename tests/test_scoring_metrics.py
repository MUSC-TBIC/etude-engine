import sys
import re

import pandas as pd

import args_and_configs
import scoring_metrics

#############################################
## Test helper functions
#############################################

def add_missing_fields( test_type ):
    score_card = scoring_metrics.new_score_card()
    new_types = score_card.keys()
    assert test_type not in new_types
    score_summary = scoring_metrics.add_missing_fields( score_card )
    score_types = score_summary.keys()
    assert test_type in score_types

def test_add_missing_fields_TP():
    add_missing_fields( 'TP' )

def test_add_missing_fields_FP():
    add_missing_fields( 'FP' )

def test_add_missing_fields_TN():
    add_missing_fields( 'TN' )

def test_add_missing_fields_FN():
    add_missing_fields( 'FN' )


## TODO - test_norm_summary variants


## TODO - test_print_score_summary variants


#############################################
## Test scoring metrics
#############################################

## TODO - add a range of edge case examples to scoring metric tests

def test_accuracy_all_zero():
    assert scoring_metrics.accuracy( 0 , 0 , 0 , 0 ) == 0.0

def test_accuracy_all_ones():
    assert scoring_metrics.accuracy( 1 , 1 , 1 , 1 ) == 0.5

def test_precision_all_zero():
    assert scoring_metrics.precision( 0 , 0 ) == 0.0

def test_precision_all_ones():
    assert scoring_metrics.precision( 1 , 1 ) == 0.5

def test_recall_all_zero():
    assert scoring_metrics.recall( 0 , 0 ) == 0.0

def test_recall_all_ones():
    assert scoring_metrics.recall( 1 , 1 ) == 0.5

def test_specificity_all_zero():
    assert scoring_metrics.specificity( 0 , 0 ) == 0.0

def test_specificity_all_ones():
    assert scoring_metrics.specificity( 1 , 1 ) == 0.5

def test_f_score_all_zero():
    assert scoring_metrics.f_score( 0.0 , 0.0 ) == 0.0

def test_f_score_even_split():
    assert scoring_metrics.f_score( 0.5 , 0.5 ) == 0.5

def test_f_score_all_ones():
    assert scoring_metrics.f_score( 1.0 , 1.0 ) == 1

def test_f_score_low_precision():
    assert scoring_metrics.f_score( 0.1 , 1.0 ) == 0.18181818181818182

def test_f_score_max_precision():
    assert scoring_metrics.f_score( 1.0 , 0.0 ) == 0.0

def test_f_score_low_recall():
    assert scoring_metrics.f_score( 1.0 , 0.1 ) == 0.18181818181818182

def test_f_score_max_recall():
    assert scoring_metrics.f_score( 0.0 , 1.0 ) == 0.0

def test_f_score_beta_inversely_proportional_to_precision():
    assert scoring_metrics.f_score( 1.0 , 0.1 , beta = 1 ) < \
        scoring_metrics.f_score( 1.0 , 0.1 , beta = 0.5 )
    assert scoring_metrics.f_score( 1.0 , 0.1 , beta = 1 ) > \
        scoring_metrics.f_score( 1.0 , 0.1 , beta = 2 )

def test_f_score_beta_proportional_to_recall():
    assert scoring_metrics.f_score( 0.1 , 1.0 , beta = 1 ) > \
        scoring_metrics.f_score( 0.1 , 1.0 , beta = 0.5 )
    assert scoring_metrics.f_score( 0.1 , 1.0 , beta = 1 ) < \
        scoring_metrics.f_score( 0.1 , 1.0 , beta = 2 )

#############################################
## Test helper functions
#############################################

def initialize_for_print_summary_test():
    score_card = scoring_metrics.new_score_card()
    score_card.loc[ score_card.shape[ 0 ] ] = \
      [ 'a.xml' , 0 , 1 , 'Sentence' , 'TP' ]
    score_card.loc[ score_card.shape[ 0 ] ] = \
      [ 'b.xml' , 0 , 1 , 'Sentence' , 'FP' ]
    score_card.loc[ score_card.shape[ 0 ] ] = \
      [ 'a.xml' , 0 , 1 , 'Sentence' , 'FN' ]
    score_card.loc[ score_card.shape[ 0 ] ] = \
      [ 'b.xml' , 0 , 1 , 'Sentence' , 'FN' ]
    command_line_args = [ 'tests/data/i2b2_2016_track-1_gold' ,
                          'tests/data/i2b2_2016_track-1_test' ]
    args = args_and_configs.get_arguments( command_line_args )
    sample_config = [ { 'type' : 'Sentence' ,
                        'XPath' : './/type:Sentence' } ,
                      { 'type' : 'Sentence' ,
                        'XPath' : './/type4:Sentence' } ]
    file_list = [ 'a.xml' , 'b.xml' ]
    return( score_card , args , sample_config , file_list )


def test_unique_score_key_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_list = initialize_for_print_summary_test()
    args.by_type = True
    ##
    scoring_metrics.print_score_summary( score_card , file_list ,
                                         sample_config , sample_config ,
                                         args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'aggregate' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'Sentence' , '1.0' , '1.0' , '0.0' , '2.0' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out


def test_by_file_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_list = initialize_for_print_summary_test()
    args.by_file = True
    ##
    scoring_metrics.print_score_summary( score_card , file_list ,
                                         sample_config , sample_config ,
                                         args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'aggregate' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'a.xml' , '1.0' , '0.0' , '0.0' , '1.0' ]  ,
                        [ 'b.xml' , '0.0' , '1.0' , '0.0' , '1.0' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out
    
    

def changing_delim_to_variable( capsys , new_delim ):
    score_card , args , sample_config , \
      file_list = initialize_for_print_summary_test()
    ##
    scoring_metrics.print_score_summary( score_card , file_list ,
                                         sample_config , sample_config ,
                                         args )
    default_delim_out, err = capsys.readouterr()
    ##
    converted_out = re.sub( args.delim ,
                            new_delim ,
                            default_delim_out )
    args.delim = new_delim
    scoring_metrics.print_score_summary( score_card , file_list ,
                                         sample_config , sample_config ,
                                         args )
    new_delim_out, err = capsys.readouterr()
    assert converted_out == new_delim_out
    if( new_delim == '\t' ):
        assert default_delim_out == new_delim_out
    else:
        assert default_delim_out != new_delim_out


def test_keeping_delim_as_tab( capsys ):
    changing_delim_to_variable( capsys , '\t' )

def test_changing_delim_to_semicolon( capsys ):
    changing_delim_to_variable( capsys , ';' )

def test_changing_delim_to_pipe( capsys ):
    changing_delim_to_variable( capsys , '|' )

