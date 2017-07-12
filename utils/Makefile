SCRIPTS = $(wildcard *.py) list-sessions-naive

upload: $(SCRIPTS)
	rsync -azvp $^ blackbox:~/tools/bin/

.PHONY: upload
