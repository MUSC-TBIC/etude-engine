Evaluating Matches
==================

Relevant command line arguments:

.. sourcecode:: bash

   --fuzzy-match-flags exact
   --fuzzy-match-flags partial
   --fuzzy-match-flags fully-contained
   --fuzzy-match-flags exact partial fully-contained

   --fuzzy-match-flags [start|end|doc-property]

   --ignore-whitespace
   --skip-chars [regex of characters to skip]

   --heed-whitespace


Exact Match
-----------

`--fuzzy-match-flags exact`

`--fuzzy-match-flags exact partial fully-contained`

Partial Match
-------------

`--fuzzy-match-flags partial`


Fully-Contained Match
---------------------

`--fuzzy-match-flags fully-contained`


Start Match
-----------

`--fuzzy-match-flags start`


End Match
---------

`--fuzzy-match-flags end`


Doc-Property Match
------------------

(In Development)

`--fuzzy-match-flags doc-property`
