
import os
import tempfile

import json

import args_and_configs
import text_extraction

#############################################
## Test extracting various patterns
#############################################

def test_extracting_datetime_from_0005_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    strict_starts = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    expected_output = \
      { '2404' :  [ { 'type': 'DateTime' ,
                      'begin_pos': '2404' ,
                      'end_pos': '2410' ,
                      'raw_text': None } ] ,
        '87' : [ { 'type': 'DateTime' ,
                   'begin_pos': '87' ,
                   'end_pos': '97' ,
                   'raw_text': None } ]
      }
    assert strict_starts == expected_output

def test_default_namespace_same_as_empty():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    strict_starts_default = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    strict_starts_empty = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  namespaces = [] ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    assert strict_starts_default == strict_starts_empty


def test_extracting_sentences_from_0005_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    config_file = 'config/uima_sentences.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    strict_starts = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  namespaces = namespaces ,
                                                  annotation_path = \
                                                      './/type:Sentence' ,
                                                  tag_name = 'Sentence' ,
                                                  begin_attribute = 'begin' ,
                                                  end_attribute = 'end' )
    assert strict_starts == {}


def test_extracting_sentences_from_reference_standard():
    ingest_file = 'tests/data/sentences/992321.sentences.xmi'
    config_file = 'config/uima_sentences.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    strict_starts = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  namespaces = namespaces ,
                                                  annotation_path = \
                                                      './/type4:Sentence' ,
                                                  tag_name = 'Sentence' ,
                                                  begin_attribute = 'begin' ,
                                                  end_attribute = 'end' )
    assert len( strict_starts ) == 113


def test_extracting_sentences_from_WebAnno():
    ingest_file = 'tests/data/sentences/992321.sentences.WebAnno.xmi'
    config_file = 'config/uima_sentences.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    strict_starts = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  namespaces = namespaces ,
                                                  annotation_path = \
                                                      './/type4:Sentence' ,
                                                  tag_name = 'Sentence' ,
                                                  begin_attribute = 'begin' ,
                                                  end_attribute = 'end' )
    assert len( strict_starts ) == 45


def test_extracting_sentences_from_CTAKES4_OpenNLP1_8():
    ingest_file = 'tests/data/sentences/992321-OUT.xmi'
    config_file = 'config/uima_sentences.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    strict_starts = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  namespaces = namespaces ,
                                                  annotation_path = \
                                                      './/type:Sentence' ,
                                                  tag_name = 'Sentence' ,
                                                  begin_attribute = 'begin' ,
                                                  end_attribute = 'end' )
    assert len( strict_starts ) == 82


#############################################
## Test writing to disk
#############################################
    
def test_writing_dictionary_for_datetime_from_0005_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    strict_starts = \
      text_extraction.extract_annotations_kernel( ingest_file ,
                                                  offset_mapping = {} ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    expected_output = \
      { '2404' :  [ { 'type': 'DateTime' ,
                      'begin_pos': '2404' ,
                      'end_pos': '2410' ,
                      'raw_text': None } ] ,
        '87' : [ { 'type': 'DateTime' ,
                   'begin_pos': '87' ,
                   'end_pos': '97' ,
                   'raw_text': None } ]
      }
    with tempfile.NamedTemporaryFile() as tmpfile_handle:
        assert os.path.exists( tmpfile_handle.name )
        text_extraction.write_annotations_to_disk( strict_starts ,
                                                   tmpfile_handle.name )
        reloaded_json = json.load( tmpfile_handle )
        assert reloaded_json == expected_output
        assert os.path.exists( tmpfile_handle.name )
    assert os.path.exists( tmpfile_handle.name ) == False


## TODO - add tests for ingore_whitespace == True | False
def test_of_presaved_dictionary_for_complex_patterns():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    presaved_file = 'tests/data/i2b2_2016_track-1_gold_out/0005_gs.xml'
    config_file = 'config/i2b2_2016_track-1.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    with open( presaved_file , 'r' ) as fp:
        reloaded_json = json.load( fp )
    strict_starts = \
      text_extraction.extract_annotations( ingest_file ,
                                           namespaces = namespaces ,
                                           document_data = {} ,
                                           patterns = patterns ,
                                           out_file = None )
    assert reloaded_json[ 'annotations' ] == strict_starts


def test_of_identity_read_write_of_dictionary_for_complex_patterns():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    config_file = 'config/i2b2_2016_track-1.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    with tempfile.NamedTemporaryFile() as tmpfile_handle:
        assert os.path.exists( tmpfile_handle.name )
        strict_starts = \
          text_extraction.extract_annotations( ingest_file ,
                                               namespaces = namespaces ,
                                               document_data = {} ,
                                               patterns = patterns ,
                                               out_file = tmpfile_handle.name )
        reloaded_json = json.load( tmpfile_handle )
        assert reloaded_json[ 'annotations' ] == strict_starts
        assert os.path.exists( tmpfile_handle.name )
    assert os.path.exists( tmpfile_handle.name ) == False

#############################################
## Test extracting document contents
#############################################

def test_extracting_doc_content_from_0005_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_gold/0005_gs.xml'
    test_dd = dict( cdata_xpath = './TEXT' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = test_dd ,
                                     out_file = None )
    expected_output = { '0': None ,
                        '1': None ,
                        '2': '0', '3': '1', '4': '2', '5': '3', '6': '4',
                        '7': '5', '8': '6', '9': '7',
                        '10': None , '11': None }
    assert offset_mapping == expected_output

def test_extracting_doc_content_from_995723_sentences_xmi():
    ingest_file = 'tests/data/sentences/995723.sentences.xmi'
    test_dd = dict( tag_xpath = './cas:Sofa' ,
                    content_attribute = 'sofaString' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = { 'cas' :
                                                    "http:///uima/cas.ecore" } ,
                                     document_data = test_dd ,
                                     out_file = None )
    expected_output = { '0': '0' , '1': '1' , '2': '2' , '3': '3' , '4': '4' ,
                        '5': '5' , '6': '6' , '7': '7' }
    assert offset_mapping == expected_output

    
