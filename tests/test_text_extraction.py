
import os
import tempfile

import json

import args_and_configs
import text_extraction

#############################################
## Test extracting various plaintext patterns
#############################################

def test_plaintext_split_on_spaces():
    raw_content = 'Hello , world'
    strict_starts = \
      text_extraction.extract_annotations_plaintext( offset_mapping = {} ,
                                                     raw_content = raw_content ,
                                                     delimiter = ' ' ,
                                                     tag_name = 'Token' )
    expected_output = \
      { '0' :  [ { 'type': 'Token',
                   'end_pos': '5',
                   'raw_text': 'Hello',
                   'begin_pos': '0' } ] ,
        '6' : [ { 'type': 'Token' ,
                  'end_pos': '7' ,
                  'raw_text': ',' ,
                  'begin_pos': '6' } ] ,
        '8' : [ { 'type': 'Token' ,
                  'end_pos': '13' ,
                  'raw_text': 'world' ,
                  'begin_pos': '8' } ]
      }
    assert strict_starts == expected_output

def test_plaintext_split_on_spaces_with_final_space():
    raw_content = 'Hello , world  '
    strict_starts = \
      text_extraction.extract_annotations_plaintext( offset_mapping = {} ,
                                                     raw_content = raw_content ,
                                                     delimiter = ' ' ,
                                                     tag_name = 'Token' )
    expected_output = \
      { '0' :  [ { 'type': 'Token',
                   'end_pos': '5',
                   'raw_text': 'Hello',
                   'begin_pos': '0' } ] ,
        '6' : [ { 'type': 'Token' ,
                  'end_pos': '7' ,
                  'raw_text': ',' ,
                  'begin_pos': '6' } ] ,
        '8' : [ { 'type': 'Token' ,
                  'end_pos': '13' ,
                  'raw_text': 'world' ,
                  'begin_pos': '8' } ]
      }
    assert strict_starts == expected_output

def test_plaintext_split_on_spaces_with_initial_space():
    raw_content = '  Hello , world'
    strict_starts = \
      text_extraction.extract_annotations_plaintext( offset_mapping = {} ,
                                                     raw_content = raw_content ,
                                                     delimiter = ' ' ,
                                                     tag_name = 'Token' )
    expected_output = \
      { '2' :  [ { 'type': 'Token',
                   'end_pos': '7',
                   'raw_text': 'Hello',
                   'begin_pos': '2' } ] ,
        '8' : [ { 'type': 'Token' ,
                  'end_pos': '9' ,
                  'raw_text': ',' ,
                  'begin_pos': '8' } ] ,
        '10' : [ { 'type': 'Token' ,
                   'end_pos': '15' ,
                   'raw_text': 'world' ,
                   'begin_pos': '10' } ]
      }
    assert strict_starts == expected_output


#############################################
## Test extracting various xml patterns
#############################################

def test_extracting_datetime_from_0005_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    strict_starts = \
      text_extraction.extract_annotations_xml( ingest_file ,
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
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    strict_starts_default = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = {} ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    strict_starts_empty = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = {} ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  namespaces = {} ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    assert strict_starts_default == strict_starts_empty


def test_extracting_sentences_from_0005_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    config_file = 'config/uima_sentences.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    strict_starts = \
      text_extraction.extract_annotations_xml( ingest_file ,
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
      text_extraction.extract_annotations_xml( ingest_file ,
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
      text_extraction.extract_annotations_xml( ingest_file ,
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
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = {} ,
                                               namespaces = namespaces ,
                                               annotation_path = \
                                                   './/type:Sentence' ,
                                               tag_name = 'Sentence' ,
                                               begin_attribute = 'begin' ,
                                               end_attribute = 'end' )
    assert len( strict_starts ) == 82


## Passing attributes through


def test_extracting_no_optional_attributes():
    ingest_file = 'tests/data/013_Conditional_Problem.xmi'
    config_file = 'config/webanno_problems_allergies_xmi.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    strict_starts = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = {} ,
                                               annotation_path = \
                                                 './custom:Problems' ,
                                               tag_name = 'Problem' ,
                                               namespaces = namespaces ,
                                               begin_attribute = 'begin' ,
                                               end_attribute = 'end' ,
                                               optional_attributes = [] )
    expected_output = \
      { '181' :  [ { 'type': 'Problem' ,
                      'begin_pos': '181' ,
                      'end_pos': '188' ,
                      'raw_text': None } ] ,
        '218' : [ { 'type': 'Problem' ,
                   'begin_pos': '218' ,
                   'end_pos': '224' ,
                   'raw_text': None } ]
      }
    assert strict_starts == expected_output


def test_extracting_with_and_without_optional_attributes():
    ingest_file = 'tests/data/013_Conditional_Problem.xmi'
    config_file = 'config/webanno_problems_allergies_xmi.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    strict_starts_no_opt_attributes = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = {} ,
                                               annotation_path = \
                                                 './custom:Problems' ,
                                               tag_name = 'Problem' ,
                                               namespaces = namespaces ,
                                               begin_attribute = 'begin' ,
                                               end_attribute = 'end' ,
                                               optional_attributes = [] )
    strict_starts_with_opt_attributes = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = {} ,
                                               annotation_path = \
                                                 './custom:Problems' ,
                                               tag_name = 'Problem' ,
                                               namespaces = namespaces ,
                                               begin_attribute = 'begin' ,
                                               end_attribute = 'end' ,
                                               optional_attributes = \
                                                 patterns[ 0 ][ 'optional_attributes' ] )
    expected_output_no_opt_attributes = \
      { '181' :  [ { 'type': 'Problem' ,
                      'begin_pos': '181' ,
                      'end_pos': '188' ,
                      'raw_text': None } ] ,
        '218' : [ { 'type': 'Problem' ,
                   'begin_pos': '218' ,
                   'end_pos': '224' ,
                   'raw_text': None } ]
      }
    expected_output_with_opt_attributes = \
      { '181' :  [ { 'type': 'Problem' ,
                     'begin_pos': '181' ,
                     'end_pos': '188' ,
                     'raw_text': None ,
                     'conditional' : 'true' ,
                     'generic' : 'false' ,
                     'historical' : 'false' ,
                     'negated' : 'false' ,
                     'not_patient' : 'true' ,
                     'uncertain' : 'false' } ] ,
        '218' : [ { 'type': 'Problem' ,
                    'begin_pos': '218' ,
                    'end_pos': '224' ,
                    'raw_text': None ,
                    'conditional' : 'false' ,
                    'generic' : 'false' ,
                    'historical' : 'true' ,
                    'negated' : 'false' ,
                    'not_patient' : 'false' ,
                    'uncertain' : 'true' } ]
      }
    assert strict_starts_no_opt_attributes == \
        expected_output_no_opt_attributes
    assert strict_starts_with_opt_attributes == \
        expected_output_with_opt_attributes
    assert strict_starts_no_opt_attributes != \
        expected_output_with_opt_attributes
    assert strict_starts_with_opt_attributes != \
        expected_output_no_opt_attributes


def test_extracting_with_and_without_optional_attributes_called_by_parent():
    ingest_file = 'tests/data/013_Conditional_Problem.xmi'
    config_file = 'config/webanno_problems_allergies_xmi.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    patterns.pop()
    offset_mapping , annots_with_opt_attributes = \
      text_extraction.extract_annotations( ingest_file ,
                                           namespaces = namespaces ,
                                           document_data = document_data ,
                                           patterns = patterns ,
                                           skip_chars = None ,
                                           out_file = None )
    patterns[ 0 ][ 'optional_attributes' ] = []
    offset_mapping , annots_without_opt_attributes = \
      text_extraction.extract_annotations( ingest_file ,
                                           namespaces = namespaces ,
                                           document_data = document_data ,
                                           patterns = patterns ,
                                           skip_chars = None ,
                                           out_file = None )
    expected_output_without_opt_attributes = \
      { '181' :  [ { 'type': 'Problem' ,
                      'begin_pos': '181' ,
                      'end_pos': '188' ,
                      'raw_text': None } ] ,
        '218' : [ { 'type': 'Problem' ,
                   'begin_pos': '218' ,
                   'end_pos': '224' ,
                   'raw_text': None } ]
      }
    expected_output_with_opt_attributes = \
      { '181' :  [ { 'type': 'Problem' ,
                     'begin_pos': '181' ,
                     'end_pos': '188' ,
                     'raw_text': None ,
                     'conditional' : 'true' ,
                     'generic' : 'false' ,
                     'historical' : 'false' ,
                     'negated' : 'false' ,
                     'not_patient' : 'true' ,
                     'uncertain' : 'false' } ] ,
        '218' : [ { 'type': 'Problem' ,
                    'begin_pos': '218' ,
                    'end_pos': '224' ,
                    'raw_text': None ,
                    'conditional' : 'false' ,
                    'generic' : 'false' ,
                    'historical' : 'true' ,
                    'negated' : 'false' ,
                    'not_patient' : 'false' ,
                    'uncertain' : 'true' } ]
      }
    assert annots_with_opt_attributes == \
        expected_output_with_opt_attributes
    assert annots_without_opt_attributes == \
        expected_output_without_opt_attributes
    assert annots_with_opt_attributes != \
        expected_output_without_opt_attributes
    assert annots_without_opt_attributes != \
        expected_output_with_opt_attributes


def test_extract_annotations_overlapping_in_same_file():
    ingest_file = 'tests/data/offset_matching/the_doctors_age_overlapping.xmi'
    namespaces = { 'cas' :
                   "http:///uima/cas.ecore" ,
                   'custom' :
                    "http:///webanno/custom.ecore" }
    document_data = dict( tag_xpath = './cas:Sofa' ,
                          content_attribute = 'sofaString' )
    patterns = [ { 'type': 'Age' , 'xpath': './custom:PHI[@Time="Age"]',
                   'display_name': 'Age', 'short_name': 'Age', 'long_name': 'Age',
                   'optional_attributes': [], 'begin_attr': 'begin', 'end_attr': 'end' } ,
                 { 'type': 'DateTime' , 'xpath': './custom:PHI[@Time="DateTime"]',
                   'display_name': 'DateTime', 'short_name': 'DateTime', 'long_name': 'DateTime',
                   'optional_attributes': [], 'begin_attr': 'begin', 'end_attr': 'end' } ,
                 { 'type': 'Number' , 'xpath': './custom:PHI[@Time="Number"]',
                   'display_name': 'Number', 'short_name': 'Number', 'long_name': 'Number',
                   'optional_attributes': [], 'begin_attr': 'begin', 'end_attr': 'end' }
    ]
    offset_mapping , annots = \
      text_extraction.extract_annotations( ingest_file ,
                                           namespaces = namespaces ,
                                           document_data = document_data ,
                                           patterns = patterns ,
                                           skip_chars = None ,
                                           out_file = None )
    expected_annots = { '24' : [ { 'type': 'Age', 'end_pos': '27', 'raw_text': None, 'begin_pos': '24' } ,
                                 { 'type': 'Number', 'end_pos': '27', 'raw_text': None, 'begin_pos': '24' } ] ,
                        '41' : [ {'type': 'DateTime', 'end_pos': '59', 'raw_text': None, 'begin_pos': '41'} ,
                                 {'type': 'DateTime', 'end_pos': '54', 'raw_text': None, 'begin_pos': '41'} ] }
    assert annots == expected_annots


#############################################
## Test writing to disk
#############################################

def test_writing_dictionary_for_datetime_from_0005_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    reference_file = 'tests/data/i2b2_2016_track-1_reference_out/0005_gs.xml'
    config_file = 'config/i2b2_2016_track-1.conf'
    try:
        tmp_descriptor, tmp_file = tempfile.mkstemp()
        os.close( tmp_descriptor )
        namespaces , document_data , patterns = \
          args_and_configs.process_config( config_file = config_file ,
                                           score_key = 'Short Name' ,
                                           score_values = [ '.*' ] )
        text_extraction.extract_annotations( ingest_file ,
                                             namespaces = namespaces ,
                                             document_data = document_data ,
                                             patterns = patterns ,
                                             skip_chars = '[\s]' ,
                                             out_file = tmp_file )
        with open( reference_file , 'r' ) as rf:
            reloaded_reference = json.load( rf )
        with open( tmp_file , 'r' ) as tf:
            reloaded_test = json.load( tf )
        assert reloaded_reference[ 'annotations' ] == reloaded_test[ 'annotations' ]
        assert reloaded_reference[ 'offset_mapping' ] == reloaded_test[ 'offset_mapping' ]
        assert reloaded_reference[ 'raw_content' ] == reloaded_test[ 'raw_content' ]
    finally:
        os.remove( tmp_file )


## TODO - add tests for ingore_whitespace == True | False
def test_of_presaved_dictionary_for_complex_patterns():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    presaved_file = 'tests/data/i2b2_2016_track-1_reference_out/0005_gs.xml'
    config_file = 'config/i2b2_2016_track-1.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    with open( presaved_file , 'r' ) as fp:
        reloaded_json = json.load( fp )
    offset_mapping , strict_starts = \
      text_extraction.extract_annotations( ingest_file ,
                                           namespaces = namespaces ,
                                           document_data = document_data ,
                                           patterns = patterns ,
                                           skip_chars = '[\s]' ,
                                           out_file = None )
    assert reloaded_json[ 'annotations' ] == strict_starts


def test_of_identity_read_write_of_dictionary_for_complex_patterns():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    config_file = 'config/i2b2_2016_track-1.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    with tempfile.NamedTemporaryFile() as tmpfile_handle:
        assert os.path.exists( tmpfile_handle.name )
        offset_mapping , strict_starts = \
          text_extraction.extract_annotations( ingest_file ,
                                               namespaces = namespaces ,
                                               document_data = document_data ,
                                               patterns = patterns ,
                                               skip_chars = '[\s]' ,
                                               out_file = tmpfile_handle.name )
        reloaded_json = json.load( tmpfile_handle )
        assert reloaded_json[ 'annotations' ] == strict_starts
        assert os.path.exists( tmpfile_handle.name )
    assert os.path.exists( tmpfile_handle.name ) == False

## TODO - add real delimited ingest file for testing
# def test_of_identity_read_write_of_dictionary_for_delimited_patterns():
#     ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
#     config_file = 'config/plaintext_sentences.conf'
#     namespaces , document_data , patterns = \
#       args_and_configs.process_config( config_file = config_file ,
#                                        score_key = 'Short Name' ,
#                                        score_values = [ '.*' ] )
#     with tempfile.NamedTemporaryFile() as tmpfile_handle:
#         assert os.path.exists( tmpfile_handle.name )
#         offset_mapping , strict_starts = \
#           text_extraction.extract_annotations( ingest_file ,
#                                                namespaces = namespaces ,
#                                                document_data = document_data ,
#                                                patterns = patterns ,
#                                                skip_chars = '[\s]' ,
#                                                out_file = tmpfile_handle.name )
#         reloaded_json = json.load( tmpfile_handle )
#         assert reloaded_json[ 'annotations' ] == strict_starts
#         assert os.path.exists( tmpfile_handle.name )
#     assert os.path.exists( tmpfile_handle.name ) == False

def test_empty_contents_of_write_of_dictionary_for_brat_patterns():
    ingest_file = 'tests/data/brat_reference/ibm.ann'
    config_file = 'config/brat_problems_allergies_standoff.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    with tempfile.NamedTemporaryFile() as tmpfile_handle:
        assert os.path.exists( tmpfile_handle.name )
        offset_mapping , strict_starts = \
          text_extraction.extract_annotations( ingest_file ,
                                               namespaces = namespaces ,
                                               document_data = document_data ,
                                               patterns = patterns ,
                                               skip_chars = '[\s]' ,
                                               out_file = tmpfile_handle.name )
        assert strict_starts == {}
        assert os.path.exists( tmpfile_handle.name )
        with open( tmpfile_handle.name , 'r' ) as rf:
            reloaded_out_file = json.load( rf )
        assert reloaded_out_file[ "annotations" ] == {}
        assert reloaded_out_file[ "raw_content" ] == "International Business Machines Corporation: IBM is Big Blue\n"
    assert os.path.exists( tmpfile_handle.name ) == False

def test_contents_of_write_of_dictionary_for_brat_patterns():
    ingest_file = 'tests/data/brat_reference/problems_and_allergens.ann'
    config_file = 'config/brat_problems_allergies_standoff.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    with tempfile.NamedTemporaryFile() as tmpfile_handle:
        assert os.path.exists( tmpfile_handle.name )
        offset_mapping , strict_starts = \
          text_extraction.extract_annotations( ingest_file ,
                                               namespaces = namespaces ,
                                               document_data = document_data ,
                                               patterns = patterns ,
                                               skip_chars = '[\s]' ,
                                               out_file = tmpfile_handle.name )
        reloaded_json = json.load( tmpfile_handle )
        assert reloaded_json[ 'annotations' ] == strict_starts
        ## T34	Problem 474 493	shortness of breath
        ## A1	Negated T34
        assert strict_starts[ '474' ][ 0 ][ 'begin_pos' ] == '474'
        assert strict_starts[ '474' ][ 0 ][ 'end_pos' ] == '493'
        assert strict_starts[ '474' ][ 0 ][ 'raw_text' ] == 'shortness of breath'
        assert strict_starts[ '474' ][ 0 ][ 'Historical' ] == 'false'
        assert strict_starts[ '474' ][ 0 ][ 'Negated' ] == 'true'
        assert os.path.exists( tmpfile_handle.name )
    assert os.path.exists( tmpfile_handle.name ) == False


def test_brat_text_bound_annotation_simple():
    line = 'T1	Organization 0 43	International Business Machines Corporation'
    new_entry = text_extraction.extract_brat_text_bound_annotation( 'test.ann' ,
                                                                    line ,
                                                                    offset_mapping = {} ,
                                                                    tag_name = 'Organization' ,
                                                                    optional_attributes = [] )
    assert( new_entry[ 'match_index' ] == 'T1' )
    assert( new_entry[ 'type' ] == 'Organization' )
    assert( new_entry[ 'begin_pos' ] == '0' )
    assert( new_entry[ 'end_pos' ] == '43' )
    assert( new_entry[ 'raw_text' ] == 'International Business Machines Corporation' )

def test_brat_text_bound_annotation_attributes_default_to_false():
    line = 'T1	Organization 0 43	International Business Machines Corporation'
    new_entry = text_extraction.extract_brat_text_bound_annotation( 'test.ann' ,
                                                                    line ,
                                                                    offset_mapping = {} ,
                                                                    tag_name = 'Organization' ,
                                                                    optional_attributes = [ 'Negated' ,
                                                                                            'Historical' ] )
    assert( new_entry[ 'Negated' ] == 'false' )
    assert( new_entry[ 'Historical' ] == 'false' )

def test_brat_text_bound_annotation_offset_mapping_works():
    line = 'T1	Organization 0 43	International Business Machines Corporation'
    new_entry = text_extraction.extract_brat_text_bound_annotation( 'test.ann' ,
                                                                    line ,
                                                                    offset_mapping = { "0": "3" ,
                                                                                       "43": "42" } ,
                                                                    tag_name = 'Organization' ,
                                                                    optional_attributes = [] )
    assert( new_entry[ 'begin_pos' ] == '0' )
    assert( new_entry[ 'begin_pos_mapped' ] == '3' )
    assert( new_entry[ 'end_pos' ] == '43' )
    assert( new_entry[ 'end_pos_mapped' ] == '42' )

def test_brat_text_bound_annotation_skip_other_tags():
    line = 'T1	Organization 0 43	International Business Machines Corporation'
    new_entry = text_extraction.extract_brat_text_bound_annotation( 'test.ann' ,
                                                                    line ,
                                                                    offset_mapping = {} ,
                                                                    tag_name = 'Person' ,
                                                                    optional_attributes = [] )
    assert( new_entry == None )

def test_brat_text_bound_annotation_discontinuous():
    ## North and South America
    ## T1	Location 0 5;16 23	North America
    ## T2	Location 10 23	South America
    line = 'T1	Location 0 5;16 23	North America'
    new_entry = text_extraction.extract_brat_text_bound_annotation( 'test.ann' ,
                                                                    line ,
                                                                    offset_mapping = {} ,
                                                                    tag_name = 'Location' ,
                                                                    optional_attributes = [] )
    assert( new_entry == None )

def test_brat_relation_binary():
    ## T3	Organization 33 41	Ericsson
    ## T4	Country 75 81	Sweden
    ## R1	Origin Arg1:T3 Arg2:T4
    line = 'R1	Origin Arg1:T3 Arg2:T4'
    new_entry = text_extraction.extract_brat_relation( 'test.ann' ,
                                                       line ,
                                                       tag_name = '' ,
                                                       optional_attributes = [] )
    assert( new_entry == None )
    
def test_brat_relation_equivalence():
    ## T1	Organization 0 43	International Business Machines Corporation
    ## T2	Organization 45 48	IBM
    ## T3	Organization 52 60	Big Blue
    ## *	Equiv T1 T2 T3
    line = '*	Equiv T1 T2 T3'
    new_entry = text_extraction.extract_brat_equivalence( 'test.ann' ,
                                                          line ,
                                                          optional_attributes = [] )
    assert( new_entry == None )


def test_brat_event():
    ## T1	Organization 0 4	Sony
    ## T2	MERGE-ORG 14 27	joint venture
    ## T3	Organization 33 41	Ericsson
    ## E1	MERGE-ORG:T2 Org1:T1 Org2:T3
    line = 'E1	MERGE-ORG:T2 Org1:T1 Org2:T3'
    new_entry = text_extraction.extract_brat_event( 'test.ann' ,
                                                    line ,
                                                    tag_name = '' ,
                                                    optional_attributes = [] )
    assert( new_entry == None )

 
def test_brat_skip_non_optional_attributes():
    ## T1	Organization 0 4	Sony
    ## T2	MERGE-ORG 14 27	joint venture
    ## T3	Organization 33 41	Ericsson
    ## E1	MERGE-ORG:T2 Org1:T1 Org2:T3
    ## A1	Negation E1
    line = 'A1	Negation E1'
    new_attribute_value = text_extraction.extract_brat_attribute( 'test.ann' ,
                                                                  line ,
                                                                  optional_attributes = [ 'Negated' ,
                                                                                          'Historical' ] )
    assert( new_attribute_value == [ 'E1' , 'Negation' , None , 'true' ] )

def test_brat_attribute_binary():
    ## T1	Organization 0 4	Sony
    ## T2	MERGE-ORG 14 27	joint venture
    ## T3	Organization 33 41	Ericsson
    ## E1	MERGE-ORG:T2 Org1:T1 Org2:T3
    ## A1	Negation E1
    line = 'A1	Negation E1'
    new_attribute_value = text_extraction.extract_brat_attribute( 'test.ann' ,
                                                                  line ,
                                                                  optional_attributes = [ 'Negation' ] )
    assert( new_attribute_value == [ 'E1' , 'Negation' , 'Negation' , 'true' ] )

def test_brat_attribute_binary_m_prefix():
    ## T1	Organization 0 4	Sony
    ## T2	MERGE-ORG 14 27	joint venture
    ## T3	Organization 33 41	Ericsson
    ## E1	MERGE-ORG:T2 Org1:T1 Org2:T3
    ## M1	Negation E1
    line = 'M1	Negation E1'
    new_attribute_value = text_extraction.extract_brat_attribute( 'test.ann' ,
                                                                  line ,
                                                                  optional_attributes = [ 'Negation' ] )
    assert( new_attribute_value == [ 'E1' , 'Negation' , 'Negation' , 'true' ] )


def test_brat_attribute_multivalue_string():
    ## T1	Organization 0 4	Sony
    ## T2	MERGE-ORG 14 27	joint venture
    ## T3	Organization 33 41	Ericsson
    ## E1	MERGE-ORG:T2 Org1:T1 Org2:T3
    ## A2	Confidence E2 L1
    line = 'A2	Confidence E2 L1'
    new_attribute_value = text_extraction.extract_brat_attribute( 'test.ann' ,
                                                                  line ,
                                                                  optional_attributes = [ 'Confidence' ] )
    assert( new_attribute_value == None )


def test_brat_normalization_ignore_unselected_reference():
    ## N1	Reference T1 Wikipedia:534366	Barack Obama
    line = 'N1	Reference T1 Wikipedia:534366	Barack Obama'
    new_entry = text_extraction.extract_brat_normalization( 'test.ann' ,
                                                            line ,
                                                            normalization_engines = [ 'Britanica' ] )
    assert( new_entry == None )


def test_brat_normalization_simple_lookup():
    ## N1	Reference T1 Wikipedia:534366	Barack Obama
    line = 'N1	Reference T1 Wikipedia:534366	Barack Obama'
    new_entry = text_extraction.extract_brat_normalization( 'test.ann' ,
                                                            line ,
                                                            normalization_engines = [ 'Wikipedia' ] )
    assert( new_entry == [ 'T1' , 'Wikipedia' , '534366' , 'Barack Obama' ] )


#############################################
## Test extracting document contents
#############################################

def test_empty_extraction_of_doc_content_from_0016_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0016_gs.xml'
    ## Look for a path that doesn't exist so that we get an empty return
    test_dd = dict( cdata_xpath = '/dev/null' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = test_dd ,
                                     skip_chars = '[\s]' )
    expected_output = {}
    assert offset_mapping == expected_output

def test_extracting_doc_content_from_0016_gs():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0016_gs.xml'
    test_dd = dict( cdata_xpath = './TEXT' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = test_dd ,
                                     skip_chars = '[\s]' )
    expected_output = { '0': None ,
                        '1': None ,
                        '2': None ,
                        '3': '0', '4': '1', '5': '2', '6': None }
    for index in [ "0" , "1" , "2" , "3" , "4" , "5" , "6" ]:
        assert offset_mapping[ index ] == expected_output[ index ]

def test_extracting_doc_content_from_0016_gs_skip_z_char():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0016_gs.xml'
    test_dd = dict( cdata_xpath = './TEXT' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = test_dd ,
                                     skip_chars = '[\sz]' )
    expected_output = { '0': None ,
                        '1': None ,
                        '2': None ,
                        '3': None , '4': None , '5': '0', '6': None }
    for index in [ "0" , "1" , "2" , "3" , "4" , "5" , "6" ]:
        assert offset_mapping[ index ] == expected_output[ index ]

def test_extracting_doc_content_from_0016_gs_skip_zpipe_char():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0016_gs.xml'
    test_dd = dict( cdata_xpath = './TEXT' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = test_dd ,
                                     skip_chars = '[z|]' )
    expected_output = { '0': '0' ,
                        '1': '1' ,
                        '2': '2' ,
                        '3': None, '4': None, '5': None, '6': '3' }
    for index in [ "0" , "1" , "2" , "3" , "4" , "5" , "6" ]:
        assert offset_mapping[ index ] == expected_output[ index ]

def test_extracting_doc_content_from_995723_sentences_xmi():
    ingest_file = 'tests/data/sentences/995723.sentences.xmi'
    test_dd = dict( tag_xpath = './cas:Sofa' ,
                    content_attribute = 'sofaString' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = { 'cas' :
                                                    "http:///uima/cas.ecore" } ,
                                     document_data = test_dd ,
                                     skip_chars = '[\s]' )
    expected_output = { '0': '0' , '1': '1' , '2': '2' , '3': '3' , '4': '4' ,
                        '5': '5' , '6': '6' , '7': '7' }
    assert offset_mapping == expected_output


def test_offset_mapping_matches_pos_mapped_automatically():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data ,
                                     skip_chars = '[\s]' )
    strict_starts = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                                  offset_mapping = offset_mapping ,
                                                  annotation_path = \
                                                      './TAGS/DATE' ,
                                                  tag_name = 'DateTime' ,
                                                  begin_attribute = 'start' ,
                                                  end_attribute = 'end' )
    for start_key in strict_starts:
        begin_pos = strict_starts[ start_key ][ 0 ][ 'begin_pos' ]
        begin_pos_mapped = strict_starts[ start_key ][ 0 ][ 'begin_pos_mapped' ]
        end_pos = strict_starts[ start_key ][ 0 ][ 'end_pos' ]
        end_pos_mapped = strict_starts[ start_key ][ 0 ][ 'end_pos_mapped' ]
        ## dictionary key is set to begin_pos
        assert start_key == begin_pos
        ## mapping works for begin position
        assert begin_pos != begin_pos_mapped
        while( offset_mapping[ begin_pos ] == None ):
            begin_pos = str( int( begin_pos ) + 1 )
        assert begin_pos_mapped == offset_mapping[ begin_pos ]
        ## mapping works for end position
        assert end_pos != end_pos_mapped
        while( offset_mapping[ end_pos ] == None ):
            end_pos = str( int( end_pos ) - 1 )
        assert end_pos_mapped == offset_mapping[ end_pos ]


def test_offset_mapping_matches_pos_mapped_manually():
    ingest_file = 'tests/data/i2b2_2016_track-1_reference/0005_gs.xml'
    document_data = dict( cdata_xpath = './TEXT' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data ,
                                     skip_chars = '[\s]' )
    strict_starts = \
      text_extraction.extract_annotations_xml( ingest_file ,
                                               offset_mapping = offset_mapping ,
                                               annotation_path = \
                                                 './TAGS/DATE' ,
                                               tag_name = 'DateTime' ,
                                               begin_attribute = 'start' ,
                                               end_attribute = 'end' )
    ##
    assert strict_starts[ '87' ][ 0 ][ 'begin_pos' ] == '87'
    assert strict_starts[ '87' ][ 0 ][ 'begin_pos_mapped' ] == \
        offset_mapping[ '87' ]
    assert strict_starts[ '87' ][ 0 ][ 'end_pos' ] == '97'
    assert strict_starts[ '87' ][ 0 ][ 'end_pos_mapped' ] == \
        offset_mapping[ '97' ]
    ##
    assert strict_starts[ '2404' ][ 0 ][ 'begin_pos' ] == '2404'
    assert strict_starts[ '2404' ][ 0 ][ 'begin_pos_mapped' ] == \
        offset_mapping[ '2404' ]
    assert strict_starts[ '2404' ][ 0 ][ 'end_pos' ] == '2410'
    assert strict_starts[ '2404' ][ 0 ][ 'end_pos_mapped' ] == \
        offset_mapping[ '2409' ]


def test_brat_standoff_extraction():
    ingest_file = 'tests/data/brat_reference/ibm.ann'
    document_data = dict( format = '.ann .txt' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data ,
                                     skip_chars = '[\s]' )
    strict_starts = \
      text_extraction.extract_annotations_brat_standoff( ingest_file ,
                                                         offset_mapping = offset_mapping ,
                                                         type_prefix = 'T' ,
                                                         tag_name = 'Organization' )
    ##
    assert strict_starts[ '0' ][ 0 ][ 'begin_pos' ] == '0'
    assert strict_starts[ '0' ][ 0 ][ 'end_pos' ] == '43'
    assert strict_starts[ '0' ][ 0 ][ 'raw_text' ] == 'International Business Machines Corporation'
    ##
    assert strict_starts[ '45' ][ 0 ][ 'begin_pos' ] == '45'
    assert strict_starts[ '45' ][ 0 ][ 'end_pos' ] == '48'
    ##
    assert strict_starts[ '52' ][ 0 ][ 'raw_text' ] == 'Big Blue'



def test_brat_standoff_extraction_with_attributes():
    ingest_file = 'tests/data/brat_reference/problems_and_allergens.ann'
    document_data = dict( format = '.ann .txt' )
    raw_content , offset_mapping = \
      text_extraction.extract_chars( ingest_file ,
                                     namespaces = {} ,
                                     document_data = document_data ,
                                     skip_chars = '[\s]' )
    strict_starts = \
      text_extraction.extract_annotations_brat_standoff( ingest_file ,
                                                         offset_mapping = offset_mapping ,
                                                         type_prefix = 'T' ,
                                                         tag_name = 'Problem' ,
                                                         optional_attributes = [ 'Conditional' ,
                                                                                 'Generic' ,
                                                                                 'Historical' ,
                                                                                 'Negated' ,
                                                                                 'NotPatient' ,
                                                                                 'Uncertain' ] )
    ##
    assert strict_starts[ '474' ][ 0 ][ 'begin_pos' ] == '474'
    assert strict_starts[ '474' ][ 0 ][ 'end_pos' ] == '493'
    assert strict_starts[ '474' ][ 0 ][ 'raw_text' ] == 'shortness of breath'


