
import sys

import etude

#############################################
## Early initialization and set-up
#############################################

def test_default_init_args():
    from mock import patch
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.reference_input == '/tmp/reference'
        assert args.test_input == '/tmp/test'
        assert args.corpus_out == None
        assert args.verbose == False

def test_init_args_verbose():
    from mock import patch
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--verbose' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        with open( '/tmp/bob.txt' , 'w' ) as fp:
            fp.write( '{}'.format( args ) )
        assert args.verbose == True

def test_init_args_corpus_out():
    from mock import patch
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--corpus-out' , '/tmp/corpusOut' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        with open( '/tmp/bob.txt' , 'a' ) as fp:
            fp.write( '{}'.format( args ) )
        assert args.corpus_out == '/tmp/corpusOut'


#############################################
## Test file/corpus io
#############################################


def test_full_matching_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' ] )
    assert match_count == 10
    assert len( file_mapping.keys() ) == match_count


def test_identical_file_suffix_matching_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' , '.xml' ] )
    assert match_count == 10
    assert len( file_mapping.keys() ) == match_count


def test_empty_reference_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ 'I_Do_Not_Exist' ] )
    assert match_count == 0
    ## Empty dictionaries evaluate to False so testing bool can tell us if any reference
    ## documents exist
    assert not bool( file_mapping )


def test_empty_test_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' , '.I_Do_Not_Exist' ] )
    assert match_count == 0
    ## Empty dictionaries evaluate to False so testing bool can tell us if any reference
    ## documents exist
    assert bool( file_mapping )
