SCRIPTS = print-compile-input.py

upload: $(SCRIPTS)
	rsync $^ blackbox:~/tools/bin/

.PHONY: upload
