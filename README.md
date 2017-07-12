Blackbox Extractor
==================

Tools related to extracting errors from Blackbox.


Broken invocation
-----------------

This invocation is broken:

    print-compile-input.py 1180 17873

Why? Because the compile event happened on June 11, 2013; but indexing started
on June 12, 2013

Dependencies
------------

    digraph {
        "list-all-sessions.py"
            -> Sessions
            -> "pairs-per-session.py"
            -> Pairs
            -> "verify-pairs.py"  // Must use print-compile-input.py
            -> Mistakes;
    }
