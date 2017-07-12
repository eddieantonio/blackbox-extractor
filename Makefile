SCRIPTS = print-compile-input.py list-all-sessions.py blackbox_connection.py pairs-per-session.py section_9.py

upload: $(SCRIPTS)
	rsync -avp $^ blackbox:~/tools/bin/

.PHONY: upload
