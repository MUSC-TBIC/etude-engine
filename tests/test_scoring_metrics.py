import sys
import re

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


#############################################
## Test print_count_summary()
#############################################

def test_aggregate_summary_counts( capsys ):
    score_card , args , sample_config , \
      file_list = initialize_for_print_summary_test()
    ##
    scoring_metrics.print_counts_summary( type_counts = score_card ,
                                          file_list = file_list ,
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
      file_list = initialize_for_print_summary_test()
    args.by_file = True
    ##
    scoring_metrics.print_counts_summary( type_counts = score_card ,
                                          file_list = file_list ,
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
                                          test_ss = test_ss ,
                                          ignore_whitespace = False )
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
                                          test_ss = test_ss ,
                                          ignore_whitespace = False )
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
                                          test_ss = test_ss ,
                                          ignore_whitespace = False )
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



