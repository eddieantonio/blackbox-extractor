# Blackbox utilities

Assume none of the following steps are safe to run in parallel.

verify-pairs.py
 ~ Creates and populates the **mistake** table.
 ~ Takes list of sfid, before id, after id from `stdin`
   and inserts it into the database

distance.py
 ~ Populates the **distance** table.
 ~ Calculates the Levenshtein distance of each pair.
 ~ Creates **distance** and **edit** table as a side-effect.

find\_edit.py
 ~ Populates the **edit** table.
 ~ Summarizes single-token syntax errors.
