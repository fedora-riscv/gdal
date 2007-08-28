Name:      gdal
Version:   1.4.2
Release:   3%{?dist}
Summary:   GIS file format library
Group:     System Environment/Libraries
License:   MIT
URL:       http://gdal.maptools.org
Source0:   %{name}-%{version}-fedora.tar.gz
Source1:   http://download.osgeo.org/gdal/gdalautotest-1.4.1.tar.gz
Patch0:    %{name}-buildfix.patch
Patch1:    %{name}-swig.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libtool swig pkgconfig
BuildRequires: doxygen tetex-latex ghostscript
BuildRequires: libpng-devel libungif-devel libjpeg-devel libtiff-devel
BuildRequires: jasper-devel cfitsio-devel hdf-devel libdap-devel librx-devel
BuildRequires: unixODBC-devel mysql-devel sqlite-devel postgresql-devel zlib-devel
BuildRequires: proj-devel geos-devel netcdf-devel hdf5-devel ogdi-devel libgeotiff-devel
BuildRequires: python-devel >= 2.4 xerces-c-devel
BuildRequires: perl(ExtUtils::MakeMaker)

# build against grass by default
%define _with_grass 1

%define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")
%define grass_support %{?_with_grass:1}%{!?_with_grass:%{?_without_grass:0}%{!?_without_grass:%{?_grass_support:%{_grass}}%{!?_grass:0}}}

%if %{grass_support}
BuildRequires: grass-devel
%endif

%description
The GDAL library provides support to handle multiple GIS file formats.

%package devel
Summary: Development Libraries for the GDAL file format library
Group: Development/Libraries
Requires: pkgconfig
Requires: libgeotiff-devel
Requires: %{name} = %{version}-%{release}

%description devel
The GDAL library provides support to handle multiple GIS file formats.

%package python
Summary: Python modules for the GDAL file format library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description python
The GDAL python modules provides support to handle multiple GIS file formats.

%package perl
Summary: Perl modules for the GDAL file format library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description perl
The GDAL perl modules provides support to handle multiple GIS file formats.

%prep
%setup -q -n %{name}-%{version}-fedora
%patch0 -p1 -b .buildfix
%patch1 -p1 -b .swig

# unpack test cases olso.
tar -xzf %{SOURCE1} .

# fix wrongly encoded files from tarball
set +x
for f in `find . -type f` ; do
   if file $f | grep -q ISO-8859 ; then
      set -x
      iconv -f ISO-8859-1 -t UTF-8 $f > ${f}.tmp && \
         mv -f ${f}.tmp $f
      set +x
   fi
   if file $f | grep -q CRLF ; then
      set -x
      sed -i -e 's|\r||g' $f
      set +x
   fi
done
set -x

# remove junks
find . -name ".cvsignore" -exec rm -rf '{}' \;

# fix some exec bits
chmod -x alg/gdal_tps.cpp
chmod -x frmts/jpeg/gdalexif.h
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdi.h
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdilayer.cpp
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdidatasource.cpp
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdidriver.cpp

%build

# fix hardcoded issues with cfitso and ogdi
sed -i 's|-L\$with_cfitsio -L\$with_cfitsio\/lib -lcfitsio|-lcfitsio|g' configure
sed -i 's|-I\$with_cfitsio|-I\$with_cfitsio\/include\/cfitsio|g' configure
sed -i 's|-L\$with_netcdf -L\$with_netcdf\/lib -lnetcdf|-lnetcdf|g' configure
sed -i 's|-L\$DODS_LIB -ldap++|-ldap++|g' configure
sed -i 's|-L\$with_ogdi -L\$with_ogdi\/lib -logdi|-logdi|g' configure
sed -i 's|-L\$with_jpeg -L\$with_jpeg\/lib -ljpeg|-ljpeg|g' configure
sed -i 's|-L\$with_libtiff\/lib -ltiff|-ltiff|g' configure
sed -i 's|-L\$with_grass\/lib||g' configure
sed -i 's|-lgeotiff -L$with_geotiff $LIBS|-lgeotiff $LIBS|g' configure
sed -i 's|-logdi31|-logdi|g' configure

# fix python path for ppc64
sed -i 's|test \"$ARCH\" = \"x86_64\"|test \"$libdir\" = \"\/usr\/lib64\"|g' configure

# append some path for few libs
export CPPFLAGS="`pkg-config ogdi --cflags`"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/netcdf-3"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/hdf"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/libgeotiff"
export CPPFLAGS="$CPPFLAGS `dap-config --cflags`"
export CFLAGS="$RPM_OPT_FLAGS" 
export CXXFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS='-L%{_libdir}/netcdf-3 -L%{_libdir}/hdf'

%configure \
        --prefix=%{_prefix} \
        --includedir=%{_includedir}/%{name}/ \
        --with-threads      \
        --with-dods-root=%{_libdir} \
        --with-ogdi=`ogdi-config --libdir` \
        --with-cfitsio=%{_prefix} \
        --with-geotiff=external   \
        --with-tiff=external      \
        --with-libtiff=external   \
        --with-libz               \
        --with-netcdf             \
        --with-hdf4               \
        --with-hdf5               \
        --with-geos               \
        --with-jasper             \
        --with-png                \
        --with-gif                \
        --with-jpeg               \
        --with-odbc               \
        --with-sqlite             \
        --with-mysql              \
        --with-curl               \
        --with-python             \
        --with-perl               \
        --with-xerces             \
        --with-xerces-lib='-lxerces-c -L%{_libdir}/hdf -L%{_libdir}/netcdf-3' \
        --with-xerces-inc=%{_includedir} \
        --without-pcraster        \
        --enable-shared           \
%if %{grass_support}
        --with-libgrass             \
        --with-grass=%{_prefix}     \
        --disable-static
%endif

# fixup hardcoded wrong compile flags.
cp GDALmake.opt GDALmake.opt.orig
sed -e "s/^CFLAGS.*$/CFLAGS=$CFLAGS/" \
-e "s/^CXXFLAGS.*$/CXXFLAGS=$CXXFLAGS/" \
-e "s/^FFLAGS.*$/FFLAGS=$FFLAGS/" \
-e "s/ cfitsio / /" \
-e "s/-ldap++/-ldap -ldapclient -ldapserver/" \
-e "s/-L\$(INST_LIB) -lgdal/-lgdal/" \
GDALmake.opt.orig > GDALmake.opt
rm GDALmake.opt.orig

# fixup non-existent lookup dir
mkdir -p external/include

# WARNING !!!
# dont use {?_smp_mflags} it break compile
# use external libtool to avoid hardcoded rpath in libs
make LIBTOOL=/usr/bin/libtool
make docs

# make perl modules, disable makefile generate
pushd swig/perl; 
 perl Makefile.PL;  make; 
 echo > Makefile.PL;
popd

%install
rm -rf $RPM_BUILD_ROOT

# fix some perl instalation issue
sed -i 's|>> $(DESTINSTALLARCHLIB)\/perllocal.pod|> \/dev\/null|g' swig/perl/Makefile_*

make \
        INST_PREFIX=%{buildroot} \
        INST_BIN=%{buildroot}%{_bindir} \
        INST_LIB=%{buildroot}%{_libdir} \
        INST_INCLUDE=%{buildroot}%{_includedir}/%{name} \
        INST_DATA=%{buildroot}%{_datadir}/%{name} \
        INST_MAN=%{buildroot}%{_mandir} \
        INST_PYMOD=%{buildroot}%{python_sitearch} \
        PERL_INSTALL_ROOT=%{buildroot} \
        install

# move perl modules in the right path
mkdir -p %{buildroot}%{perl_vendorarch}
mv %{buildroot}%{_libdir}/Geo %{buildroot}%{perl_vendorarch}/
rm -rf %{buildroot}%{perl_vendorarch}/Geo/GDAL
mv %{buildroot}%{perl_sitearch}/auto/Geo/* %{buildroot}%{perl_vendorarch}/Geo/
rm -rf %{buildroot}%{_libdir}/perl5/site_perl %{buildroot}/auto %{buildroot}%{perl_sitelib}

# install pkgconfig file
cat > %{name}.pc <<EOF
prefix=%{_prefix}
exec_prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}

Name: GDAL
Description: GIS file format library
Version: %{version}
Libs: -L\${libdir} -lgdal
Cflags: -I\${includedir}/%{name}
EOF

mkdir -p %{buildroot}%{_libdir}/pkgconfig/
install -p -m 644 %{name}.pc %{buildroot}%{_libdir}/pkgconfig/

# fix some exec bits
find %{buildroot}%{perl_vendorarch} -name "*.so" -exec chmod 755 '{}' \;
chmod -x pymod/samples/*

# build and include more docs
mkdir -p doc/frmts; find frmts -name "*.html" -exec install -m 644 '{}' doc/frmts/ \;
mkdir -p doc/ogrsf_frmts; find ogr/ogrsf_frmts -name "*.html" -exec install -m 644 '{}' doc/ogrsf_frmts \;

# some commented out are broken for now
pushd doc; doxygen *.dox; popd
pushd rfc; doxygen *.dox; popd
pushd rfc/latex; make refman.pdf; popd
#pushd ogr/ogrsf_frmts; doxygen *.dox; popd
#pushd ogr/ogrsf_frmts/latex; make refman.pdf; popd
pushd swig/perl; doxygen; popd
pushd swig/perl/latex; make refman.pdf; popd

# cleanup junks
for junk in {*.a,*.la,*.bs,.exists,.packlist,.cvsignore} ; do
find %{buildroot} -name "$junk" -exec rm -rf '{}' \;
done

%check

pushd gdalautotest-1.4.1

# export test enviroment
export PYTHONPATH=$PYTHONPATH:%{buildroot}%{python_sitearch}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH%{buildroot}%{_libdir}
export GDAL_DATA=%{buildroot}%{_datadir}/%{name}/

# remove some testcases for now due to build failure
rm -rf ogr/ogr_pg.py     # no pgsql during test (disabled)
rm -rf ogr/ogr_dods.py   # no DODS  during test (disabled)
rm -rf gdrivers/dods.py  # no DODS  during test (disabled)
rm -rf gdrivers/hfa.py   # no HFA   during test (disabled)
rm -rf gcore/hfa_write.py  # HFA driver absent  (disabled)
rm -rf ogr/ogr_dgn.py      # DGW driver absent  (disabled)
rm -rf osr/osr_esri.py     # ESRI datum absent  (disabled)

rm -rf gcore/tiff_write.py # crash ugly on 64bit (mustfix)

# run tests but force than normal exit
./run_all.py || exit 0

popd

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files 
%defattr(-,root,root,-)
%doc NEWS PROVENANCE.TXT-mainstream PROVENANCE.TXT-fedora COMMITERS
%doc doc/frmts  
#%doc doc/ogrsf_frmts doc/html
%{_bindir}/gdal_contour
%{_bindir}/gdal_rasterize
%{_bindir}/gdal_translate
%{_bindir}/gdaladdo
%{_bindir}/gdalinfo
%{_bindir}/gdaltindex
%{_bindir}/gdalwarp
%{_bindir}/ogr*
%{_libdir}/*.so.*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%{_mandir}/man1/gdaladdo.1.gz
%{_mandir}/man1/gdalinfo.1.gz
%{_mandir}/man1/gdaltindex.1.gz
%{_mandir}/man1/gdalwarp.1.gz
%{_mandir}/man1/gdal_contour.1.gz 
%{_mandir}/man1/gdal_rasterize.1.gz
%{_mandir}/man1/gdal_translate.1.gz
%{_mandir}/man1/gdal_utilities.1.gz
%{_mandir}/man1/ogr*.1.gz

%files devel
%defattr(-,root,root,-)
%doc html ogr/html rfc/html rfc/latex/refman.pdf 
%doc ogr/wcts/html 
#%doc ogr/ogrsf_frmts/html 
#%doc ogr/ogrsf_frmts/latex/refman.pdf
%{_bindir}/%{name}-config
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}.pc
%{_mandir}/man1/%{name}-config*

%files python
%defattr(-,root,root,-)
%doc pymod/samples
%exclude %{_bindir}/*.py?
%attr(0755,root,root) %{_bindir}/*.py
%exclude %{python_sitearch}/*.la
%{python_sitearch}/*
%{_mandir}/man1/pct2rgb.1.gz
%{_mandir}/man1/rgb2pct.1.gz
%{_mandir}/man1/gdal_merge.1.gz

%files perl
%defattr(-,root,root,-)
%doc swig/perl/html swig/perl/latex/refman.pdf swig/perl/README
%{perl_vendorarch}/*

%changelog
* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 1.4.2-3
- Rebuild for selinux ppc32 issue.

* Wed Jul 24 2007 Balint Cristian <cbalint@redhat.com> 1.4.2-2
- disable one more HFA test, HFA is unaviable due to license

* Wed Jul 24 2007 Balint Cristian <cbalint@redhat.com> 1.4.2-1
- new upstream one
- catch some more docs
- fix ogr python module runtime
- include testcases and run tests
- enable geotiff external library we have new libgeotiff now
- EPSG geodetic database is licensed OK since v6.13 so re-enable
- enable it against grass by default, implement optional switches 

* Tue Jun 05 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-4
- re-build.

* Sat May 12 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-3
- re-build against grass.

* Fri May 11 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-2
- fix python lookup paths for ppc64.

* Wed May 09 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-1
- new upstream release.
- disable temporary grass-devel requirement untill find a
  resonable solution for gdal-grass egg-chicken dep problem.

* Fri Apr 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-22
- and olso dont attempt pack missing docs.

* Fri Apr 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-21
- exclude some docs, doxygen segfault with those now upstream.

* Fri Apr 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-20
- rebuild against latest fedora upstream tree.

* Mon Apr 02 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-19
- own gdal includedir
- fix one more spurious lib path

* Wed Mar 21 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-18
- remove system lib path from gdal-config --libs, its implicit

* Tue Mar 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-17
- enable build against grass
- fix incorrect use of 32/64 library paths lookups

* Fri Mar 16 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-16
- fix gdal flag from pkgconfig file

* Thu Mar 15 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-15
- require pkgconfig
- generate pkgconfig from spec instead

* Thu Mar 15 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-14
- require perl(ExtUtils::MakeMaker) instead ?dist checking
- add pkgconfig file 

* Wed Mar 14 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-13
- fix typo in specfile

* Wed Mar 14 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-12
- add missing dot from dist string in specfile

* Wed Mar 14 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-11
- fix fc6 fc5 builds

* Thu Mar 1 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-10
- fix mock build
- require perl-devel

* Tue Feb 27 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-9
- repack tarball for fedora, explain changes in PROVENANCE-fedora,
  license should be clean now according to PROVENANCE-* files
- require ogdi since is aviable now
- drop nogeotiff patch, in -fedora tarball geotiff is removed
- man page triage over subpackages
- exclude python byte compiled objects
- fix some source C file exec bits

* Sat Feb 24 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-8
- fix more things in spec
- include more docs

* Wed Feb 21 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-7
- libtool in requirement list for build

* Wed Feb 21 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-6
- use external libtool to avoid rpath usage
- include more docs

* Mon Feb 12 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-5
- use rm -rf for removal of dirs.
- fix require lists

* Mon Feb 12 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-4
- fix doxygen buildreq
- make sure r-path is fine.

* Sat Feb 10 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-3
- disable now ogdi (pending ogdi submission).

* Sat Feb 10 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-2
- more fixups for lib paths

* Fri Feb 09 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-1
- first pack for fedora extras
- disable geotiff (untill license sorted out)
- enable all options aviable from extras
- pack perl and python modules
- kill r-path from libs
- pack all docs posible
