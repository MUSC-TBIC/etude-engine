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
    new_types = score_card[ 'exact' ].keys()
    assert test_type not in new_types
    scoring_metrics.add_missing_fields( score_card )
    score_types = score_card.keys()
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
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ 'a.xml' , 0 , 1 , 'Sentence' , 'TP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ 'b.xml' , 0 , 1 , 'Sentence' , 'FP' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ 'a.xml' , 0 , 1 , 'Sentence' , 'FN' ]
    score_card[ 'exact' ].loc[ score_card[ 'exact' ].shape[ 0 ] ] = \
      [ 'b.xml' , 0 , 1 , 'Sentence' , 'FN' ]
    command_line_args = [ '--reference-input' , 'tests/data/i2b2_2016_track-1_reference' ,
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
                                         fuzzy_flag = 'exact' ,
                                         args = args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ 'exact' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'micro-average' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'Sentence' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'macro-average by type' , '1.0' , '1.0' , '0.0' , '2.0' ] ]
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
                                         fuzzy_flag = 'exact' ,
                                         args = args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ 'exact' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'micro-average' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'Sentence' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'Sentence x a.xml' , '1.0' , '0.0' , '0.0' , '1.0' ] ,
                        [ 'Sentence x b.xml' , '0.0' , '1.0' , '0.0' , '1.0' ] ,
                        [ 'macro-average by type' , '1.0' , '1.0' , '0.0' , '2.0' ] ]
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
                                         fuzzy_flag = 'exact' ,
                                         args = args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ 'exact' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'micro-average' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'a.xml' , '1.0' , '0.0' , '0.0' , '1.0' ]  ,
                        [ 'b.xml' , '0.0' , '1.0' , '0.0' , '1.0' ] ,
                        [ 'macro-average by file' , '1.0' , '1.0' , '0.0' , '2.0' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out


def test_by_file_f_metrics( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.metrics_list = [ 'Precision' , 'Recall' , 'F1' ]
    args.by_file = True
    ##
    scoring_metrics.print_score_summary( score_card , file_mapping ,
                                         sample_config , sample_config ,
                                         fuzzy_flag = 'exact' ,
                                         args = args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ 'exact' , 'Precision' , 'Recall' , 'F1' ] ,
                        [ 'micro-average' , '0.5' , '0.333333333333' , '0.4' ] ,
                        [ 'a.xml' , '1.0' , '0.5' , '0.666666666667' ]  ,
                        [ 'b.xml' , '0.0' , '0.0' , '0.0' ] ,
                        [ 'macro-average by file' , '0.5' , '0.25' , '0.333333333333' ] ]
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
                                         fuzzy_flag = 'exact' ,
                                         args = args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ 'exact' , 'TP' , 'FP' , 'TN' , 'FN' ] ,
                        [ 'micro-average' , '1.0' , '1.0' , '0.0' , '2.0' ] ,
                        [ 'a.xml' , '1.0' , '0.0' , '0.0' , '1.0' ] ,
                        [ 'a.xml x Sentence' , '1.0' , '0.0' , '0.0' , '1.0' ] ,
                        [ 'b.xml' , '0.0' , '1.0' , '0.0' , '1.0' ]  ,
                        [ 'b.xml x Sentence' , '0.0' , '1.0' , '0.0' , '1.0' ] ,
                        [ 'macro-average by file' , '1.0' , '1.0' , '0.0' , '2.0' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out


def test_by_file_and_type_to_reference_file_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.metrics_list = [ 'Precision' , 'Recall' , 'F1' ]
    args.by_file_and_type = True
    ##
    try:
        args.reference_out = tempfile.mkdtemp()
        scoring_metrics.print_score_summary( score_card , file_mapping ,
                                             sample_config , sample_config ,
                                             fuzzy_flag = 'exact' ,
                                             args = args )
        ##
        for filename in [ 'a.xml' , 'b.xml' ]:
            ref_file = '{}/{}'.format( 'tests/data/print_summary_reference_out' ,
                                       filename )
            test_file = '{}/{}'.format( args.reference_out ,
                                        filename )
            with open( ref_file , 'r' ) as fp:
                reference_json = json.load( fp )
            with open( test_file , 'r' ) as fp:
                reloaded_json = json.load( fp )
            assert reference_json == reloaded_json
            os.remove( test_file )
    finally:
        ## If this returns a OSError: [Errno 66] Directory not empty,
        ## then the asserts in the previous try statement failed. Treat
        ## it as a test failure not a try/catch problem.
        os.rmdir( args.reference_out )


def test_by_file_and_type_to_test_file_summary_stats( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.metrics_list = [ 'Precision' , 'Recall' , 'F1' ]
    args.by_file_and_type = True
    ##
    try:
        args.test_out = tempfile.mkdtemp()
        scoring_metrics.print_score_summary( score_card , file_mapping ,
                                             sample_config , sample_config ,
                                             fuzzy_flag = 'exact' ,
                                             args = args )
        ##
        for filename in [ 'a.xml' , 'b.xml' ]:
            ref_file = '{}/{}'.format( 'tests/data/print_summary_test_out' ,
                                       filename )
            test_file = '{}/{}'.format( args.test_out ,
                                        filename )
            with open( ref_file , 'r' ) as fp:
                reference_json = json.load( fp )
            with open( test_file , 'r' ) as fp:
                reloaded_json = json.load( fp )
            assert reference_json == reloaded_json
            os.remove( test_file )
    finally:
        ## If this returns a OSError: [Errno 66] Directory not empty,
        ## then the asserts in the previous try statement failed. Treat
        ## it as a test failure not a try/catch problem.
        os.rmdir( args.test_out )


def test_csv_out_header_creation( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.metrics_list = [ 'Precision' , 'Recall' , 'F1' ]
    ##
    try:
        tmp_descriptor, tmp_file = tempfile.mkstemp()
        os.close( tmp_descriptor )
        args.csv_out = tmp_file
        os.remove( args.csv_out )
        assert os.path.exists( args.csv_out ) == False
        scoring_metrics.print_score_summary( score_card , file_mapping ,
                                             sample_config , sample_config ,
                                             fuzzy_flag = 'exact' ,
                                             args = args )
        ##
        expected_values = [ 'FuzzyFlag' , 'ClassType' , 'Class' , 'SubClassType' , 'SubClass' ,
                            'Precision' , 'Recall' , 'F1' ]
        with open( tmp_file , 'r' ) as fp:
            head_line = fp.readline().strip()
            assert head_line == args.delim.join( '{}'.format( m ) for m in expected_values )
    finally:
        os.remove( tmp_file )


def test_csv_out_append_if_present( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.metrics_list = [ 'TP' , 'FP' , 'Precision' , 'Recall' , 'F1' ]
    ## This flavor of named temporary file is automatically created, which should
    ## trigger the logic branching that tests if the csv_out file is already
    ## present
    with tempfile.NamedTemporaryFile() as tmpfile_handle:
        args.csv_out = tmpfile_handle.name
        scoring_metrics.print_score_summary( score_card , file_mapping ,
                                             sample_config , sample_config ,
                                             fuzzy_flag = 'exact' ,
                                             args = args )
        ##
        expected_values = [ 'exact' , 'micro-average' , '' , '' , '' ,
                            '1.0' , '1.0' , '0.5' , '0.333333333333' , '0.4' ]
        with open( tmpfile_handle.name , 'r' ) as fp:
            head_line = fp.readline().strip()
            assert head_line == args.delim.join( '{}'.format( m ) for m in expected_values )


def changing_delim_to_variable( capsys , new_delim ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    ##
    scoring_metrics.print_score_summary( score_card , file_mapping ,
                                         sample_config , sample_config ,
                                         fuzzy_flag = 'exact' ,
                                         args = args )
    default_delim_out, err = capsys.readouterr()
    ##
    converted_out = re.sub( args.delim ,
                            new_delim ,
                            default_delim_out )
    args.delim = new_delim
    scoring_metrics.print_score_summary( score_card , file_mapping ,
                                         sample_config , sample_config ,
                                         fuzzy_flag = 'exact' ,
                                         args = args )
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

def TODO_aggregate_summary_counts( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    ##
    scoring_metrics.print_counts_summary( type_counts = score_card[ 'exact' ] ,
                                          file_mapping = file_mapping ,
                                          test_config = sample_config ,
                                          args = args )
    agg_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'Sentence' ] ,
                        [ 'micro-average' , '4' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    agg_out = agg_out.strip()
    expected_out = expected_out.strip()
    assert agg_out == expected_out

def TODO_by_file_summary_counts( capsys ):
    score_card , args , sample_config , \
      file_mapping = initialize_for_print_summary_test()
    args.by_file = True
    ##
    scoring_metrics.print_counts_summary( type_counts = score_card[ 'exact' ] ,
                                          file_mapping = file_mapping ,
                                          test_config = sample_config ,
                                          args = args )
    by_type_out, err = capsys.readouterr()
    ##
    expected_values = [ [ '#########' , 'Sentence' ] ,
                        [ 'micro-average' , '4' ] ,
                        [ 'a.xml' , '2' ] ,
                        [ 'b.xml' , '2' ] ]
    for expected_values in expected_values:
        print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
    expected_out, err = capsys.readouterr()
    by_type_out = by_type_out.strip()
    expected_out = expected_out.strip()
    assert by_type_out == expected_out


def test_evaluate_positions_copy_match():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , reference_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    reference_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = reference_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    test_om = reference_om
    test_ss = reference_ss
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_empty_reference_ss():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    reference_om = {}
    reference_ss = {}
    raw_content , test_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = reference_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'FP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_empty_test_ss():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , reference_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    reference_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = reference_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    test_om = {}
    test_ss = {}
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'FN' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_empty_dictionaries():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    reference_om = {}
    reference_ss = {}
    test_om = {}
    test_ss = {}
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_tweak_annotation_dictionary_heed_whitespace():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , reference_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data )
    reference_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = reference_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_om = reference_om
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = reference_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_ss[ '87' ][ 0 ][ 'begin_pos' ] = '73'
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 73 , 97 , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_tweak_annotation_dictionary_ignore_whitespace():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , reference_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data ,
                                     skip_chars = '[\s]' )
    reference_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = reference_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_om = reference_om
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = reference_om ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    test_ss[ '87' ][ 0 ][ 'begin_pos' ] = '73'
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 70 , 80 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2006 , 2011 , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def prepare_evaluate_positions_structs():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , reference_om = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data ,
                                     skip_chars = '[\s]' )
    reference_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = reference_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    test_om = reference_om
    test_ss = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = test_om ,
                                               annotation_path = \
                                                  './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    return ingest_file , reference_ss , test_ss


def test_evaluate_positions_missing_mapped_keys_with_heed_whitespace():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    del reference_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    del reference_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    del test_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    del test_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_missing_reference_begin_mapped_key():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    del reference_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 70 , 80 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2006 , 2011 , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_missing_reference_end_mapped_key():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    del reference_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 70 , 80 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2006 , 2011 , 'DateTime' , 'FP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_missing_test_begin_mapped_key():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    del test_ss[ "2404" ][ 0 ][ "begin_pos_mapped" ]
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 70 , 80 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2006 , 2011 , 'DateTime' , 'FN' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_missing_test_end_mapped_key():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    del test_ss[ "2404" ][ 0 ][ "end_pos_mapped" ]
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = True )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 70 , 80 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2006 , 2011 , 'DateTime' , 'FN' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_partial_v_fully_FP_conflict():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card( fuzzy_flags = [ 'fully-contained' , 'partial' ] )
    ingest_file = '137-02.xml'
    ref_ss_filename = 'tests/data/strict_sets/partial_fully-contained_mismatch_reference_ss.json'
    test_ss_filename = 'tests/data/strict_sets/partial_fully-contained_mismatch_test_ss.json'
    with open( ref_ss_filename , 'r' ) as fp:
        reference_ss = json.load( fp )
    with open( test_ss_filename , 'r' ) as fp:
        test_ss = json.load( fp )
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        fuzzy_flag = 'fully-contained' ,
                                        use_mapped_chars = True )
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        fuzzy_flag = 'partial' ,
                                        use_mapped_chars = True )
    ##
    assert_frame_equal( score_card[ 'fully-contained' ] ,
                        score_card[ 'partial' ] )


#############################################
## Test nested annotation entries
#############################################


def test_evaluate_positions_nested_annotations_reference_first_match():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    ##
    new_entry = text_extraction.create_annotation_entry( begin_pos = "87" ,
                                                         begin_pos_mapped = "70" ,
                                                         end_pos = "97" ,
                                                         end_pos_mapped = "80" ,
                                                         raw_text = None ,
                                                         tag_name = "Age" )
    reference_ss[ "87" ].append( new_entry )
    ##
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'Age' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_nested_annotations_reference_second_match():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    ##
    new_entry = text_extraction.create_annotation_entry( begin_pos = "87" ,
                                                         begin_pos_mapped = "70" ,
                                                         end_pos = "97" ,
                                                         end_pos_mapped = "80" ,
                                                         raw_text = None ,
                                                         tag_name = "Age" )
    reference_ss[ "87" ].append( new_entry )
    ##
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'Age' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_nested_annotations_test():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    ##
    new_entry = text_extraction.create_annotation_entry( begin_pos = "87" ,
                                                         begin_pos_mapped = "70" ,
                                                         end_pos = "97" ,
                                                         end_pos_mapped = "80" ,
                                                         raw_text = None ,
                                                         tag_name = "Age" )
    test_ss[ "87" ].append( new_entry )
    ##
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'Age' , 'FP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )


def test_evaluate_positions_nested_annotations_reference_and_test():
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card()
    ingest_file , reference_ss , test_ss = \
      prepare_evaluate_positions_structs()
    ##
    new_entry = text_extraction.create_annotation_entry( begin_pos = "87" ,
                                                         begin_pos_mapped = "70" ,
                                                         end_pos = "97" ,
                                                         end_pos_mapped = "80" ,
                                                         raw_text = None ,
                                                         tag_name = "Age" )
    reference_ss[ "87" ].append( new_entry )
    test_ss[ "87" ].append( new_entry )
    ##
    scoring_metrics.evaluate_positions( ingest_file ,
                                        confusion_matrix ,
                                        score_card ,
                                        reference_ss = reference_ss ,
                                        test_ss = test_ss ,
                                        use_mapped_chars = False )
    ##
    expected_score_card = scoring_metrics.new_score_card()
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 87 , 97 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ ingest_file , 2404 , 2410 , 'DateTime' , 'TP' ]
    assert_frame_equal( score_card[ 'exact' ] ,
                        expected_score_card[ 'exact' ] )




#############################################
## Test exact, overlapping, and fully contained
#############################################

def prepare_evaluate_positions_offset_alignment( test_filename ):
    reference_filename = 'tests/data/offset_matching/the_doctors_age_reference.xmi'
    namespaces = { 'cas' :
                   "http:///uima/cas.ecore" ,
                   'custom' :
                   "http:///webanno/custom.ecore" }
    document_data = dict( tag_xpath = './cas:Sofa' ,
                          content_attribute = 'sofaString' )
    raw_content , reference_om = \
      text_extraction.extract_chars( ingest_file = reference_filename ,
                                     namespaces = namespaces ,
                                     document_data = document_data ,
                                     skip_chars = '[\s]' )
    test_om = reference_om
    tag_set = { 'DateTime' : './custom:PHI[@Time="DateTime"]' ,
                'Age' : './custom:PHI[@Time="Age"]' }
    reference_ss = {}
    test_ss = {}
    for tag_name in tag_set:
        reference_ss.update( 
         text_extraction.extract_annotations_xml( reference_filename ,
                                                  offset_mapping = reference_om ,
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
    return reference_ss , test_ss


def prepare_offset_alignment_score_cards( filename , reference_ss , test_ss ):
    fuzzy_flags = [ 'exact' ,
                    'fully-contained' ,
                    'partial' ]
    confusion_matrix = {}
    score_card = scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    for fuzzy_flag in fuzzy_flags:
        scoring_metrics.evaluate_positions( filename ,
                                            confusion_matrix ,
                                            score_card ,
                                            reference_ss ,
                                            test_ss ,
                                            fuzzy_flag = fuzzy_flag ,
                                            use_mapped_chars = True )
    return score_card , fuzzy_flags


def test_exact_match_overlap():
    test_filename = 'tests/data/offset_matching/the_doctors_age_reference.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss == test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'exact' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_contained_on_both_sides():
    test_filename = 'tests/data/offset_matching/the_doctors_age_contained_on_both_sides.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 30 , 'EOF' , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ].loc[ expected_score_card[ 'fully-contained' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'fully-contained' ].loc[ expected_score_card[ 'fully-contained' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'fully-contained' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_contained_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_contained_on_left.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 30 , 48 , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ].loc[ expected_score_card[ 'fully-contained' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'fully-contained' ].loc[ expected_score_card[ 'fully-contained' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'fully-contained' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_contained_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_contained_on_right.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 'EOF' , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ].loc[ expected_score_card[ 'fully-contained' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'fully-contained' ].loc[ expected_score_card[ 'fully-contained' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'fully-contained' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_partial_on_both_sides():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_both_sides.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 40 , 43 , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_partial_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_left.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 40 , 48 , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_partial_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_right.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 43 , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_partial_on_left_contained_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_left_contained_on_right.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 40 , 'EOF' , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_partial_on_right_contained_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_on_right_contained_on_left.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 30 , 43 , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'partial' ].loc[ expected_score_card[ 'partial' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_partial_leftside_outlier():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_leftside_outlier.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 30 , 31 , 'DateTime' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'exact' ]
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_partial_rightside_outlier():
    test_filename = 'tests/data/offset_matching/the_doctors_age_partial_rightside_outlier.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'TP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 23 , 26 , 'Age' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'exact' ]
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_type_mismatch():
    test_filename = 'tests/data/offset_matching/the_doctors_age_type_mismatch.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'DateTime' , 'FP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'Age' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'exact' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_type_mismatch_contained_on_left():
    test_filename = 'tests/data/offset_matching/the_doctors_age_type_mismatch_contained_on_left.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'DateTime' , 'FP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 30 , 48 , 'Age' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'exact' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )


def test_match_overlap_type_mismatch_contained_on_right():
    test_filename = 'tests/data/offset_matching/the_doctors_age_type_mismatch_contained_on_right.xmi'
    reference_ss , test_ss = \
        prepare_evaluate_positions_offset_alignment( test_filename = test_filename )
    assert reference_ss != test_ss
    ##
    system_score_card , fuzzy_flags = \
      prepare_offset_alignment_score_cards( test_filename ,
                                            reference_ss ,
                                            test_ss )
    expected_score_card = \
      scoring_metrics.new_score_card( fuzzy_flags = fuzzy_flags )
    ## exact match only
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'Age' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 19 , 21 , 'DateTime' , 'FP' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 48 , 'DateTime' , 'FN' ]
    expected_score_card[ 'exact' ].loc[ expected_score_card[ 'exact' ].shape[ 0 ] ] = \
      [ test_filename , 32 , 'EOF' , 'Age' , 'FP' ]
    ## fully-contained matches
    expected_score_card[ 'fully-contained' ] = expected_score_card[ 'exact' ]
    ## overlapping matches
    expected_score_card[ 'partial' ] = expected_score_card[ 'exact' ]
    ##
    for fuzzy_flag in fuzzy_flags:
        assert_frame_equal( system_score_card[ fuzzy_flag ] ,
                            expected_score_card[ fuzzy_flag ] )



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

