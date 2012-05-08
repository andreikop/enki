OUT_DIR=$(PWD)/../../mksv3.gh-pages/dev
IN_DIR=$(PWD)

check-dir:
	@if [ ! -d $(OUT_DIR) ]; then \
		echo Check out gh-pages branch of this project to $(OUT_DIR) directory; \
		exit 1; \
	fi

doc: check-dir
	cd $(OUT_DIR) && git reset --hard HEAD
	cd $(OUT_DIR) && git ls-files -z | xargs -0 git rm -rf
	cd $(OUT_DIR) && rm -rf *

	sphinx-build $(IN_DIR) $(OUT_DIR)
	cp -R $(IN_DIR)/screenshots $(OUT_DIR)
	mkdir -p $(OUT_DIR)/screenshots/preview
	cd $(IN_DIR)/screenshots && ls *.png | xargs -i convert -scale 16% {} $(OUT_DIR)/screenshots/preview/{}
	
	mv $(OUT_DIR)/_static $(OUT_DIR)/static
	mv $(OUT_DIR)/_sources $(OUT_DIR)/sources
	perl -pi -e "s/_sources/sources/g;" `find $(OUT_DIR) -name '*.html'`
	perl -pi -e "s/_static/static/g;" `find $(OUT_DIR) -name '*.html'`

push: doc
	cd $(OUT_DIR) && \
	git add -A  && \
	git rm --cached .buildinfo  && \
	git rm --cached -r .doctrees  && \
	git commit -m 'Documentation update'  && \
	git push origin gh-pages

