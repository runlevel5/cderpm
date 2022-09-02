#!/bin/bash

CWD=$(pwd)
rm -rf cdesktopenv-code
git clone git://git.code.sf.net/p/cdesktopenv/code cdesktopenv-code
cd cdesktopenv-code/cde
GITHASH="$(git log --pretty=format:'%h' -n 1)"
DATESTAMP="$(date +%Y%m%d)"
cd ${CWD}
VERSION="$(grep Version: cde.spec | awk '{ print $$2; }')"

if [[ $(git tag | grep "${VERSION}") ]]; then
  git checkout tags/$VERSION -b master
  OUTPUT="cde-${VERSION}.tar.gz"
else
  OUTPUT="cde-git-${GITHASH}.tar.gz"
fi

find cdesktopenv-code -type d -name .git | xargs rm -rf
mv cdesktopenv-code/cde/ cde-${VERSION}/
tar -czf ${OUTPUT} cde-${VERSION}/
rm -rf cde-${VERSION}/
sha1sum ${OUTPUT} > ${CWD}/sources
echo
echo "New source archived to ${OUTPUT}"
