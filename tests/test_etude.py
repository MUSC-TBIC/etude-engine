
import etude

#############################################
## Test file/corpus io
#############################################


def test_full_matching_directory():
    match_count , file_mapping = \
      etude.collect_files( gold_folder = 'tests/data/i2b2_2016_track-1_gold' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' ] )
    assert match_count == 10
    assert len( file_mapping.keys() ) == match_count


def test_identical_file_suffix_matching_directory():
    match_count , file_mapping = \
      etude.collect_files( gold_folder = 'tests/data/i2b2_2016_track-1_gold' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' , '.xml' ] )
    assert match_count == 10
    assert len( file_mapping.keys() ) == match_count


def test_empty_gold_directory():
    match_count , file_mapping = \
      etude.collect_files( gold_folder = 'tests/data/i2b2_2016_track-1_gold' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ 'I_Do_Not_Exist' ] )
    assert match_count == 0
    ## Empty dictionaries evaluate to False so testing bool can tell us if any gold
    ## documents exist
    assert not bool( file_mapping )


def test_empty_test_directory():
    match_count , file_mapping = \
      etude.collect_files( gold_folder = 'tests/data/i2b2_2016_track-1_gold' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' , '.I_Do_Not_Exist' ] )
    assert match_count == 0
    ## Empty dictionaries evaluate to False so testing bool can tell us if any gold
    ## documents exist
    assert bool( file_mapping )
