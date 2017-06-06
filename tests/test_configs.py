
import json

import etude

#############################################
## Test loading and reading of config files
#############################################

def test_set_score_key_Sentences():
    filename = 'config/uima_sentences.conf'
    patterns = etude.process_config( config_file = filename ,
                                     score_key = 'Short Name' )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Sentence"

def test_set_score_key_DateTime_Tutorial():
    filename = 'config/CAS_XMI.conf'
    patterns = etude.process_config( config_file = filename ,
                                     score_key = 'Short Name' )
    for pattern in patterns:
        assert pattern[ 'type' ] == "DateTime"
    patterns = etude.process_config( config_file = filename ,
                                     score_key = 'Parent' )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Time"
    patterns = etude.process_config( config_file = filename ,
                                     score_key = 'Long Name' )
    for pattern in patterns:
        assert pattern[ 'type' ] == "Date and Time Information"


def test_skip_missing_XPath():
    filename = 'config/i2b2_2016_track-1.conf'
    patterns = etude.process_config( config_file = filename ,
                                     score_key = 'Short Name' )
    for pattern in patterns:
        assert pattern[ 'long_name' ] != "Other Person Name"


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
        patterns = etude.process_config( config_file = filename ,
                                         score_key = 'Short Name' )
        with open( 'tests/data/' + fileroot + '.json' , 'w' ) as fp:
            json.dump( patterns , fp ,
                       indent = 4 )

