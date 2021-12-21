#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Usage: $0 version"
	exit 1
fi

VERSION="$1"

wget https://github.com/OSGeo/gdal/releases/download/v$VERSION/gdal-$VERSION.tar.gz

tar xvf gdal-"${VERSION}".tar.gz

mv gdal-"${VERSION}"{,-fedora} && pushd gdal-"${VERSION}"-fedora

rm data/cubewerx_extra.wkt
rm data/esri_extra.wkt
rm data/esri_Wisconsin_extra.wkt
rm data/esri_StatePlane_extra.wkt
rm data/ecw_cs.wkt

#Really necessary?
rm -r swig/php

popd


#TODO: Insert Provenance file

tar cvfJ gdal-"${VERSION}"-fedora.tar.xz gdal-"${VERSION}"-fedora
