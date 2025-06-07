number = 14586
name = han
hslfile = $(number)_$(name).hsl
bs4 = beautifulsoup4-4.9.3

release/$(hslfile): config.xml src/*.py lib/bs4 lib/hanparse/base.py
	docker run --volume $(shell pwd):/hsl/projects/$(name) --workdir /hsl lindra/gira /usr/bin/python2 generator.pyc $(name)

interactive: lib/bs4
	docker run -it --volume $(shell pwd):/project -e PYTHONPATH=/project/lib --workdir /project lindra/gira /usr/bin/python2 

test: lib/bs4
	docker run -it --volume $(shell pwd):/project -e PYTHONPATH=/project/lib --workdir /project/lib/hanparse/test lindra/gira /usr/bin/python2 test.py

lib/bs4: lib/$(bs4).tar.gz
	tar xzvf $^ --directory=lib $(bs4)/bs4
	mv lib/$(bs4)/bs4 lib
	touch $@
	rmdir lib/$(bs4)

clean:
	rm -f release/$(hslfile)
