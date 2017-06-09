
Sample Runs
=========

Basic Run
--------

The simplest test run requires that we specify a gold directory and a
test directory.  The default file matching assumes that our gold and
test files match names exactly and both end in '.xml'.  With just the
two directory arguments, we get aggregate scores for the default
metrics across the full directory.  In the next sample run, you can
see how to include a per-file score breakdown and a
per-annotation-type score breakdown.

```bash
python etude.py \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_gold \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_test

python etude.py \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_gold \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
	--by-file \
	--by-type

```


Specifying Annotation Configs
--------------------------

We can use the same gold corpus to analyze annotations generated by
UIMA's DateTime tutorial (see link below). A minimal run requires
creating a matching dataset for the default configurations. Process
the I2B2 dev set using the DateTime tutorial provided with UIMA. Then,
because the output files for the I2B2 dev-annotations end in '.xml'
but the UIMA tutorial files end in '.txt', you need to specify a file
suffix translation rule. Also, the annotations are encoded slightly
differently by the tutorial descriptor than by the I2B2 gold.  As
such, you will need to load a different configuration for the test
directory to tell ETUDE how to find and extract the annotations.  (If
you run this example without the '--test-config' argument, you should
see all FN matches because nothing can be extracted from the test corpus.)

Link:  http://uima.apache.org/downloads/releaseDocs/2.2.2-incubating/docs/html/tutorials_and_users_guides/tutorials_and_users_guides.html#ugr.tug.aae.building_aggregates

```bash
export I2B2_CORPUS="/path/to/Corpora and annotations/2016 NGRID challenge (deid)/2016_track_1-deidentification"

export I2B2_OUTPUT="/tmp/datetime-out"
mkdir $I2B2_OUTPUT

$UIMA_HOME/bin/runAE.sh \
  $UIMA_HOME/examples/descriptors/tutorial/ex3/TutorialDateTime.xml \
  $I2B2_CORPUS/dev-text \
  $I2B2_OUTPUT

python etude.py \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_gold \
    $I2B2_OUTPUT \
	--by-type \
	--file-suffix ".xml" ".txt" \
	--test-config config/CAS_XMI.conf

#########	TP	FP	TN	FN
aggregate	19.0	20.0	0.0	426.0
Age	0.0	0.0	0.0	92.0
DateTime	19.0	20.0	0.0	105.0
HCUnit	0.0	0.0	0.0	76.0
OtherID	0.0	0.0	0.0	7.0
OtherLoc	0.0	0.0	0.0	5.0
OtherOrg	0.0	0.0	0.0	21.0
Patient	0.0	0.0	0.0	19.0
PhoneFax	0.0	0.0	0.0	6.0
Provider	0.0	0.0	0.0	64.0
StateCountry	0.0	0.0	0.0	21.0
StreetCity	0.0	0.0	0.0	4.0
Zip	0.0	0.0	0.0	4.0
eAddress	0.0	0.0	0.0	2.0

python etude.py \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_gold \
    $I2B2_OUTPUT \
	--file-suffix ".xml" ".txt"

#########	TP	FP	TN	FN
aggregate	0.0	0.0	0.0	445.0

```

Scoring on Different Fields
-----------------------

The above examples show scoring based on the default key in the
configuration file used for matching the gold to the test
configuration.  You may wish to group annotations on different fields,
such as the parent class or long description.

```bash
python etude.py \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_gold \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
	--by-type

python etude.py \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_gold \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
	--by-type \
	--score-key "Parent"

python etude.py \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_gold \
    $ETUDE_DIR/tests/data/i2b2_2016_track-1_test \
	--by-type \
	--score-key "Long Name"

```

Configuring Annotation Extraction
========================

Several sample configurations are provided in the config/ folder.
Each long name for an annotation description should be unique due to how Python's configuration parser works.
XPath's should also be unique within a config file but do not programmitically need to be.
The begin and end attribute are required for a pattern to be scorable.

```
[ Long Name or Description ]
Parent:           (optional; useful for merging multiple child types together for scoring)
Short Name:  (optional; useful for displaying as column output name and merging
                       multiple XPaths into a single scoring category)
XPath:            (required; pattern used by XPath to find annotation)
Begin Attr:     (required; beginning or start offset attribute name)
End Attr:       (required; end offset attribute name)
Text Attr:      (optional; not used by anything currently)
```

Dependencies
==========

Python module requirements for running ETUDE are included in the requirements.txt file.
You should be able to install all non-default packages using pip:

```bash
pip install -r requirements
```

Testing
=====

Unit testing is done with the pytest module.
Because of a bug in how tests are processed in Python 2.7, you should run pytest indirectly rather than directly:

```bash
python -m pytest tests
```
