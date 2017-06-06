
Sample Runs
=========

A minimal run requires creating a matching dataset for the default configurations.
Process the I2B2 dev set using the DateTime tutorial provided with UIMA.
Then, because the output files for the I2B2 dev-annotations end in '.xml' but the UIMA tutorial files end in '.txt', you need to specify a file suffix translation rule.

```bash
export I2B2_CORPUS="/path/to/Corpora and annotations/2016 NGRID challenge (deid)/2016_track_1-deidentification"

export I2B2_OUTPUT="/tmp/datetime-out"
mkdir $I2B2_OUTPUT

$UIMA_HOME/bin/runAE.sh \
  $UIMA_HOME/examples/descriptors/tutorial/ex3/TutorialDateTime.xml \
  $I2B2_CORPUS/dev-text \
  $I2B2_OUTPUT

/usr/bin/python etude.py \
    $I2B2_CORPUS/dev-annotations \
    $I2B2_OUTPUT \
	--file-suffix ".xml" ".txt"

#########     TP        FP       TN       FN
aggregate        679.0  123.0     0.0    4821.0

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
