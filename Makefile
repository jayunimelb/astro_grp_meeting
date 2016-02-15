manual:
	python available.py
	python make_selection.py
	python generate.py
	open build/index.html

auto:
	python increment.py
	python available.py
	python make_selection.py
	python generate.py
	open build/index.html

push:
	git add .
	git commit -m "increment `date +"%d/%m/%y"`"
	git subtree push --prefix build origin gh-pages
	# git push origin `git subtree split --prefix build master`:gh-pages --force

.PHONY: manual auto push
