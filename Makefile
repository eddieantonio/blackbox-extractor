SCRIPTS = print-compile-input.py list-all-sessions.py

upload: $(SCRIPTS)
	rsync -avp $^ blackbox:~/tools/bin/

.PHONY: upload
