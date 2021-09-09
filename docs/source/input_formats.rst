Input Formats & Support Details
=============================================

Simple Plain Text
--------------------------------

Newlines for Sentences
~~~~~~~~~~~~~~~~~~~~~~

Local sample configuration files (under `config/`):

* `plaintext_sentences.conf`

  
Structured Plain Text (e.g., csv)
---------------------------------


CSV with Start, End, and Negation Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `csv_diagnoses.conf`

If the configuration file includes a key/value pair for `Opt Col`,
then we forcibly include the following three available values for this
column:

* affirmed
* negated
* possible


brat Annotation
~~~~~~~~~~~~~~~

The `brat rapid annotation tool <http://brat.nlplab.org/>`_ generates
`brat standoff format <http://brat.nlplab.org/standoff.html>`_.
Annotations are stored in a seconardy file (`*.ann`) while the
original text is found in a plain text file (`*.txt`). This standoff
format uses character offsets to locate spans:  "*All offsets all [sic]
indexed from 0 and include the character at the start offset but
exclude the character at the end offset.*"  See `BioNLP Shared Task
standoff format <http://2011.bionlp-st.org/home/file-formats>`_ for a
related format.

**Limitations:**
The extraction engine currently only handles continous text-bound
annotations for evaluation.  Binary attributes can be extracted and
included in the evaluation dictionary but are not scored themselves.
Discontinous text-bound annotations, relations, events, multi-value
attributes, normalizations, and notes are not supported.

Local sample configuration files (under `config/`):

* `brat_problems_allergies_standoff.conf`


XML Formats
--------------------------------

UIMA CAS XMI
~~~~~~~~~~~~~~~

Local sample configuration files (under `config/`):

* `CAS_XMI.conf`
* `i2b2_2016_track-1.conf`
* `uima_sentences.conf`
* `webanno_phi_xmi.conf`
* `webanno_problems_allergies_xmi.conf`
* `webanno_uima_xmi.conf`
  
  
Other
~~~~~~~~~~~~~~~

Extra sample configuration files (via `the ETUDE engine configs
<https://github.com/MUSC-TBIC/etude-engine-configs>`_ repository): 

* `i2b2/...`
* `n2c2/n2c2_2018_track-1.conf`

