
import os
import sys

from mock import patch

import tempfile

import json

import etude
import args_and_configs

#############################################
## Early initialization and set-up
#############################################

def test_default_init_args():
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
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--verbose' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.verbose == True

def test_init_args_corpus_out():
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--corpus-out' , '/tmp/corpusOut' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.corpus_out == '/tmp/corpusOut'

def test_init_args_heed_whitespace():
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--heed-whitespace' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.ignore_whitespace == False
        assert args.skip_chars == None

def test_init_args_ignore_whitespace():
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--ignore-whitespace' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.ignore_whitespace == True
        assert args.skip_chars == '[\s]'

def test_init_args_skip_chars():
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--skip-chars' , '[z\|]' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.ignore_whitespace == True
        assert args.skip_chars == '[z\|]'

def test_init_args_skip_chars_and_whitespace_flag():
    test_args = [ 'etude.py' ,
                  '--reference-input' , '/tmp/reference' ,
                  '--test-input' , '/tmp/test' ,
                  '--ignore-whitespace' ,
                  '--skip-chars' , '[z\|]' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.ignore_whitespace == True
        assert args.skip_chars == '[z\|]'

def test_init_args_progressbar_default():
    test_args = [ 'etude.py' , '--no-metrics' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.progressbar_output == 'stderr'
        assert not args.progressbar_disabled
        assert args.progressbar_file == sys.stderr

def test_init_args_progressbar_stderr():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--progressbar-output' , 'stderr' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.progressbar_output == 'stderr'
        assert not args.progressbar_disabled
        assert args.progressbar_file == sys.stderr

def test_init_args_progressbar_stdout():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--progressbar-output' , 'stdout' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.progressbar_output == 'stdout'
        assert not args.progressbar_disabled
        assert args.progressbar_file == sys.stdout

def test_init_args_progressbar_none():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--progressbar-output' , 'none' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.progressbar_output == 'none'
        assert args.progressbar_disabled
        assert args.progressbar_file is None

def test_init_args_file_prefix_simplex():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--file-prefix' , '.xyz' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.file_prefix == '.xyz'

def test_init_args_file_prefix_simplex_dash():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--file-prefix' , ' -03.xyz' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert args.file_prefix == '-03.xyz'

def test_init_args_file_suffix_simplex():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--file-suffix' , '.xyz' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert len( args.file_suffix ) == 1
        assert args.file_suffix[ 0 ] == '.xyz'

def test_init_args_file_suffix_simplex_dash():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--file-suffix' , ' -03.xyz' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert len( args.file_suffix ) == 1
        assert args.file_suffix[ 0 ] == '-03.xyz'

def test_init_args_file_suffix_duplex():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--file-suffix' , '.xyz' , '.abc' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert len( args.file_suffix ) == 2
        assert args.file_suffix[ 0 ] == '.xyz'
        assert args.file_suffix[ 1 ] == '.abc'

def test_init_args_file_suffix_duplex_dash():
    test_args = [ 'etude.py' , '--no-metrics' ,
                  '--file-suffix' , ' -03.xyz' , ' -03.abc' ]
    with patch.object( sys , 'argv' , test_args ):
        args = etude.init_args()
        assert len( args.file_suffix ) == 2
        assert args.file_suffix[ 0 ] == '-03.xyz'
        assert args.file_suffix[ 1 ] == '-03.abc'


#############################################
## Test file/corpus io
#############################################


def test_full_matching_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' ] ,
                           skip_missing_files_flag = True )
    assert match_count == 10
    assert len( file_mapping.keys() ) == match_count

def test_full_matching_directory_file_mapping():
    file_mapping = \
      etude.get_file_mapping( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                              test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                              file_prefix = '/' ,
                              file_suffix = [ '.xml' ] ,
                              skip_missing_files_flag = True )
    assert len( file_mapping.keys() ) == 10


def test_identical_file_suffix_matching_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' , '.xml' ] ,
                           skip_missing_files_flag = True )
    assert match_count == 10
    assert len( file_mapping.keys() ) == match_count


def test_empty_reference_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ 'I_Do_Not_Exist' ] ,
                           skip_missing_files_flag = True )
    assert match_count == 0
    ## Empty dictionaries evaluate to False so testing bool can tell us if any reference
    ## documents exist
    assert not bool( file_mapping )

def test_empty_reference_directory_file_mapping():
    file_mapping = \
      etude.get_file_mapping( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                              test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                              file_prefix = '/' ,
                              file_suffix = [ 'I_Do_Not_Exist' ] ,
                              skip_missing_files_flag = True )
    assert file_mapping is None


def test_score_empty_test_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' , '.I_Do_Not_Exist' ] ,
                           skip_missing_files_flag = False )
    assert match_count == 0
    ## A dictionary containing only empty values evaluates to False
    ## so testing bool can tell us if any reference documents exist
    assert bool( file_mapping )

def test_score_empty_test_directory_file_mapping():
    file_mapping = \
      etude.get_file_mapping( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                              test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                              file_prefix = '/' ,
                              file_suffix = [ '.xml' , '.I_Do_Not_Exist' ] ,
                              skip_missing_files_flag = False )
    assert file_mapping is None

def test_skip_empty_test_directory():
    match_count , file_mapping = \
      etude.collect_files( reference_folder = 'tests/data/i2b2_2016_track-1_reference' ,
                           test_folder = 'tests/data/i2b2_2016_track-1_test' ,
                           file_prefix = '/' ,
                           file_suffix = [ '.xml' , '.I_Do_Not_Exist' ] ,
                           skip_missing_files_flag = True )
    assert match_count == 0
    assert file_mapping == {}

def test_out_filepath_with_none():
    assert etude.generate_out_file( None , 'foo.txt' ) == None

def test_out_filepath_with_output_dir():
    assert etude.generate_out_file( '/tmp/bar' , 'foo.txt' ) == '/tmp/bar/foo.txt'

def test_create_output_folders_noop():
    etude.create_output_folders( None , None )
    assert True

def test_create_output_folders_ref_dir():
    try:
        tmp_dir = tempfile.mkdtemp()
        os.rmdir( tmp_dir )
        assert not os.path.exists( tmp_dir )
        etude.create_output_folders( tmp_dir , None )
        assert os.path.exists( tmp_dir )
    finally:
        os.rmdir( tmp_dir )

def test_create_output_folders_test_dir():
    try:
        tmp_dir = tempfile.mkdtemp()
        os.rmdir( tmp_dir )
        assert not os.path.exists( tmp_dir )
        etude.create_output_folders( None , tmp_dir )
        assert os.path.exists( tmp_dir )
    finally:
        os.rmdir( tmp_dir )

def test_create_output_folders_ref_and_test_dir():
    try:
        tmp_ref_dir = tempfile.mkdtemp()
        tmp_test_dir = tempfile.mkdtemp()
        os.rmdir( tmp_ref_dir )
        os.rmdir( tmp_test_dir )
        assert not os.path.exists( tmp_ref_dir )
        assert not os.path.exists( tmp_test_dir )
        etude.create_output_folders( tmp_ref_dir , tmp_test_dir )
        assert os.path.exists( tmp_ref_dir )
        assert os.path.exists( tmp_test_dir )
    finally:
        os.rmdir( tmp_ref_dir )
        os.rmdir( tmp_test_dir )

#############################################
## Test generating annotation counts
#############################################


def test_count_ref_set_default( capsys ):
    presaved_file = 'tests/data/i2b2_2016_track-1_reference_out/0005_gs.xml'
    command_line_args = [ 'etude.py' ,
                          '--reference-input' , 'tests/data/i2b2_2016_track-1_reference' ,
                          '--reference-config' , 'config/i2b2_2016_track-1.conf' ,
                          '--print-counts' , '--no-metrics' ]
    with patch.object( sys , 'argv' , command_line_args ):
        args = etude.init_args()
        namespaces , document_data , patterns = \
          args_and_configs.process_config( config_file = args.reference_config ,
                                           score_key = args.score_key ,
                                           score_values = args.score_values )
        with open( presaved_file , 'r' ) as fp:
            reloaded_json = json.load( fp )
        etude.count_ref_set( this_ns = namespaces ,
                             this_dd = document_data ,
                             this_patterns = patterns ,
                             this_folder = args.reference_input ,
                             args = args ,
                             file_prefix = args.file_prefix ,
                             file_suffix = args.file_suffix[ 0 ] )
        default_out, err = capsys.readouterr()
        expected_values = [ [ 'counts' , 'n' ] ,
                            [ 'Total' , '445' ] ]
        for expected_values in expected_values:
            print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
        expected_out, err = capsys.readouterr()
        default_out = default_out.strip()
        expected_out = expected_out.strip()
        assert default_out == expected_out

def test_count_ref_set_by_type( capsys ):
    presaved_file = 'tests/data/i2b2_2016_track-1_reference_out/0005_gs.xml'
    command_line_args = [ 'etude.py' ,
                          '--reference-input' , 'tests/data/i2b2_2016_track-1_reference' ,
                          '--reference-config' , 'config/i2b2_2016_track-1.conf' ,
                          '--by-type' ,
                          '--print-counts' , '--no-metrics' ]
    with patch.object( sys , 'argv' , command_line_args ):
        args = etude.init_args()
        namespaces , document_data , patterns = \
          args_and_configs.process_config( config_file = args.reference_config ,
                                           score_key = args.score_key ,
                                           score_values = args.score_values )
        with open( presaved_file , 'r' ) as fp:
            reloaded_json = json.load( fp )
        etude.count_ref_set( this_ns = namespaces ,
                             this_dd = document_data ,
                             this_patterns = patterns ,
                             this_folder = args.reference_input ,
                             args = args ,
                             file_prefix = args.file_prefix ,
                             file_suffix = args.file_suffix[ 0 ] )
        default_out, err = capsys.readouterr()
        expected_values = [ [ 'counts' , 'n' ] ,
                            [ 'Total' , '445' ] ,
                            [ 'Age' , '92' ] ,
                            [ 'DateTime' , '124' ] ,
                            [ 'HCUnit' , '76' ] ,
                            [ 'OtherID' , '7' ] ,
                            [ 'OtherLoc' , '5' ] ,
                            [ 'OtherOrg' , '21' ] ,
                            [ 'Patient' , '19' ] ,
                            [ 'PhoneFax' , '6' ] ,
                            [ 'Provider' , '64' ] ,
                            [ 'StateCountry' , '21' ] ,
                            [ 'StreetCity' , '4' ] ,
                            [ 'Zip' , '4' ] ,
                            [ 'eAddress' , '2' ] ]
        for expected_values in expected_values:
            print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
        expected_out, err = capsys.readouterr()
        default_out = default_out.strip()
        expected_out = expected_out.strip()
        assert default_out == expected_out

def test_count_ref_set_by_file( capsys ):
    presaved_file = 'tests/data/i2b2_2016_track-1_reference_out/0005_gs.xml'
    command_line_args = [ 'etude.py' ,
                          '--reference-input' , 'tests/data/i2b2_2016_track-1_reference' ,
                          '--reference-config' , 'config/i2b2_2016_track-1.conf' ,
                          '--by-file' ,
                          '--print-counts' , '--no-metrics' ]
    with patch.object( sys , 'argv' , command_line_args ):
        args = etude.init_args()
        namespaces , document_data , patterns = \
          args_and_configs.process_config( config_file = args.reference_config ,
                                           score_key = args.score_key ,
                                           score_values = args.score_values )
        with open( presaved_file , 'r' ) as fp:
            reloaded_json = json.load( fp )
        etude.count_ref_set( this_ns = namespaces ,
                             this_dd = document_data ,
                             this_patterns = patterns ,
                             this_folder = args.reference_input ,
                             args = args ,
                             file_prefix = args.file_prefix ,
                             file_suffix = args.file_suffix[ 0 ] )
        default_out, err = capsys.readouterr()
        expected_values = [ [ 'counts' , 'n' ] ,
                            [ 'Total' , '445' ] ,
                            [ '0005_gs.xml' , '31' ] ,
                            [ '0016_gs.xml' , '51' ] ,
                            [ '0267_gs.xml' , '59' ] ,
                            [ '0273_gs.xml' , '35' ] ,
                            [ '0389_gs.xml' , '34' ] ,
                            [ '0475_gs.xml' , '45' ] ,
                            [ '0617_gs.xml' , '32' ] ,
                            [ '0709_gs.xml' , '41' ] ,
                            [ '0982_gs.xml' , '95' ] ,
                            [ '0992_gs.xml' , '22' ] ]
        for expected_values in expected_values:
            print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
        expected_out, err = capsys.readouterr()
        default_out = default_out.strip()
        expected_out = expected_out.strip()
        assert default_out == expected_out

def test_count_ref_set_by_type_and_file( capsys ):
    presaved_file = 'tests/data/i2b2_2016_track-1_reference_out/0005_gs.xml'
    command_line_args = [ 'etude.py' ,
                          '--reference-input' , 'tests/data/i2b2_2016_track-1_reference' ,
                          '--reference-config' , 'config/i2b2_2016_track-1.conf' ,
                          '--by-type' , '--by-file' ,
                          '--print-counts' , '--no-metrics' ]
    with patch.object( sys , 'argv' , command_line_args ):
        args = etude.init_args()
        namespaces , document_data , patterns = \
          args_and_configs.process_config( config_file = args.reference_config ,
                                           score_key = args.score_key ,
                                           score_values = args.score_values )
        with open( presaved_file , 'r' ) as fp:
            reloaded_json = json.load( fp )
        etude.count_ref_set( this_ns = namespaces ,
                             this_dd = document_data ,
                             this_patterns = patterns ,
                             this_folder = args.reference_input ,
                             args = args ,
                             file_prefix = args.file_prefix ,
                             file_suffix = args.file_suffix[ 0 ] )
        default_out, err = capsys.readouterr()
        expected_values = [ [ 'counts' , 'n' ] ,
                            [ 'Total' , '445' ] ,
                            [ '0005_gs.xml' , '31' ] ,
                            [ '0016_gs.xml' , '51' ] ,
                            [ '0267_gs.xml' , '59' ] ,
                            [ '0273_gs.xml' , '35' ] ,
                            [ '0389_gs.xml' , '34' ] ,
                            [ '0475_gs.xml' , '45' ] ,
                            [ '0617_gs.xml' , '32' ] ,
                            [ '0709_gs.xml' , '41' ] ,
                            [ '0982_gs.xml' , '95' ] ,
                            [ '0992_gs.xml' , '22' ] ,
                            [ 'Age' , '92' ] ,
                            [ 'DateTime' , '124' ] ,
                            [ 'HCUnit' , '76' ] ,
                            [ 'OtherID' , '7' ] ,
                            [ 'OtherLoc' , '5' ] ,
                            [ 'OtherOrg' , '21' ] ,
                            [ 'Patient' , '19' ] ,
                            [ 'PhoneFax' , '6' ] ,
                            [ 'Provider' , '64' ] ,
                            [ 'StateCountry' , '21' ] ,
                            [ 'StreetCity' , '4' ] ,
                            [ 'Zip' , '4' ] ,
                            [ 'eAddress' , '2' ] ]
        for expected_values in expected_values:
            print( args.delim.join( '{}'.format( m ) for m in expected_values ) )
        expected_out, err = capsys.readouterr()
        default_out = default_out.strip()
        expected_out = expected_out.strip()
        assert default_out == expected_out

def test_count_ref_set_csv_out():
    presaved_file = 'tests/data/i2b2_2016_track-1_csv_out.csv'
    try:
        tmp_descriptor, tmp_file = tempfile.mkstemp()
        os.close( tmp_descriptor )
        command_line_args = [ 'etude.py' ,
                              '--reference-input' , 'tests/data/i2b2_2016_track-1_reference' ,
                              '--reference-config' , 'config/i2b2_2016_track-1.conf' ,
                              '--csv-out' , tmp_file ,
                              '--by-file' , '--by-type' , '--by-file-and-type' , '--by-type-and-file' ,
                              '--print-counts' , '--no-metrics' ]
        with patch.object( sys , 'argv' , command_line_args ):
            args = etude.init_args()
            namespaces , document_data , patterns = \
              args_and_configs.process_config( config_file = args.reference_config ,
                                               score_key = args.score_key ,
                                               score_values = args.score_values )
            import csv
            with open( presaved_file , 'r' ) as fp:
                reloaded_csv = fp.read()
            etude.count_ref_set( this_ns = namespaces ,
                                 this_dd = document_data ,
                                 this_patterns = patterns ,
                                 this_folder = args.reference_input ,
                                 args = args ,
                                 file_prefix = args.file_prefix ,
                                 file_suffix = args.file_suffix[ 0 ] )
            with open( tmp_file , 'r' ) as fp:
                new_csv = fp.read()
            assert new_csv == reloaded_csv
    finally:
        os.remove( tmp_file )


#############################################
## Test scoring annotations
#############################################


