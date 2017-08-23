
import json

import args_and_configs

#############################################
## Test passing command line arguments
#############################################

def test_default_ignore_whitespace_flag():
    command_line_args = [ '--gold-input' , 'tests/data/i2b2_2016_track-1_gold' ,
                          '--test-input' , 'tests/data/i2b2_2016_track-1_test' ]
    args = args_and_configs.get_arguments( command_line_args )
    assert args.ignore_whitespace == True

def test_ignore_whitespace_flag_usage():
    command_line_args = [ '--gold-input' , 'tests/data/i2b2_2016_track-1_gold' ,
                          '--test-input' , 'tests/data/i2b2_2016_track-1_test' ,
                          '--heed-whitespace' ]
    args = args_and_configs.get_arguments( command_line_args )
    assert args.ignore_whitespace == False

def test_heed_whitespace_flag_usage():
    command_line_args = [ '--gold-input' , 'tests/data/i2b2_2016_track-1_gold' ,
                          '--test-input' , 'tests/data/i2b2_2016_track-1_test' ,
                          '--ignore-whitespace' ]
    args = args_and_configs.get_arguments( command_line_args )
    assert args.ignore_whitespace == True


#############################################
## Test loading and reading of config files
#############################################

## Namespaces

def test_i2b2_2016_track_1_has_empty_namespace():
    config_file = 'config/i2b2_2016_track-1.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    ## Empty dictionary resolves as False
    assert not bool( namespaces )
    

def test_sentences_has_defined_namespaces():
    config_file = 'config/uima_sentences.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    ## Non-empty dictionary resolves as True
    expected_namespaces = \
      { 'cas' : 'http:///uima/cas.ecore' ,
        'type': 'http:///com/clinacuity/deid/nlp/uima/type.ecore',
        'type4': 'http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore' 
      }
    assert namespaces == expected_namespaces
    

def test_webanno_custom_namespaces():
    config_file = 'config/webanno_uima_xmi.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = config_file ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    ## Non-empty dictionary resolves as True
    expected_namespaces = { 'custom': 'http:///webanno/custom.ecore' }
    with open( '/tmp/stdout.log' , 'w' ) as fp:
        fp.write( '-----------\n{}\n-------------\n'.format( namespaces ) )
    assert namespaces == expected_namespaces
    

## Patterns

def test_set_score_key_Sentences():
    filename = 'config/uima_sentences.conf'
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = [ '.*' ] )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Sentence"

def test_set_score_key_DateTime_Tutorial():
    filename = 'config/CAS_XMI.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "DateTime"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Parent' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Time"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Long Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Date and Time Information"


def test_skip_missing_XPath():
    filename = 'config/i2b2_2016_track-1.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'long_name' ] != "Other Person Name"

def test_set_score_key_match_Time_Tutorial():
    filename = 'config/CAS_XMI.conf'
    score_values = [ 'Time' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "DateTime"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Parent' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Time"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Long Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Date and Time Information"

def test_set_score_key_match_strict_start_and_end_char_Tutorial():
    filename = 'config/CAS_XMI.conf'
    score_values = [ '^[DT].*[en]$' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "DateTime"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Parent' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Time"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Long Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Date and Time Information"

def test_set_score_key_match_over_multiple_values_Tutorial():
    filename = 'config/CAS_XMI.conf'
    score_values = [ '^D.*e$' , '^D.*n$' , '^T.*e$' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "DateTime"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Parent' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Time"
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Long Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Date and Time Information"


def test_skip_missing_XPath():
    filename = 'config/i2b2_2016_track-1.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    for pattern in patterns:
        assert pattern[ 'long_name' ] != "Other Person Name"

## Document Data


def test_default_document_format():
    filename = 'config/i2b2_2016_track-1.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    assert document_data[ 'format' ] == 'Unknown'


def test_plaintext_document_format():
    filename = 'config/plaintext_sentences.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    assert document_data[ 'format' ] == 'txt'


## Raw Content

def test_raw_content_extraction_from_cdata():
    filename = 'config/i2b2_2016_track-1.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    assert document_data[ 'cdata_xpath' ] == './TEXT'
    assert 'tag_xpath' not in document_data
    assert 'content_attribute' not in document_data


def test_raw_content_extraction_from_attribute():
    filename = 'config/webanno_phi_xmi.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    assert 'cdata_xpath' not in document_data
    assert document_data[ 'tag_xpath' ] == './cas:Sofa'
    assert document_data[ 'content_attribute' ] == 'sofaString'


def test_raw_content_extraction_from_plaintext():
    filename = 'config/plaintext_sentences.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    assert 'cdata_xpath' not in document_data
    assert 'tag_xpath' not in document_data
    assert 'content_attribute' not in document_data


## Required and Optional Attribute Extraction

def test_optional_attributes():
    filename = 'config/webanno_problems_allergies_xmi.conf'
    score_values = [ '.*' ]
    namespaces , document_data , patterns = \
      args_and_configs.process_config( config_file = filename ,
                                       score_key = 'Short Name' ,
                                       score_values = score_values )
    assert 'Conditional' in patterns[ 0 ][ 'optional_attributes' ] 
    assert 'Generic' in patterns[ 0 ][ 'optional_attributes' ] 
    assert 'Historical' in patterns[ 0 ][ 'optional_attributes' ] 
    assert 'Negated' in patterns[ 0 ][ 'optional_attributes' ] 
    assert 'NotPatient' in patterns[ 0 ][ 'optional_attributes' ] 
    assert 'Uncertain' in patterns[ 0 ][ 'optional_attributes' ] 


#############################################
## Helper functions to help in setting up tests
#############################################

def convert_configs_to_json():
    fileroots = [ 'CAS_XMI' ,
                  'i2b2_2016_track-1' ,
                  'uima_sentences' ,
                  'webanno_uima_xmi' ]
    for fileroot in fileroots:
        filename = 'config/' + fileroot + '.conf'
        namespaces , document_data , patterns = \
          args_and_configs.process_config( config_file = filename ,
                                           score_key = 'Short Name' ,
                                           score_values = [ '.*' ] )
        with open( 'tests/data/' + fileroot + '.json' , 'w' ) as fp:
            json.dump( patterns , fp ,
                       indent = 4 )

