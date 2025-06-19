# Install helpers

install-textblob:
	mkdir -p venv/share/nltk_data
	NLTK_DATA=venv/share/nltk_data ./venv/bin/python -m textblob.download_corpora lite

run-test:
	# venv/bin/python -m unittest -v test.test_fill_out_sentence_object
	venv/bin/python -m unittest -v test.test_pos
