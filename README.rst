
Documentation
================================

The latest documentation (compiled from the contents of the `docs` folder) can be viewed on-line:
`ETUDE Engine’s documentation <https://etude-engine.readthedocs.io/en/latest/index.html>`_

Documentation for the ETUDE engine is managed via reStructuredText files and `Sphinx <http://www.sphinx-doc.org/>`_.
If you don't have Sphinx installed, you should check out a quick primer (`First Steps with Sphinx <http://www.sphinx-doc.org/en/1.7/tutorial.html>`_) or install it as below:

.. sourcecode:: bash

   ## If you don't have Sphinx installed already
   pip install Sphinx

   ## Generate a locally viewable HTML version
   cd docs
   make html

The latest version of the documentation can be generated as locally viewable HTML:  file:///path/to/git/repository/docs/_build/html/index.html


Sample Runs
===========

Basic Run
---------

The simplest test run requires that we specify a reference directory and
a test directory. The default file matching assumes that our reference
and test files match names exactly and both end in ‘.xml’. With just the
two directory arguments, we get micro-average scores for the default
metrics across the full directory.

.. code:: bash

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_test

+---------------+-------+-----+-----+-------+
| exact         | TP    | FP  | TN  | FN    |
+===============+=======+=====+=====+=======+
| micro-average | 374.0 | 8.0 | 0.0 | 108.0 |
+---------------+-------+-----+-----+-------+

.. note::

   You may get a warning if you run the previous command from a
   directory other than `$ETUDE_DIR`:
   
   ``ERROR: No reference patterns extracted from config.  Bailing out
   now.``

   This warning is because the default configuration files use
   relative paths.  See the section below
   
In the next sample runs, you can see how to include a per-file score
breakdown and a per-annotation-type score breakdown.

.. code:: bash

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
       --by-file

+-----------------------+-------+-----+-----+-------+
| exact                 | TP    | FP  | TN  | FN    |
+=======================+=======+=====+=====+=======+
| micro-average         | 340.0 | 8.0 | 0.0 | 105.0 |
+-----------------------+-------+-----+-----+-------+
| 0005_gs.xml           | 31.0  | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| 0016_gs.xml           | 21.0  | 0.0 | 0.0 | 30.0  |
+-----------------------+-------+-----+-----+-------+
| 0267_gs.xml           | 27.0  | 0.0 | 0.0 | 32.0  |
+-----------------------+-------+-----+-----+-------+
| 0273_gs.xml           | 0.0   | 0.0 | 0.0 | 35.0  |
+-----------------------+-------+-----+-----+-------+
| 0389_gs.xml           | 26.0  | 8.0 | 0.0 | 8.0   |
+-----------------------+-------+-----+-----+-------+
| 0475_gs.xml           | 45.0  | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| 0617_gs.xml           | 32.0  | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| 0709_gs.xml           | 41.0  | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| 0982_gs.xml           | 95.0  | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| 0992_gs.xml           | 22.0  | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| macro-average by file | 340.0 | 8.0 | 0.0 | 105.0 |
+-----------------------+-------+-----+-----+-------+

.. code:: bash

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
       --by-type

+-----------------------+-------+-----+-----+-------+
| exact                 | TP    | FP  | TN  | FN    |
+=======================+=======+=====+=====+=======+
| micro-average         | 340.0 | 8.0 | 0.0 | 105.0 |
+-----------------------+-------+-----+-----+-------+
| Age                   | 63.0  | 2.0 | 0.0 | 29.0  |
+-----------------------+-------+-----+-----+-------+
| DateTime              | 91.0  | 2.0 | 0.0 | 33.0  |
+-----------------------+-------+-----+-----+-------+
| HCUnit                | 61.0  | 4.0 | 0.0 | 15.0  |
+-----------------------+-------+-----+-----+-------+
| OtherID               | 7.0   | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| OtherLoc              | 1.0   | 0.0 | 0.0 | 4.0   |
+-----------------------+-------+-----+-----+-------+
| OtherOrg              | 18.0  | 0.0 | 0.0 | 3.0   |
+-----------------------+-------+-----+-----+-------+
| Patient               | 16.0  | 0.0 | 0.0 | 3.0   |
+-----------------------+-------+-----+-----+-------+
| PhoneFax              | 5.0   | 0.0 | 0.0 | 1.0   |
+-----------------------+-------+-----+-----+-------+
| Provider              | 54.0  | 0.0 | 0.0 | 10.0  |
+-----------------------+-------+-----+-----+-------+
| StateCountry          | 14.0  | 0.0 | 0.0 | 7.0   |
+-----------------------+-------+-----+-----+-------+
| StreetCity            | 4.0   | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| Zip                   | 4.0   | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| eAddress              | 2.0   | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| macro-average by type | 340.0 | 8.0 | 0.0 | 105.0 |
+-----------------------+-------+-----+-----+-------+

Specifying Annotation Configs
-----------------------------

We can use the same reference corpus to analyze annotations generated by
UIMA’s DateTime tutorial (see link below). A minimal run requires
creating a matching dataset for the default configurations. Process the
I2B2 dev set using the DateTime tutorial provided with UIMA. Then,
because the output files for the I2B2 dev-annotations end in ‘.xml’ but
the UIMA tutorial files end in ‘.txt’, you need to specify a file suffix
translation rule. Also, the annotations are encoded slightly differently
by the tutorial descriptor than by the I2B2 reference. As such, you will
need to load a different configuration for the test directory to tell
ETUDE how to find and extract the annotations. (If you run this example
without the ‘–test-config’ argument, you should see all FN matches
because nothing can be extracted from the test corpus.)

Link:
http://uima.apache.org/downloads/releaseDocs/2.2.2-incubating/docs/html/tutorials_and_users_guides/tutorials_and_users_guides.html#ugr.tug.aae.building_aggregates

.. code:: bash

   export I2B2_CORPUS="/path/to/Corpora and annotations/2016 NGRID challenge (deid)/2016_track_1-deidentification"

   export I2B2_OUTPUT="/tmp/datetime-out"
   mkdir $I2B2_OUTPUT

   $UIMA_HOME/bin/runAE.sh \
     $UIMA_HOME/examples/descriptors/tutorial/ex3/TutorialDateTime.xml \
     $I2B2_CORPUS/dev-text \
     $I2B2_OUTPUT

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $I2B2_OUTPUT \
       --by-type \
       --file-suffix ".xml" ".txt" \
       --test-config config/CAS_XMI.conf

   #########   TP  FP  TN  FN
   aggregate   19.0    20.0    0.0 426.0
   Age 0.0 0.0 0.0 92.0
   DateTime    19.0    20.0    0.0 105.0
   HCUnit  0.0 0.0 0.0 76.0
   OtherID 0.0 0.0 0.0 7.0
   OtherLoc    0.0 0.0 0.0 5.0
   OtherOrg    0.0 0.0 0.0 21.0
   Patient 0.0 0.0 0.0 19.0
   PhoneFax    0.0 0.0 0.0 6.0
   Provider    0.0 0.0 0.0 64.0
   StateCountry    0.0 0.0 0.0 21.0
   StreetCity  0.0 0.0 0.0 4.0
   Zip 0.0 0.0 0.0 4.0
   eAddress    0.0 0.0 0.0 2.0

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $I2B2_OUTPUT \
       --file-suffix ".xml" ".txt"

   #########   TP  FP  TN  FN
   aggregate   0.0 0.0 0.0 445.0

Scoring on Different Fields
---------------------------

The above examples show scoring based on the default key in the
configuration file used for matching the reference to the test
configuration. You may wish to group annotations on different fields,
such as the parent class or long description.

.. code:: bash

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
       --by-type

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
       --by-type \
       --score-key "Parent"

   python $ETUDE_DIR/etude.py \
       --reference-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_reference \
       --test-input $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
       --by-type \
       --score-key "Long Name"

+-----------------------+-------+-----+-----+-------+
| exact                 | TP    | FP  | TN  | FN    |
+=======================+=======+=====+=====+=======+
| micro-average         | 341.0 | 7.0 | 0.0 | 104.0 |
+-----------------------+-------+-----+-----+-------+
| Address               | 22.0  | 0.0 | 0.0 | 7.0   |
+-----------------------+-------+-----+-----+-------+
| Contact Information   | 7.0   | 0.0 | 0.0 | 1.0   |
+-----------------------+-------+-----+-----+-------+
| Identifiers           | 7.0   | 0.0 | 0.0 | 0.0   |
+-----------------------+-------+-----+-----+-------+
| Locations             | 80.0  | 4.0 | 0.0 | 22.0  |
+-----------------------+-------+-----+-----+-------+
| Names                 | 70.0  | 0.0 | 0.0 | 13.0  |
+-----------------------+-------+-----+-----+-------+
| Time                  | 155.0 | 3.0 | 0.0 | 61.0  |
+-----------------------+-------+-----+-----+-------+
| macro-average by type | 341.0 | 7.0 | 0.0 | 104.0 |
+-----------------------+-------+-----+-----+-------+

+--------------------------------+-------+-----+-----+-------+
| exact                          | TP    | FP  | TN  | FN    |
+================================+=======+=====+=====+=======+
| micro-average                  | 340.0 | 8.0 | 0.0 | 105.0 |
+--------------------------------+-------+-----+-----+-------+
| Age Greater than 89            | 63.0  | 2.0 | 0.0 | 29.0  |
+--------------------------------+-------+-----+-----+-------+
| Date and Time Information      | 91.0  | 2.0 | 0.0 | 33.0  |
+--------------------------------+-------+-----+-----+-------+
| Electronic Address Information | 2.0   | 0.0 | 0.0 | 0.0   |
+--------------------------------+-------+-----+-----+-------+
| Health Care Provider Name      | 54.0  | 0.0 | 0.0 | 10.0  |
+--------------------------------+-------+-----+-----+-------+
| Health Care Unit Name          | 61.0  | 4.0 | 0.0 | 15.0  |
+--------------------------------+-------+-----+-----+-------+
| Other ID Numbers               | 7.0   | 0.0 | 0.0 | 0.0   |
+--------------------------------+-------+-----+-----+-------+
| Other Locations                | 1.0   | 0.0 | 0.0 | 4.0   |
+--------------------------------+-------+-----+-----+-------+
| Other Organization Name        | 18.0  | 0.0 | 0.0 | 3.0   |
+--------------------------------+-------+-----+-----+-------+
| Patient Name                   | 16.0  | 0.0 | 0.0 | 3.0   |
+--------------------------------+-------+-----+-----+-------+
| Phone, Fax, or Pager Number    | 5.0   | 0.0 | 0.0 | 1.0   |
+--------------------------------+-------+-----+-----+-------+
| State or Country               | 14.0  | 0.0 | 0.0 | 7.0   |
+--------------------------------+-------+-----+-----+-------+
| Street City Name               | 4.0   | 0.0 | 0.0 | 0.0   |
+--------------------------------+-------+-----+-----+-------+
| ZIP Code                       | 4.0   | 0.0 | 0.0 | 0.0   |
+--------------------------------+-------+-----+-----+-------+
| macro-average by type          | 340.0 | 8.0 | 0.0 | 105.0 |
+--------------------------------+-------+-----+-----+-------+

Custom Evaluation Print-Outs
================================

The majority of you evaluation output customization can be handled by the above command-line arguments.
However, sometimes you'll need to generate output that exactly matches some very specific formatting requirements.
For these instances, ETUDE supports custom print functions.
Currently, those print functions must be hard-coded into `scoring_metrics.py`.
Our roadmap includes the ability to load and trigger these print functions from a standard folder to make the system much more modular.
Until that point, you can see an example custom print-out that targets the `2018 n2c2 Track 1 <https://www.aclweb.org/portal/content/2018-n2c2-nlp-shared-task-and-workshop>`_ output format.
The configurations for this sample are in our sister repository:
`ETUDE Engine Configs for n2c2 <https://github.com/MUSC-TBIC/etude-engine-configs/tree/master/n2c2>`_
The original evaluation script for the competition, used as a point of reference, can be found on github:
`Evaluation scripts for the 2018 N2C2 shared tasks on clinical NLP  <https://github.com/filannim/2018_n2c2_evaluation_scripts>`_

.. code:: bash

   export ETUDE_DIR=etude-engine
   export ETUDE_CONFIGS_DIR=etude-engine-configs
   
   export N2C2_DATA=/tmp/n2c2

   python ${ETUDE_DIR}/etude.py \
     --reference-input ${N2C2_DATA}/train_annotations \
      --reference-config ${ETUDE_CONFIGS_DIR}/n2c2/2018_n2c2_track-1.conf \
      --test-input ${N2C2_DATA}/train_annotations \
      --test-config ${ETUDE_CONFIGS_DIR}/n2c2/2018_n2c2_track-1.conf \
      --no-metrics \
      --print-custom "2018 n2c2 track 1" \
      --fuzzy-match-flag exact \
      --file-suffix ".xml" \
      --empty-value 0.0


   ******************************************* TRACK 1 ********************************************
                         ------------ met -------------    ------ not met -------    -- overall ---
                         Prec.   Rec.    Speci.  F(b=1)    Prec.   Rec.    F(b=1)    F(b=1)  AUC   
              Abdominal  1.0000  1.0000  1.0000  1.0000    1.0000  1.0000  1.0000    1.0000  1.0000
           Advanced-cad  1.0000  1.0000  0.0000  1.0000    0.0000  0.0000  0.0000    0.5000  0.5000
          Alcohol-abuse  0.0000  0.0000  1.0000  0.0000    1.0000  1.0000  1.0000    0.5000  0.5000
             Asp-for-mi  1.0000  1.0000  0.0000  1.0000    0.0000  0.0000  0.0000    0.5000  0.5000
             Creatinine  1.0000  1.0000  1.0000  1.0000    1.0000  1.0000  1.0000    1.0000  1.0000
          Dietsupp-2mos  1.0000  1.0000  1.0000  1.0000    1.0000  1.0000  1.0000    1.0000  1.0000
             Drug-abuse  0.0000  0.0000  1.0000  0.0000    1.0000  1.0000  1.0000    0.5000  0.5000
                English  1.0000  1.0000  0.0000  1.0000    0.0000  0.0000  0.0000    0.5000  0.5000
                  Hba1c  1.0000  1.0000  1.0000  1.0000    1.0000  1.0000  1.0000    1.0000  1.0000
               Keto-1yr  0.0000  0.0000  1.0000  0.0000    1.0000  1.0000  1.0000    0.5000  0.5000
         Major-diabetes  1.0000  1.0000  1.0000  1.0000    1.0000  1.0000  1.0000    1.0000  1.0000
        Makes-decisions  1.0000  1.0000  0.0000  1.0000    0.0000  0.0000  0.0000    0.5000  0.5000
                Mi-6mos  1.0000  1.0000  1.0000  1.0000    1.0000  1.0000  1.0000    1.0000  1.0000
                         ------------------------------    ----------------------    --------------
        Overall (micro)  1.0000  1.0000  1.0000  1.0000    1.0000  1.0000  1.0000    1.0000  1.0000
        Overall (macro)  0.7692  0.7692  0.6923  0.7692    0.6923  0.6923  0.6923    0.7308  0.7308
   
                                                       10 files found


Contextually-Grounded Annotation Examples
---------------------------------------------

A second class of custom outputs is to generate listings of real annotations with left- and right-margins of context. Most often, you will want to use this type of output to generate a listing of all the FP annotations your system generated or all the FN annotations your system failed to find.

The generation of this output is dependent on a score card having been written to disk during a normal evaluation run. You'll also want to make sure to have generated a system output directory.  Both flags are show in examples below.  Additional flags let you determine how much of a context window (in characters) you want to see on the left and right of the annotation.

If we focus solely on the `partial` matches, then we're guaranteed to get FP and FN annotations that don't overlap. We don't distinguish between span mismatches and type mismatches.

.. code:: bash

   export ETUDE_DIR=etude-engine

   python3 ${ETUDE_DIR}/etude.py \
     --reference-input ${ETUDE_DIR}/tests/data/i2b2_2016_track-1_reference \
     --reference-config ${ETUDE_DIR}/config/i2b2_2016_track-1.conf \
     --test-input ${ETUDE_DIR}/tests/data/i2b2_2016_track-1_test \
     --test-config ${ETUDE_DIR}/config/i2b2_2016_track-1.conf \
     --file-suffix "xml" \
     --by-type \
     -m FP FN \
     --fuzzy-match-flags partial \
     --pretty-print \
     --test-out /tmp/system \
     --write-score-cards

   ## Use standard settings
   python3 ${ETUDE_DIR}/extract_samples.py \
     --score-card /tmp/system/metrics_partial_score_card.csv \
     --annotation-out /tmp/system

   ## Show a larger left margin than right margin
   python3 ${ETUDE_DIR}/extract_samples.py \
     --score-card /tmp/system/metrics_partial_score_card.csv \
     --annotation-out /tmp/system \
     --left-margin 25 \
     --right-margin 10

   ## Only print the FP annotations
   python3 ${ETUDE_DIR}/extract_samples.py \
     --score-card /tmp/system/metrics_partial_score_card.csv \
     --annotation-out /tmp/system \
     --metrics FP

   ## The system output filenames differ from the reference
   ## filenames in that they end in '.txt.xmi' rather than
   ## just '.txt'
   python3 ${ETUDE_DIR}/extract_samples.py \
     --score-card /tmp/system/metrics_partial_score_card.csv \
     --annotation-out /tmp/system \
     --file-suffix ".txt" ".txt.xmi"


Configuring Annotation Extraction
=================================

Several sample configurations are provided in the config/ folder. Each
long name for an annotation description should be unique due to how
Python’s configuration parser works. XPath’s should also be unique
within a config file but do not programmitically need to be. The begin
and end attribute are required for a pattern to be scorable.

::

   [ Long Name or Description ]
   Parent:           (optional; useful for merging multiple child types together for scoring)
   Short Name:  (optional; useful for displaying as column output name and merging
                          multiple XPaths into a single scoring category)
   XPath:            (required; pattern used by XPath to find annotation)
   Begin Attr:     (required; beginning or start offset attribute name)
   End Attr:       (required; end offset attribute name)
   Text Attr:      (optional; not used by anything currently)


Additional interesting or useful configuration files can be found in
our sister repository:
`ETUDE Engine Configs <https://github.com/MUSC-TBIC/etude-engine-configs>`_

Dependencies
============

Python module requirements for running ETUDE are included in the
requirements.txt file. You should be able to install all non-default
packages using pip:

.. code:: bash

   pip install -r requirements

   
Building with PyInstaller
================================

After installing all required dependencies (as above), you can opt to create a stand-alone version of the ETUDE engine with `PyInstaller <https://www.pyinstaller.org/>`_. 

The vanilla creation is
.. code:: bash

   cd $ETUDE_ENGINE_DIR
   
   pyinstaller --onefile --distpath=dist/linux etude.py
   pyinstaller --onefile --distpath=dist/osx etude.py
   pyinstaller --onefile --distpath=dist/windows etude.py

   
Testing
=======

Unit testing is done with the pytest module. Because of a bug in how
tests are processed in Python 2.7, you should run pytest indirectly
rather than directly:

.. code:: bash

   python -m pytest tests/

   ## You can also generate a coverate report in html format
   python2.7 -m pytest --cov-report html:cov_html_py2.7 --cov=./ tests/
   python3.7 -m pytest --cov-report html:cov_html_py3.7 --cov=./ tests/
   
   ## The junit file is helpful for automated systems or CI pipelines
   python -m pytest --junitxml=junit.xml tests

