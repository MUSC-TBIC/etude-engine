`build status <https://git.musc.edu/tbic/etude/commits/master>`__
`coverage report <https://git.musc.edu/tbic/etude/commits/master>`__

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

Dependencies
============

Python module requirements for running ETUDE are included in the
requirements.txt file. You should be able to install all non-default
packages using pip:

.. code:: bash

   pip install -r requirements

Testing
=======

Unit testing is done with the pytest module. Because of a bug in how
tests are processed in Python 2.7, you should run pytest indirectly
rather than directly:

.. code:: bash

   python -m pytest tests/

   ## You can also generate a coverate report in html format
   python -m pytest --cov-report html --cov=./ tests/

   ## The junit file is helpful for automated systems or CI pipelines
   python -m pytest --junitxml=junit.xml tests