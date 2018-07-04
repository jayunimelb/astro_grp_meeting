update_webpage:
	python generate.py
	git add .
	git commit -m "increment `date +"%d/%m/%y"`"
	git subtree push --prefix build origin gh-pages
	open build/index.html
	git push origin `git subtree split --prefix build master`:gh-pages --force


.PHONY: auto increment select reselect confirm push
