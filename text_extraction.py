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
        while( offset_mapping[ position ] == None ):
            position = str( int( position ) + direction )
        return offset_mapping[ position ]


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
                                text_attribute = None ):
    found_annots = {}
    strict_starts = {}
    ##
    tree = ET.parse( ingest_file )
    root = tree.getroot()
    ##
    try:
        found_annots = root.findall( annotation_path , namespaces )
    except SyntaxError, e:
        print( 'I had a problem parsing the XML file.  Are you sure your XPath is correct and matches your namespace?\n\tSkipping file ({}) and XPath ({})\n\tReported Error:  {}'.format( ingest_file , annotation_path , e ) )
        return strict_starts
    ##
    for annot in found_annots:
        if( begin_attribute != None ):
            begin_pos = annot.get( begin_attribute )
            begin_pos_mapped = map_position( offset_mapping , begin_pos , 1 )
        if( end_attribute != None ):
            ## TODO - add flag to distinguish between conditions
            ##        when the end_pos marks the last character
            ##        vs. when the end_pos is the position after
            ##        the last character
            end_pos = annot.get( end_attribute )
            end_pos_mapped = map_position( offset_mapping , end_pos , -1 )
            if( not bool( offset_mapping ) ):
                end_pos_mapped = None
            else:
                offset_key = end_pos
                while( offset_mapping[ offset_key ] == None ):
                    offset_key = str( int( offset_key ) - 1 )
                end_pos_mapped = offset_mapping[ offset_key ]
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
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = [ new_entry ]
    ## 
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
    return strict_starts


def write_annotations_to_disk( annotations , out_file ):
    if( out_file == None ):
        return
    ##
    ## TODO - add directory existence check
    with open( out_file , 'w' ) as output:
        json.dump( annotations , output ,
                   indent = 4 )


#############################################
## Accessing the original raw content for
## a document
#############################################


def split_content( raw_text , offset_mapping ):
    list_of_chars = list( raw_text )
    init_offset = 0
    mapped_offset = 0
    for char in list_of_chars:
        if( char.isspace() ):
            offset_mapping[ '{}'.format( init_offset ) ] = None
        else:
            offset_mapping[ '{}'.format( init_offset ) ] = '{}'.format( mapped_offset )
            mapped_offset += 1
        init_offset += 1
    return offset_mapping
    

def extract_chars( ingest_file ,
                   namespaces ,
                   document_data ):
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
        return None , offset_mapping
    ##
    tree = ET.parse( ingest_file )
    root = tree.getroot()
    ##
    try:
        found_annots = root.findall( content_path , namespaces )
    except SyntaxError, e:
        print( 'I had a problem parsing the XML file.  Are you sure your XPath is correct and matches your namespace?\n\tSkipping file ({}) and XPath ({})\n\tReported Error:  {}'.format( ingest_file , content_path , e ) )
        return None , offset_mapping
    ##
    raw_text = None
    for annot in found_annots:
        if( cdata_flag ):
            raw_text = annot.text
        elif( attribute_flag ):
            raw_text = annot.attrib[ attribute_name ]
    ##
    if( raw_text != None ):
        offset_mapping = split_content( raw_text ,
                                        offset_mapping )
    return raw_text , offset_mapping
    

def extract_plaintext( ingest_file ):
    offset_mapping = {}
    ##
    with open( ingest_file , 'r' ) as fp:
        raw_text = fp.read()
    offset_mapping = split_content( raw_text ,
                                    offset_mapping )
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
                         ignore_whitespace = True ,
                         out_file = None ):
    raw_content = None
    annotations = {}
    offset_mapping = {}
    file_dictionary = {}
    if( bool( document_data ) ):
        if( 'format' in document_data and
            document_data[ 'format' ] == 'txt' ):
            raw_content , offset_mapping = extract_plaintext( ingest_file )

        else:
            raw_content , offset_mapping = extract_chars( ingest_file ,
                                                          namespaces ,
                                                          document_data )
    for pattern in patterns:
        if( 'delimiter' in pattern ):
            annotations.update( 
                extract_annotations_plaintext( offset_mapping = offset_mapping ,
                                               raw_content = raw_content ,
                                               delimiter = \
                                                 pattern[ 'delimiter' ] ,
                                               tag_name = pattern[ 'type' ] ) )
        elif( 'xpath' in pattern and
              'begin_attr' in pattern and
              'end_attr' in pattern ):
            annotations.update( 
                extract_annotations_xml( ingest_file ,
                                         offset_mapping = offset_mapping ,
                                         namespaces = namespaces ,
                                         annotation_path = pattern[ 'xpath' ] ,
                                         tag_name = pattern[ 'type' ] ,
                                         begin_attribute = \
                                           pattern[ 'begin_attr' ] ,
                                         end_attribute = \
                                           pattern[ 'end_attr' ] ) )
        else:
            print( 'WARNING:  Skipping pattern because it is missing essential elements:\n\n{}'.format( pattern ) )
    file_dictionary = dict( raw_content = raw_content ,
                            offset_mapping = offset_mapping ,
                            annotations = annotations )
    ##
    write_annotations_to_disk( file_dictionary , out_file )
    return offset_mapping , annotations

