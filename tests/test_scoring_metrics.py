import os
import sys
import re
import tempfile

import json

import args_and_configs
import scoring_metrics
import text_extraction

from pandas.testing import assert_frame_equal

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
## Test print_score_summary()
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
    command_line_args = [ '--gold-input' , 'tests/data/i2b2_2016_track-1_gold' ,
                          '--test-input' , 'tests/data/i2b2_2016_track-1_test' ]
    args = args_and_configs.get_arguments( command_line_args )
    sample_config = [ { 'type' : 'Sentence' ,
                        'XPath' : './/type:Sentence' } ,
                      { 'type' : 'Sentence' ,
                        'XPath' : './/type4:Sentence' } ]
    file_mapping = { 'a.xml': 'a.xml' , 'b.xml': 'b.xml' }
    return( score_card , args , sample_config , file_mapping )


def test_unique_score_key_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.by_type = True
    ##
    scoring_metrics.print_score_summary( score_card , file_mapping ,
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


def test_by_type_and_file_score_key_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.by_type_and_file = True
    ##
    scoring_metrics.print_score_summary( score_card , file_mapping ,
                                         sample_config , sample_config ,
                                         args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'aggregate' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'Sentence' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'Sentence x a.xml' , '1.0' , '0.0' , '0.0' , '1.0' ] ,
                        [ 'Sentence x b.xml' , '0.0' , '1.0' , '0.0' , '1.0' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out


def test_by_file_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.by_file = True
    ##
    scoring_metrics.print_score_summary( score_card , file_mapping ,
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


def test_by_file_and_type_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.by_file_and_type = True
    ##
    scoring_metrics.print_score_summary( score_card , file_mapping ,
                                         sample_config , sample_config ,
                                         args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'aggregate' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'a.xml' , '1.0' , '0.0' , '0.0' , '1.0' ] ,
                        [ 'a.xml x Sentence' , '1.0' , '0.0' , '0.0' , '1.0' ] ,
                        [ 'b.xml' , '0.0' , '1.0' , '0.0' , '1.0' ]  ,
                        [ 'b.xml x Sentence' , '0.0' , '1.0' , '0.0' , '1.0' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out
    
    

def changing_delim_to_variable( capsys , new_delim ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    ##
    scoring_metrics.print_score_summary( score_card , file_mapping ,
                                         sample_config , sample_config ,
                                         args )
    default_delim_out, err = capsys.readouterr()
    ##
    converted_out = re.sub( args.delim ,
                            new_delim ,
                            default_delim_out )
    args.delim = new_delim
    scoring_metrics.print_score_summary( score_card , file_mapping ,
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


#############################################
## Test print_count_summary()
#############################################

def test_aggregate_summary_counts( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    ##
    scoring_metrics.print_counts_summary( type_counts = score_card ,
                                          file_mapping = file_mapping ,
                                          test_config = sample_config ,
                                          args = args )
    agg_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'Sentence' ] ,
                        [ 'aggregate' , '4' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    agg_out = agg_out.strip()
    expected_out = expected_out.strip()
    assert agg_out == expected_out

def test_by_file_summary_counts( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.by_file = True
    ##
    scoring_metrics.print_counts_summary( type_counts = score_card ,
                                          file_mapping = file_mapping ,
                                          test_config = sample_config ,
                                          args = args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'Sentence' ] ,
                        [ 'aggregate' , '4' ] ,
                        [ 'a.xml' , '2' ] ,
                        [ 'b.xml' , '2' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out


def test_evaluate_positions_copy_match():
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , gold_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    gold_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = gold_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    test_om = gold_om
    test_ss = gold_ss
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '87' , '97' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2404' , '2410' , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_empty_gold_ss():
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    gold_om = {}
    gold_ss = {}
    raw_content , test_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = gold_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '87' , '97' , 'DateTime' , 'FP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2404' , '2410' , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_empty_test_ss():
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , gold_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    gold_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = gold_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    test_om = {}
    test_ss = {}
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '87' , '97' , 'DateTime' , 'FN' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2404' , '2410' , 'DateTime' , 'FN' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_empty_dictionaries():
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    gold_om = {}
    gold_ss = {}
    test_om = {}
    test_ss = {}
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_tweak_annotation_dictionary_heed_whitespace():
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , gold_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    gold_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = gold_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_om = gold_om
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = gold_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_ss[ '87' ][ 0 ][ 'begin_pos' ] = '73'
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '87' , '97' , 'DateTime' , 'FN' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2404' , '2410' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '73' , '97' , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_tweak_annotation_dictionary_ignore_whitespace():
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , gold_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    gold_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = gold_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_om = gold_om
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = gold_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_ss[ '87' ][ 0 ][ 'begin_pos' ] = '73'
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '70' , '80' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2006' , '2011' , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card , expected_score_card )


def prepare_evaluate_positions_missing_mapped_keys():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , gold_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    gold_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = gold_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    test_om = gold_om
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = test_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    return ingest_file , gold_ss , test_ss


def test_evaluate_positions_missing_mapped_keys_with_heed_whitespace():
    score_card = scoring_metrics.new_score_card()
    ingest_file , gold_ss , test_ss = \
      prepare_evaluate_positions_missing_mapped_keys()
    del gold_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    del gold_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    del test_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    del test_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '87' , '97' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2404' , '2410' , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_missing_gold_begin_mapped_key():
    score_card = scoring_metrics.new_score_card()
    ingest_file , gold_ss , test_ss = \
      prepare_evaluate_positions_missing_mapped_keys()
    del gold_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '70' , '80' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2006' , '2011' , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_missing_gold_end_mapped_key():
    score_card = scoring_metrics.new_score_card()
    ingest_file , gold_ss , test_ss = \
      prepare_evaluate_positions_missing_mapped_keys()
    del gold_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '70' , '80' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2006' , '2011' , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_missing_test_begin_mapped_key():
    score_card = scoring_metrics.new_score_card()
    ingest_file , gold_ss , test_ss = \
      prepare_evaluate_positions_missing_mapped_keys()
    del test_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '70' , '80' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2006' , '2011' , 'DateTime' , 'FN' ]
    assert_frame_equal( score_card , expected_score_card )


def test_evaluate_positions_missing_test_end_mapped_key():
    score_card = scoring_metrics.new_score_card()
    ingest_file , gold_ss , test_ss = \
      prepare_evaluate_positions_missing_mapped_keys()
    del test_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    score_card = \
      scoring_metrics.evaluate_positions( ingest_file ,
                                          score_card ,
                                          gold_ss = gold_ss ,
                                          test_ss = test_ss ,
                                          ignore_whitespace = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '70' , '80' , 'DateTime' , 'TP' ]
    expected_score_card.loc[ expected_score_card.shape[ 0 ] ] = \
      [ ingest_file , '2006' , '2011' , 'DateTime' , 'FN' ]
    assert_frame_equal( score_card , expected_score_card )


#############################################
## Test exact, overlapping, and fully contained
#############################################

def prepare_evaluate_positions_offset_alignment( test_filename ):
    gold_filename = 'tests/data/offset_matching/the_doctors_age_gold.xmi'
    namespaces = { 'cas' :
                   "http:///uima/cas.ecore" ,
                   'custom' :
                   "http:///webanno/custom.ecore" }
    document_data = dict( tag_xpath = './cas:Sofa' ,
                          content_attribute = 'sofaString' )
    raw_content , gold_om = \
      text_extraction.extract_chars( ingest_file = gold_filename ,
                                     namespaces = namespaces ,
                                     document_data = document_data )
    test_om = gold_om
    tag_set = { 'DateTime' : './custom:PHI[@Time="DateTime"]' ,
                'Age' : './custom:PHI[@Time="Age"]' }
    gold_ss = {}
    test_ss = {}
    for tag_name in tag_set:
        gold_ss.update( 
         text_extraction.extract_annotations_xml( gold_filename ,
                                                  offset_mapping = gold_om ,
                                                  annotation_path = tag_set[ tag_name ] ,
                                                  tag_name = tag_name ,
                                                  namespaces = namespaces ,
                                                  begin_attribute = 'begin' ,
                                                  end_attribute = 'end' ) )
        test_ss.update( 
         text_extraction.extract_annotations_xml( test_filename ,
                                                  offset_mapping = test_om ,
                                                  annotation_path = tag_set[ tag_name ] ,
                                                  tag_name = tag_name ,
                                                  namespaces = namespaces ,
                                                  begin_attribute = 'begin' ,
                                                  end_attribute = 'end' ) )
    with open( '/tmp/bob.txt' , 'w' ) as fp:
        import json
        json.dump( gold_ss , fp , indent = 4 )
        fp.write( '\n' )
        json.dump( test_ss , fp , indent = 4 )
    return gold_ss , test_ss

def test_exact_match_overlap():
    test_filename = 'tests/data/offset_matching/the_doctors_age_gold.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss == test_ss

def test_match_overlap_contained_on_both_sides():
    test_filename = 'tests/data/offset_matching/the_doctors_age_contained_on_both_sides.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_contained_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_contained_on_left.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_contained_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_contained_on_right.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_partial_on_both_sides():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_both_sides.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_partial_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_left.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_partial_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_right.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_partial_on_left_contained_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_left_contained_on_right.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_partial_on_right_contained_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_right_contained_on_left.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_type_mismatch():
    test_filename = 'tests/data/offset_matching/the_doctors_age_type_mismatch.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_type_mismatch_contained_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_type_mismatch_contained_on_left.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss

def test_match_overlap_type_mismatch_contained_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_type_mismatch_contained_on_right.xmi'
    gold_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert gold_ss != test_ss



#############################################
## Test augmenting dictionaries on disk
#############################################

def test_empty_path_recursive_deep_key_value_pair():
    base_dict = {}
    reference_dict = { 'hello' : 'world' }
    base_dict = scoring_metrics.recursive_deep_key_value_pair( base_dict ,
                                                               [] ,
                                                               'hello' ,
                                                               'world' )
    assert base_dict == reference_dict

def test_one_deep_path_recursive_deep_key_value_pair():
    base_dict = {}
    reference_dict = { 'foobar' : { 'hello' : 'world' } }
    base_dict = scoring_metrics.recursive_deep_key_value_pair( base_dict ,
                                                               [ 'foobar' ] ,
                                                               'hello' ,
                                                               'world' )
    assert base_dict == reference_dict


def test_two_deep_path_recursive_deep_key_value_pair():
    base_dict = {}
    reference_dict = { 'foo' : { 'bar' : { 'hello' : 'world' } } }
    base_dict = scoring_metrics.recursive_deep_key_value_pair( base_dict ,
                                                               [ 'foo' , 'bar' ] ,
                                                               'hello' ,
                                                               'world' )
    assert base_dict == reference_dict


def test_empty_path_dictionary_augmentation():
    base_dict = { 'Do not disturb' : [ 8 , 6 , 7, 5 , 3, 0 , 9 ] ,
                  'Thing 1' : 'Thing 2' }
    reference_dict = { 'Do not disturb' : [ 8 , 6 , 7, 5 , 3, 0 , 9 ] ,
                       'Thing 1' : 'Thing 2' ,
                       'hello' : 'world' }
    try:
        tmp_descriptor, tmp_file = tempfile.mkstemp()
        os.close( tmp_descriptor )
        with open( tmp_file , 'w' ) as fp:
            json.dump( base_dict , fp )
        scoring_metrics.update_output_dictionary( tmp_file ,
                                                  [] ,
                                                  [ 'hello' ] ,
                                                  [ 'world' ] )
        with open( tmp_file , 'r' ) as fp:
            test_dict = json.load( fp )
        assert test_dict == reference_dict
    finally:
        os.remove( tmp_file )


def test_one_deep_path_dictionary_augmentation():
    base_dict = { 'Do not disturb' : [ 8 , 6 , 7, 5 , 3, 0 , 9 ] ,
                  'Thing 1' : 'Thing 2' }
    reference_dict = { 'Do not disturb' : [ 8 , 6 , 7, 5 , 3, 0 , 9 ] ,
                       'Thing 1' : 'Thing 2' ,
                       'foobar' : { 'hello' : 'world' } }
    try:
        tmp_descriptor, tmp_file = tempfile.mkstemp()
        os.close( tmp_descriptor )
        with open( tmp_file , 'w' ) as fp:
            json.dump( base_dict , fp )
        scoring_metrics.update_output_dictionary( tmp_file ,
                                                  [ 'foobar' ] ,
                                                  [ 'hello' ] ,
                                                  [ 'world' ] )
        with open( tmp_file , 'r' ) as fp:
            test_dict = json.load( fp )
        assert test_dict == reference_dict
    finally:
        os.remove( tmp_file )


def test_two_deep_path_dictionary_augmentation():
    base_dict = { 'Do not disturb' : [ 8 , 6 , 7, 5 , 3, 0 , 9 ] ,
                  'Thing 1' : 'Thing 2' }
    reference_dict = { 'Do not disturb' : [ 8 , 6 , 7, 5 , 3, 0 , 9 ] ,
                       'Thing 1' : 'Thing 2' ,
                       'foo' : { 'bar' : { 'hello' : 'world' } } }
    try:
        tmp_descriptor, tmp_file = tempfile.mkstemp()
        os.close( tmp_descriptor )
        with open( tmp_file , 'w' ) as fp:
            json.dump( base_dict , fp )
        scoring_metrics.update_output_dictionary( tmp_file ,
                                                  [ 'foo' , 'bar' ] ,
                                                  [ 'hello' ] ,
                                                  [ 'world' ] )
        with open( tmp_file , 'r' ) as fp:
            test_dict = json.load( fp )
        assert test_dict == reference_dict
    finally:
        os.remove( tmp_file )

