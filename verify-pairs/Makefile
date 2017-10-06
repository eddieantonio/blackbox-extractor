DATABASE = java-mistakes.sqlite3

.PHONY: all
all:
	@echo No command selected
	@sed -ne '/^#;/s/...//p' Makefile | sort

#; distance - create distance table.
.PHONY: distance
distance:
	./distance.py

#; edit - populate edit table: prereq: distance.
.PHONY: distance
edit:
	./find_edit.py

#; rm-distance - remove all in distance table.
.PHONY: rm-distance
rm-distance: rm-edit
	sqlite3 $(DATABASE) 'DELETE FROM distance;'

#; rm-edit - remove all in edit table.
.PHONY: rm-edit
rm-edit:
	sqlite3 $(DATABASE) 'DELETE FROM edit;'

#; test - run tests
.PHONY: test
test:
	py.test --doctest-mod verify-pairs.py distance.py
