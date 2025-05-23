# Install helpers

install-textblob:
	mkdir -p venv/share/nltk_data
	NLTK_DATA=venv/share/nltk_data ./venv/bin/python -m textblob.download_corpora lite
