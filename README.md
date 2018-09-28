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


License
-------

Copyright © 2017–2018 Eddie Antonio Santos.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
