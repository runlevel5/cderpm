# Makefile to drive local builds of the cde RPM.
# Author:  David Cantrell <david.l.cantrell@gmail.com>

CWD := $(shell pwd)
RPMBUILD = rpmbuild --define='_topdir $(CWD)' \
                    --define='_sourcedir $(CWD)' \
                    --define='_specdir $(CWD)'
URL = https://www.burdell.org/cde/

NAME = $(shell grep Name: cde.spec | awk '{ print $$2; }')
VERSION = $(shell grep Version: cde.spec | awk '{ print $$2; }')
RELEASE = $(shell grep Release: cde.spec | awk '{ print $$2; }' | cut -d '%' -f 1)
ARCH = $(shell uname -m)

all: fetch build

# This could be improved from any of my other projects.
fetch:
	@while read checksum filename ; do \
		if [ -f ${CWD}/$${filename} ]; then \
			computed="$$(sha256sum $(CWD)/$${filename} | cut -d ' ' -f 1)" ; \
			if [ "$${computed}" = "$${checksum}" ]; then \
				echo "Already have $${filename} and it checks out." ; \
			else \
				curl -O $(URL)/$${filename} ; \
				computed="$$(sha256sum $(CWD)/$${filename} | cut -d ' ' -f 1)" ; \
				if [ ! "$${computed}" = "$${checksum}" ]; then \
					echo "*** INVALID CHECKSUM $${filename}" ; \
					exit 1 ; \
				fi ; \
			fi ; \
		else \
			curl -O $(URL)/$${filename} ; \
			computed="$$(sha256sum $(CWD)/$${filename} | cut -d ' ' -f 1)" ; \
			if [ ! "$${computed}" = "$${checksum}" ]; then \
				echo "*** INVALID CHECKSUM $${filename}" ; \
				exit 1 ; \
			fi ; \
		fi ; \
	done < $(CWD)/sources

# Local RPM building right here in this directory
build:
	$(RPMBUILD) -ba cde.spec
prep:
	$(RPMBUILD) -bp cde.spec

compile:
	$(RPMBUILD) -bb cde.spec

install:
	$(RPMBUILD) -bi cde.spec

srpm: fetch
	$(RPMBUILD) -bs -v cde.spec 2>&1 | tee rpmbuild.out
	srpm="$$(echo $$(basename $$(cut -d ' ' -f 2 < rpmbuild.out)))" ; \
	mv $(CWD)/SRPMS/$$srpm $(CWD)
	rm -f rpmbuild.out

# Release helpers
tag:
	git tag -s -m "Tag $(NAME)-$(VERSION)-$(RELEASE)" $(NAME)-$(VERSION)-$(RELEASE)

clog:
	@len=$$(($$(wc -l < cde.spec) - $$(sed -n '/%changelog/=' cde.spec))) ; \
	top=$$(tail -n $$len cde.spec | sed -n '/^$$/=' | head -n 1) ; \
	tail -n $$len cde.spec | head -n $$(($$top - 1)) > clog
	@cat clog

# Housekeeping
clean:
	-rm -rf BUILD BUILDROOT RPMS SRPMS clog

realclean: clean
	while read checksum filename ; do \
		[ -f "$$filename" ] && rm -f "$$filename" ; \
	done < $(CWD)/sources
