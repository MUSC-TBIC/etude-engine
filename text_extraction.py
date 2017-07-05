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
            begin_orig = None
            if( begin_pos in offset_mapping ):
                begin_orig = begin_pos
                begin_pos = offset_mapping[ begin_pos ]
        if( end_attribute != None ):
            end_pos = annot.get( end_attribute )
            end_orig = None
            if( end_pos in offset_mapping ):
                end_orig = end_pos
                end_pos = offset_mapping[ end_pos ]
        if( text_attribute == None ):
            raw_text = annot.text
        else:
            raw_text = annot.get( text_attribute )
        new_entry = dict( begin_pos = begin_pos ,
                          end_pos = end_pos ,
                          raw_text = raw_text ,
                          type = tag_name )
        if( begin_orig != None ):
            new_entry[ 'begin_orig' ] = begin_orig
        if( end_orig != None ):
            new_entry[ 'end_orig' ] = end_orig
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


def extract_annotations( ingest_file ,
                         namespaces ,
                         document_data ,
                         patterns ,
                         out_file = None ):
    annotations = {}
    offset_mapping = {}
    if( bool( document_data ) ):
        offset_mapping = extract_chars( ingest_file ,
                                        namespaces ,
                                        document_data ,
                                        out_file )
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
    ##
    write_annotations_to_disk( annotations , out_file )
    return annotations


def split_content( raw_text , offset_mapping ):
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
    return offset_mapping
    

## TODO - return character counts for printing/comparison
def extract_chars( ingest_file ,
                   namespaces ,
                   document_data ,
                   out_file = None ):
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
        return offset_mapping
    ##
    tree = ET.parse( ingest_file )
    root = tree.getroot()
    ##
    try:
        found_annots = root.findall( content_path , namespaces )
    except SyntaxError, e:
        print( 'I had a problem parsing the XML file.  Are you sure your XPath is correct and matches your namespace?\n\tSkipping file ({}) and XPath ({})\n\tReported Error:  {}'.format( ingest_file , content_path , e ) )
        return offset_mapping
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
    ##
    ##write_annotations_to_disk( annotations , out_file )
    ##return annotations
    return offset_mapping

