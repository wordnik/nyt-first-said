BROWSERIFY = ./node_modules/.bin/browserify
UGLIFY = ./node_modules/uglify-es/bin/uglifyjs

pushall: sync
	git push origin master

build:
	$(BROWSERIFY) app.js > index.js

run: build
	python -m http.server

prettier:
	prettier --single-quote --write "**/*.js"
