import pandas as pd

import scoring_metrics

#############################################
## Test helper functions
#############################################

def add_missing_fields( test_type ):
    score_card = scoring_metrics.new_score_card()
    new_types = score_card.keys()
    assert test_type not in new_types
    score_summary = scoring_metrics.add_missing_fields( score_card )
    score_types = score_summary.keys()
    assert test_type in score_types

def test_add_missing_fields_TP():
    add_missing_fields( 'TP' )

def test_add_missing_fields_FP():
    add_missing_fields( 'FP' )

def test_add_missing_fields_TN():
    add_missing_fields( 'TN' )

def test_add_missing_fields_FN():
    add_missing_fields( 'FN' )


## TODO - test_norm_summary variants


## TODO - test_print_score_summary variants


#############################################
## Test scoring metrics
#############################################

## TODO - add a range of edge case examples to scoring metric tests

def test_accuracy_all_zero():
    assert scoring_metrics.accuracy( 0 , 0 , 0 , 0 ) == 0.0

def test_accuracy_all_ones():
    assert scoring_metrics.accuracy( 1 , 1 , 1 , 1 ) == 0.5

def test_precision_all_zero():
    assert scoring_metrics.precision( 0 , 0 ) == 0.0

def test_precision_all_ones():
    assert scoring_metrics.precision( 1 , 1 ) == 0.5

def test_recall_all_zero():
    assert scoring_metrics.recall( 0 , 0 ) == 0.0

def test_recall_all_ones():
    assert scoring_metrics.recall( 1 , 1 ) == 0.5

def test_specificity_all_zero():
    assert scoring_metrics.specificity( 0 , 0 ) == 0.0

def test_specificity_all_ones():
    assert scoring_metrics.specificity( 1 , 1 ) == 0.5

def test_f_score_all_zero():
    assert scoring_metrics.f_score( 0.0 , 0.0 ) == 0.0

def test_f_score_even_split():
    assert scoring_metrics.f_score( 0.5 , 0.5 ) == 0.5

def test_f_score_all_ones():
    assert scoring_metrics.f_score( 1.0 , 1.0 ) == 1

def test_f_score_low_precision():
    assert scoring_metrics.f_score( 0.1 , 1.0 ) == 0.18181818181818182

def test_f_score_max_precision():
    assert scoring_metrics.f_score( 1.0 , 0.0 ) == 0.0

def test_f_score_low_recall():
    assert scoring_metrics.f_score( 1.0 , 0.1 ) == 0.18181818181818182

def test_f_score_max_recall():
    assert scoring_metrics.f_score( 0.0 , 1.0 ) == 0.0

def test_f_score_beta_inversely_proportional_to_precision():
    assert scoring_metrics.f_score( 1.0 , 0.1 , beta = 1 ) < \
        scoring_metrics.f_score( 1.0 , 0.1 , beta = 0.5 )
    assert scoring_metrics.f_score( 1.0 , 0.1 , beta = 1 ) > \
        scoring_metrics.f_score( 1.0 , 0.1 , beta = 2 )

def test_f_score_beta_proportional_to_recall():
    assert scoring_metrics.f_score( 0.1 , 1.0 , beta = 1 ) > \
        scoring_metrics.f_score( 0.1 , 1.0 , beta = 0.5 )
    assert scoring_metrics.f_score( 0.1 , 1.0 , beta = 1 ) < \
        scoring_metrics.f_score( 0.1 , 1.0 , beta = 2 )

