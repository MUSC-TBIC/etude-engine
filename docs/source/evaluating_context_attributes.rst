Evaluating Context Attributes
=============================

Relevant command line arguments:

.. sourcecode:: bash
		
   --score-attributes
   --score-attributes <list,of,attributes,to,score>

   --by-attribute
   --by-type-and-attribute


Sample Test Data
----------------


Contextual attributes can be encoded as XML attributes. In the case of
this sample WebAnno document, each attribute was a binary flag that
could be set to `true` or `false`.  True Negatives (TNs) are indicated
by the corresponding XML attribute value being `False` (e.g.,
`negated="false"`).

.. sourcecode:: bash

   python ${ETUDE_DIR}/etude.py \
      --reference-input ${ETUDE_DIR}/tests/data \
      --reference-config ${ETUDE_DIR}/config/webanno_problems_allergies_xmi.conf \
      --test-input ${ETUDE_DIR}/tests/data \
      --test-config ${ETUDE_DIR}/config/webanno_problems_allergies_xmi.conf \
      --file-suffix "013_Conditional_Problem.xmi" \
      --by-type \
      --by-attribute \
      --score-attributes


In the following brat `.ann` file, context attributes are similar to
labels or notes added to an annotation. The default value should be
made explicit. These files assume a concept is `Present` unless
negated (e.g., `A17 Negated T22` is unpacked to meand that
`A(nnotation)17` indicates that concept `T22` is `Negated`). Likewise,
concepts are `Current` unless flagged `Historical`. True Negatives
(TNs) are indicated by the absence of a label.

.. sourcecode:: bash
   
   python3 ${ETUDE_DIR}/etude.py \
      --reference-input "${ETUDE_DIR}/tests/data/brat_reference" \
      --reference-config "${ETUDE_DIR}/config/brat_problems_allergies_standoff.conf" \
      --test-input "${ETUDE_DIR}/tests/data/brat_system_out" \
      --test-config "${ETUDE_DIR}/config/brat_problems_allergies_standoff.conf" \
      --file-suffix ".ann" \
      --by-type \
      -m TP FP FN Precision Recall F1 \
      --by-attribute \
      --score-attributes \
      --by-type-and-attribute


This sample CSV file has a single column with multiple possible value
in it. Because the metrics for `affirmed` vs. `negated` vs. `possible`
are in direct conflict, it is not meaningful to compare their
aggregate precision and recall. Instead, it is more reasonable to look
at their relative performance or accuracy as an attribute. True
Negatives (TNs) are indicated by a concept not being flagged for a
particular label. Every TN counted for `affirmed` should correlate
with a `TP`, `FP`, or `FN` with both `negated` and `possible`.

.. sourcecode:: bash

   python3 etude.py \
      --reference-config config/csv_diagnoses.conf \
      --reference-input tests/data/csv_reference_out \
      --test-config config/csv_diagnoses.conf \
      --test-input tests/data/csv_system_out \
      --file-suffix ".csv" \
      --heed-whitespace \
      --fuzzy-match-flags exact partial \
      --score-attributes affirmed,negated,possible \
      --by-attribute \
      --by-type

