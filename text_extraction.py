import json
import xml.etree.ElementTree as ET

def extract_annotations_kernel( ingest_file ,
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
        if( end_attribute != None ):
            end_pos = annot.get( end_attribute )
        if( text_attribute == None ):
            raw_text = annot.text
        else:
            raw_text = annot.get( text_attribute )
        new_entry = dict( begin_pos = begin_pos ,
                          end_pos = end_pos ,
                          raw_text = raw_text ,
                          type = tag_name )
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
                         patterns ,
                         out_file = None ):
    annotations = {}
    for pattern in patterns:
        annotations.update( 
            extract_annotations_kernel( ingest_file ,
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


