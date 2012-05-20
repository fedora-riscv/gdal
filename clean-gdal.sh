# Volker Fröhlich
tar xvfz gdal-1.9.1RC2.tar.gz

mv gdal-1.9.1{,-fedora} && pushd gdal-1.9.1-fedora

rm data/cubewerx_extra.wkt
rm data/esri_extra.wkt
rm data/ecw_cs.wkt

#Muss man swig wirklich löschen?
rm -r swig/php
rm -r frmts/bsb

popd


#TODO: Provenance reinkopieren

tar cvfz gdal-1.9.1-fedora.tar.gz gdal-1.9.1-fedora
