import sys
import logging as log

import os
import json
import xml.etree.ElementTree as ET
import re



#############################################
## Minor helper functions to help simplify
## the apparent logic of extracting out
## annotations
#############################################


def create_annotation_entry( begin_pos , begin_pos_mapped ,
                             end_pos , end_pos_mapped ,
                             raw_text ,
                             tag_name ):
    new_entry = dict( begin_pos = begin_pos ,
                      end_pos = end_pos ,
                      raw_text = raw_text ,
                      type = tag_name )
    ##
    if( begin_pos_mapped != None ):
        new_entry[ 'begin_pos_mapped' ] = begin_pos_mapped
    ##
    if( end_pos_mapped != None ):
        new_entry[ 'end_pos_mapped' ] = end_pos_mapped
    return new_entry


def map_position( offset_mapping , position , direction ):
    if( not bool( offset_mapping ) ):
        return None
    else:
        try:
            while( offset_mapping[ position ] == None ):
                position = str( int( position ) + direction )
            return offset_mapping[ position ]
        except KeyError:
            if( direction < 0 ):
                return 'EOF'
            elif( direction > 0 ):
                return 'SOF'
            else:
                return None


#############################################
## 
#############################################

def extract_annotations_xml( ingest_file ,
                             offset_mapping ,
                             annotation_path ,
                             tag_name ,
                             namespaces = {} ,
                             begin_attribute = None ,
                             end_attribute = None ,
                             text_attribute = None ,
                             optional_attributes = [] ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    found_annots = {}
    strict_starts = {}
    ##
    tree = ET.parse( ingest_file )
    root = tree.getroot()
    ##
    try:
        found_annots = root.findall( annotation_path , namespaces )
    except SyntaxError, e:
        log.warn( 'I had a problem parsing the XML file.  Are you sure your XPath is correct and matches your namespace?\n\tSkipping file ({}) and XPath ({})\n\tReported Error:  {}'.format( ingest_file , annotation_path , e ) )
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return strict_starts
    ##
    log.debug( 'Found {} annotation(s) matching the pattern \'{}\''.format(
        len( found_annots ) , annotation_path ) )
    for annot in found_annots:
        if( begin_attribute != None ):
            try:
                begin_pos = annot.get( begin_attribute )
                begin_pos_mapped = map_position( offset_mapping , begin_pos , 1 )
            except NameError, e:
                log.error( 'NameError:  {}'.format( e ) )
        if( end_attribute != None ):
            ## TODO - add flag to distinguish between conditions
            ##        when the end_pos marks the last character
            ##        vs. when the end_pos is the position after
            ##        the last character
            try:
                end_pos = annot.get( end_attribute )
                end_pos_mapped = map_position( offset_mapping , end_pos , -1 )
            except NameError, e:
                log.error( 'NameError:  {}'.format( e ) )
        if( text_attribute == None ):
            raw_text = annot.text
        else:
            raw_text = annot.get( text_attribute )
        new_entry = create_annotation_entry( begin_pos = begin_pos ,
                                             begin_pos_mapped = begin_pos_mapped ,
                                             end_pos = end_pos ,
                                             end_pos_mapped = end_pos_mapped ,
                                             raw_text = raw_text ,
                                             tag_name = tag_name )
        ##
        for optional_attr in optional_attributes:
            new_entry[ optional_attr ] = annot.get( optional_attr )
        ##
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = [ new_entry ]
    ## 
    return strict_starts

def extract_annotations_brat_standoff( ingest_file ,
                                       offset_mapping ,
                                       type_prefix ,
                                       tag_name ,
                                       optional_attributes = [] ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    annots_by_index = dict()
    ##
    try:
        with open( ingest_file , 'r' ) as fp:
            for line in fp:
                line = line.rstrip()
                ## T1	Organization 0 43	International Business Machines Corporation
                matches = re.match( '^' + type_prefix + '([0-9]+)\s+(\w+)\s+([0-9]+)\s+([0-9]+)\s+(.*)' ,
                                    line )
                if( matches and matches.group( 2 ) == tag_name ):
                    match_index = matches.group( 1 )
                    begin_pos = matches.group( 3 )
                    begin_pos_mapped = map_position( offset_mapping , begin_pos , 1 )
                    end_pos = matches.group( 4 )
                    end_pos_mapped = map_position( offset_mapping , end_pos , -1 )
                    raw_text = matches.group( 5 )
                    new_entry = create_annotation_entry( begin_pos = begin_pos ,
                                                         begin_pos_mapped = begin_pos_mapped ,
                                                         end_pos = end_pos ,
                                                         end_pos_mapped = end_pos_mapped ,
                                                         raw_text = raw_text ,
                                                         tag_name = tag_name )
                    new_entry[ 'match_index' ] = '{}{}'.format( type_prefix , match_index )
                    for optional_attr in optional_attributes:
                        ## TODO - quick hack to match attributes (see below)
                        key = optional_attr.lower()
                        if( key == 'notpatient' ):
                            key = 'not_patient'
                        new_entry[ key ] = 'false'
                    ##
                    annots_by_index[ new_entry[ 'match_index' ] ] = new_entry
                    continue
                ##
                ## A1	Negated T34
                matches = re.match( '^A([0-9]+)\s+(\w+)\s+([A-Z][0-9]+)$' ,
                                    line )
                if( matches ):
                    match_index = matches.group( 3 )
                    attribute = matches.group( 2 )
                    if( attribute in optional_attributes and
                        match_index in annots_by_index.keys() ):
                        ## TODO - quick hack to match attributes (see above)
                        key = attribute.lower()
                        if( key == 'notpatient' ):
                            key = 'not_patient'
                        annots_by_index[ match_index ][ key ] = 'true'
                        continue
    except IOError, e:
        log.warn( 'I had a problem reading the standoff notation file ({}).\n\tReported Error:  {}'.format( ingest_file ,
                                                                                                            e ) )
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    strict_starts = {}
    for match_index in annots_by_index:
        new_entry = annots_by_index[ match_index ]
        begin_pos = new_entry[ 'begin_pos' ]
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = [ new_entry ]
    return strict_starts


def extract_annotations_plaintext( offset_mapping ,
                                   raw_content ,
                                   delimiter ,
                                   tag_name ):
    strict_starts = {}
    init_offset = 0
    last_offset = 0
    ##
    list_of_chars = list( raw_content )
    ##
    for char in list_of_chars:
        if( re.search( delimiter , char ) ):
            ## Skip when we see multiple of the same delimiter in a row
            if( init_offset == last_offset ):
                init_offset += 1
                last_offset = init_offset
                continue
            begin_pos = str( last_offset )
            begin_pos_mapped = map_position( offset_mapping , begin_pos , 1 )
            ## TODO - add flag to distinguish between conditions
            ##        when the end_pos marks the last character
            ##        vs. when the end_pos is the position after
            ##        the last character
            last_offset = init_offset + 1
            end_pos = str( init_offset )
            end_pos_mapped = map_position( offset_mapping , end_pos , -1 )
            raw_text = ''.join( list_of_chars[ int( begin_pos ):int( end_pos ) ] )
            new_entry = create_annotation_entry( begin_pos = begin_pos ,
                                                 begin_pos_mapped = \
                                                   begin_pos_mapped ,
                                                 end_pos = end_pos ,
                                                 end_pos_mapped = end_pos_mapped ,
                                                 raw_text = raw_text ,
                                                 tag_name = tag_name )
            ##
            if( begin_pos in strict_starts.keys() ):
                strict_starts[ begin_pos ].append( new_entry )
            else:
                strict_starts[ begin_pos ] = [ new_entry ]
        init_offset += 1
        ##
    if( last_offset < init_offset ):
        begin_pos = str( last_offset )
        begin_pos_mapped = map_position( offset_mapping , begin_pos , 1 )
        ## TODO - add flag to distinguish between conditions
        ##        when the end_pos marks the last character
        ##        vs. when the end_pos is the position after
        ##        the last character
        last_offset = init_offset + 1
        end_pos = str( init_offset )
        end_pos_mapped = map_position( offset_mapping , end_pos , -1 )
        raw_text = ''.join( list_of_chars[ int( begin_pos ):int( end_pos ) ] )
        new_entry = create_annotation_entry( begin_pos = begin_pos ,
                                             begin_pos_mapped = begin_pos_mapped ,
                                             end_pos = end_pos ,
                                             end_pos_mapped = end_pos_mapped ,
                                             raw_text = raw_text ,
                                             tag_name = tag_name )
        ##
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = [ new_entry ]
    ## 
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    ##
    return strict_starts


def write_annotations_to_disk( annotations , out_file ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    if( out_file == None ):
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return
    ##
    ## TODO - add directory existence check
    with open( out_file , 'w' ) as output:
        json.dump( annotations , output ,
                   indent = 4 )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )


def split_content( raw_text , offset_mapping , skip_chars ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    list_of_chars = list( raw_text )
    init_offset = 0
    mapped_offset = 0
    for char in list_of_chars:
        if( re.match( skip_chars , char ) ):
            offset_mapping[ '{}'.format( init_offset ) ] = None
        else:
            offset_mapping[ '{}'.format( init_offset ) ] = '{}'.format( mapped_offset )
            mapped_offset += 1
        init_offset += 1
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return offset_mapping
    

def extract_chars( ingest_file ,
                   namespaces ,
                   document_data ,
                   skip_chars = None ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    offset_mapping = {}
    ##
    cdata_flag = False
    attribute_flag = False
    if( 'cdata_xpath' in document_data.keys() ):
        cdata_flag = True
        content_path = document_data[ 'cdata_xpath' ]
    elif( 'content_attribute' in document_data.keys() ):
        attribute_flag = True
        content_path = document_data[ 'tag_xpath' ]
        attribute_name = document_data[ 'content_attribute' ]
    else:
        log.debug( "Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return None , offset_mapping
    ##
    tree = ET.parse( ingest_file )
    root = tree.getroot()
    ##
    try:
        found_annots = root.findall( content_path , namespaces )
    except SyntaxError, e:
        log.warn( 'I had a problem parsing the XML file.  Are you sure your XPath is correct and matches your namespace?\n\tSkipping file ({}) and XPath ({})\n\tReported Error:  {}'.format( ingest_file , content_path , e ) )
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return None , offset_mapping
    ##
    raw_text = None
    log.debug( 'Found {} match(es) for the pattern \'{}\''.format( len( found_annots ) ,
                                                                   content_path ) )
    if( len( found_annots ) > 1 ):
        log.warn( 'Expected to only find a single pattern matching content XPath (\'{}\') but found {}.  Using first match.'.format( content_path , len( found_annots ) ) )
    elif( len( found_annots ) == 0 ):
        log.warn( 'Expected to find exactly one match for content XPath (\'{}\') but found {}.  Returning empty document content.'.format( content_path , len( found_annots ) ) )
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return None , offset_mapping
    for annot in found_annots:
        if( cdata_flag ):
            raw_text = annot.text
            break
        elif( attribute_flag ):
            try:
                raw_text = annot.attrib[ attribute_name ]
                break
            except KeyError, e:
                log.warn( 'KeyError:  could not find attribute_name {} in the matched path \'{}\''.format( e , content_path ) )
                raw_text = None
    ##
    if( raw_text != None and skip_chars != None ):
        offset_mapping = split_content( raw_text ,
                                        offset_mapping ,
                                        skip_chars )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return raw_text , offset_mapping
    

def extract_plaintext( ingest_file , skip_chars ):
    offset_mapping = {}
    ##
    with open( ingest_file , 'r' ) as fp:
        raw_text = fp.read()
    if( raw_text != None and skip_chars != None ):
        offset_mapping = split_content( raw_text ,
                                        offset_mapping ,
                                        skip_chars )
    return raw_text , offset_mapping


def align_tokens_on_whitespace( dictionary ,
                                out_file ):
    if( out_file != None and
        os.path.exists( out_file ) ):
        os.remove( out_file )
    mapping = dictionary[ 'offset_mapping' ]
    keys = mapping.keys()
    content = dictionary[ 'raw_content' ]
    keys.sort( key = int )
    token_start = None
    for this_token in keys:
        ##print( '{}\t{}\t{}'.format( token_start ,
        ##                                this_token ,
        ##                                mapping[ this_token ] ) )
        if( mapping[ this_token ] != None and
            token_start == None ):
            token_start = this_token
        elif( mapping[ this_token ] == None and
              token_start != None ):
            if( out_file != None ):
                with open( out_file , 'a' ) as fp:
                    fp.write( '{}\n'.format( ##token_start , previous_token ,
                        content[ int( token_start ):int( this_token ) ] ) )
            token_start = None
    #print( '{} vs. {}'.format( len( dictionary[ 'raw_content' ] ) ,
    #                           len( dictionary[ 'raw_content' ] ) ) )


#############################################
## 
#############################################

def extract_annotations( ingest_file ,
                         namespaces ,
                         document_data ,
                         patterns ,
                         skip_chars = None ,
                         out_file = None ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    raw_content = None
    annotations = {}
    offset_mapping = {}
    file_dictionary = {}
    if( bool( document_data ) ):
        if( 'format' in document_data and
            document_data[ 'format' ] == 'txt' ):
            try:
                raw_content , offset_mapping = extract_plaintext( ingest_file ,
                                                                  skip_chars )
            except:
                e = sys.exc_info()[0]
                log.error( 'Uncaught exception in extract_plaintext:  {}'.format( e ) )
        elif( 'format' in document_data and
              document_data[ 'format' ] == '.ann .txt' ):
            ## TODO use format to change filename according to pattern
            ## document_data[ 'format' ]
            plaintext_alternate_file = re.sub( '.ann$' ,
                                               '.txt' ,
                                               ingest_file )
            try:
                raw_content , offset_mapping = extract_plaintext( plaintext_alternate_file ,
                                                                  skip_chars )
            except:
                e = sys.exc_info()[0]
                log.error( 'Uncaught exception in extract_plaintext:  {}'.format( e ) )
        else:
            try:
                raw_content , offset_mapping = extract_chars( ingest_file ,
                                                              namespaces ,
                                                              document_data ,
                                                              skip_chars )
            except ET.ParseError, e:
                log.warn( 'ParseError in file ({}):  {}'.format( ingest_file , e ) )
                log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
                return offset_mapping , annotations
            except:
                e = sys.exc_info()[0]
                log.error( 'Uncaught exception in extract_chars:  {}'.format( e ) )
    if( skip_chars and raw_content == None ):
        log.error( 'I could not find the raw content for this document but was asked to ignore its whitespace.  Add document data to the config file for extracting raw content or use the --heed-whitespace flag.' )
        log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
        return offset_mapping , annotations
    for pattern in patterns:
        new_annots = None
        if( 'delimiter' in pattern ):
            new_annots = \
                extract_annotations_plaintext( offset_mapping = offset_mapping ,
                                               raw_content = raw_content ,
                                               delimiter = \
                                                 pattern[ 'delimiter' ] ,
                                               tag_name = pattern[ 'type' ] )
        elif( 'type_prefix' in pattern ):
            new_annots = \
                extract_annotations_brat_standoff( ingest_file ,
                                                   offset_mapping = offset_mapping ,
                                                   type_prefix = \
                                                     pattern[ 'type_prefix' ] ,
                                                   tag_name = pattern[ 'type' ] ,
                                                   optional_attributes = \
                                                   pattern[ 'optional_attributes' ] )
        elif( 'xpath' in pattern and
              'begin_attr' in pattern and
              'end_attr' in pattern ):
            new_annots = \
                extract_annotations_xml( ingest_file ,
                                         offset_mapping = offset_mapping ,
                                         namespaces = namespaces ,
                                         annotation_path = pattern[ 'xpath' ] ,
                                         tag_name = pattern[ 'type' ] ,
                                         begin_attribute = \
                                           pattern[ 'begin_attr' ] ,
                                         end_attribute = \
                                           pattern[ 'end_attr' ] ,
                                         optional_attributes = \
                                           pattern[ 'optional_attributes' ] )
        else:
            print( 'WARNING:  Skipping pattern because it is missing essential elements:\n\n{}'.format( pattern ) )
        ##
        ##annotations.update( new_annots )
        if( new_annots != None ):
            for new_annot_key in new_annots.keys():
                if( new_annot_key in annotations.keys() ):
                    combined_annots = annotations[ new_annot_key ] + new_annots[ new_annot_key ] 
                    annotations.update( { new_annot_key : combined_annots } )
                else:
                    annotations.update( { new_annot_key : new_annots[ new_annot_key ] } )
    file_dictionary = dict( raw_content = raw_content ,
                            offset_mapping = offset_mapping ,
                            annotations = annotations )
    ##
    ##
    try:
        write_annotations_to_disk( file_dictionary , out_file )
    except IOError as e:
        log.error( 'IOError caught in write_annotations_to_disk:  {}'.format( e ) )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in write_annotations_to_disk:  {}'.format( e ) )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return offset_mapping , annotations

