import sys
import logging as log

import json
import xml.etree.ElementTree as ET

def extract_annotations_kernel( ingest_file ,
                                offset_mapping ,
                                annotation_path ,
                                tag_name ,
                                namespaces = {} ,
                                begin_attribute = None ,
                                end_attribute = None ,
                                text_attribute = None ):
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
                if( not bool( offset_mapping ) ):
                    begin_pos_mapped = None
                else:
                    offset_key = begin_pos
                    while( offset_mapping[ offset_key ] == None ):
                        offset_key = str( int( offset_key ) - 1 )
                    begin_pos_mapped = offset_mapping[ offset_key ]
            except NameError, e:
                log.error( 'NameError:  {}'.format( e ) )
        if( end_attribute != None ):
            ## TODO - add flag to distinguish between conditions
            ##        when the end_pos marks the last character
            ##        vs. when the end_pos is the position after
            ##        the last character
            try:
                end_pos = annot.get( end_attribute )
                if( not bool( offset_mapping ) ):
                    end_pos_mapped = None
                else:
                    offset_key = end_pos
                    while( offset_mapping[ offset_key ] == None ):
                        offset_key = str( int( offset_key ) - 1 )
                    end_pos_mapped = offset_mapping[ offset_key ]
            except NameError, e:
                log.error( 'NameError:  {}'.format( e ) )
        if( text_attribute == None ):
            raw_text = annot.text
        else:
            raw_text = annot.get( text_attribute )
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
        ##
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = [ new_entry ]
    ## 
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
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


def extract_annotations( ingest_file ,
                         namespaces ,
                         document_data ,
                         patterns ,
                         ignore_whitespace = True ,
                         out_file = None ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    raw_content = None
    annotations = {}
    offset_mapping = {}
    file_dictionary = {}
    if( bool( document_data ) ):
        try:
            raw_content , offset_mapping = extract_chars( ingest_file ,
                                                          namespaces ,
                                                          document_data ,
                                                          out_file )
        except:
            e = sys.exc_info()[0]
            log.error( 'Uncaught exception in extract_chars:  {}'.format( e ) )
    for pattern in patterns:
        annotations.update( 
            extract_annotations_kernel( ingest_file ,
                                        offset_mapping = offset_mapping ,
                                        namespaces = namespaces ,
                                        annotation_path = pattern[ 'xpath' ] ,
                                        tag_name = pattern[ 'type' ] ,
                                        begin_attribute = \
                                            pattern[ 'begin_attr' ] ,
                                        end_attribute = \
                                            pattern[ 'end_attr' ] ) )
    file_dictionary = dict( raw_content = raw_content ,
                            offset_mapping = offset_mapping ,
                            annotations = annotations )
    ##
    try:
        write_annotations_to_disk( file_dictionary , out_file )
    except:
        e = sys.exc_info()[0]
        log.error( 'Uncaught exception in write_annotations_to_disk:  {}'.format( e ) )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return offset_mapping , annotations


def split_content( raw_text , offset_mapping ):
    log.debug( "Entering '{}'".format( sys._getframe().f_code.co_name ) )
    list_of_chars = list( raw_text )
    init_offset = 0
    mapped_offset = 0
    for char in list_of_chars:
        if( char.isspace() ):
            offset_mapping[ '{}'.format( init_offset ) ] = None
        else:
            offset_mapping[ '{}'.format( init_offset ) ] = '{}'.format( mapped_offset )
            ##offset_mapping[ init_offset ] = mapped_offset
            mapped_offset += 1
        init_offset += 1
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return offset_mapping
    

## TODO - return character counts for printing/comparison
def extract_chars( ingest_file ,
                   namespaces ,
                   document_data ,
                   out_file = None ):
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
    if( raw_text != None ):
        offset_mapping = split_content( raw_text ,
                                        offset_mapping )
    log.debug( "-- Leaving '{}'".format( sys._getframe().f_code.co_name ) )
    return raw_text , offset_mapping

