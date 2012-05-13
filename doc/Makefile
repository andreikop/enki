OUT_DIR=$(PWD)/../../mksv3.gh-pages
IN_DIR=$(PWD)

check-dir:
	@if [ ! -d $(OUT_DIR) ]; then \
		echo Check out gh-pages branch of this project to $(OUT_DIR) directory; \
		exit 1; \
	fi

doc: check-dir
	cd $(OUT_DIR) && git reset --hard HEAD
	@if [ -d $(OUT_DIR)/api ]; then \
		cd $(OUT_DIR) && git rm -rf api; \
	fi

	sphinx-build $(IN_DIR) $(OUT_DIR)/api
	
	cd $(OUT_DIR)/api && mv _static static
	cd $(OUT_DIR)/api && mv _sources sources
	perl -pi -e "s/_sources/sources/g;" `find $(OUT_DIR)/api -name '*.html'`
	perl -pi -e "s/_static/static/g;" `find $(OUT_DIR)/api -name '*.html'`

push: doc
	cd $(OUT_DIR)/api && \
	git add -A  && \
	git rm --cached .buildinfo  && \
	git rm --cached -r .doctrees  && \
	git commit -m 'Plugin API update'  && \
	git push origin gh-pages
