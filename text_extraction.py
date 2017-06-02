import xml.etree.ElementTree as ET

def extract_annotations_kernel( ingest_file ,
                                annotation_path ,
                                tag_name ,
                                begin_attribute = None ,
                                end_attribute = None ,
                                text_attribute = None ,
                                default_score = 'FN' ):
    strict_starts = {}
    ##
    tree = ET.parse( ingest_file )
    root = tree.getroot()
    ## TODO - allow arbitrary namespaces either read from file or as argument
    namespaces = { 'custom' : 'http:///webanno/custom.ecore' ,
                   'type' : 'http:///com/clinacuity/deid/nlp/uima/type.ecore'  ,
                   'type2' : 'http:///com/clinacuity/deid/uima/core/type.ecore'  ,
                   'type4' : 'http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore' }
    ##
    for annot in root.findall( annotation_path , namespaces ):
        if( begin_attribute != None ):
            begin_pos = annot.get( begin_attribute )
        if( end_attribute != None ):
            end_pos = annot.get( end_attribute )
        if( text_attribute == None ):
            raw_text = annot.text
        else:
            raw_text = annot.get( text_attribute )
        new_entry = dict( end_pos = end_pos ,
                          raw_text = raw_text ,
                          type = tag_name ,
                          score = default_score )
        if( begin_pos in strict_starts.keys() ):
            strict_starts[ begin_pos ].append( new_entry )
        else:
            strict_starts[ begin_pos ] = [ new_entry ]
        ##print( '\t{}\t{}\t{}'.format( begin_pos , end_pos , raw_text ) )
    ## 
    return strict_starts


def extract_annotations( ingest_file ,
                         patterns ):
    annotations = {}
    for pattern in patterns:
        annotations.update( 
            extract_annotations_kernel( ingest_file ,
                                        annotation_path = pattern[ 'xpath' ] ,
                                        tag_name = pattern[ 'type' ] ,
                                        begin_attribute = pattern[ 'begin_attr' ] ,
                                        end_attribute = pattern[ 'end_attr' ] ) )
    return annotations


