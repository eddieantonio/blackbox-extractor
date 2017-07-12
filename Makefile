SCRIPTS = print-compile-input.py list-all-sessions.py blackbox_connection.py pairs-per-session.py section_9.py

upload: $(SCRIPTS)
	rsync -azvp $^ blackbox:~/tools/bin/

.PHONY: upload
