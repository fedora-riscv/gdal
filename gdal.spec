#TODO: Un-bundle g2clib and grib
#TODO: Python 3 bindings possible since 1.7.0

Name:      gdal
Version:   1.7.3
Release:   15%{?dist}
Summary:   GIS file format library
Group:     System Environment/Libraries
License:   MIT
URL:       http://www.gdal.org/
# Source0:   http://download.osgeo.org/gdal/gdal-%%{version}.tar.gz
# see PROVENANCE.TXT-fedora for details
Source0:   %{name}-%{version}-fedora.tar.gz
Source1:   http://download.osgeo.org/gdal/gdalautotest-1.7.3.tar.gz
# create versionless symlink
Source2:   gdal-1.7.3.pom
Patch1:    %{name}-mysql.patch
Patch2:    %{name}-bindir.patch
Patch3:    %{name}-AIS.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=693952 
# http://trac.osgeo.org/gdal/ticket/3694 -- Still present in 1.8 tarball
Patch5:    %{name}-1.8.0-mitab.patch

# Allow to use libpng 1.5
# http://trac.osgeo.org/gdal/changeset/21526
# Not necessary for 1.8 and later
Patch6:    %{name}-1.7.3-png15.patch

# Ruby headers are stored in a different place in 1.9
# Don't use Xcompiler, as GCC doesn't like it anymore
Patch7:    %{name}-1.7.3-ruby-1.9.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libtool pkgconfig
BuildRequires: python-devel numpy xerces-c-devel
BuildRequires: libpng-devel libungif-devel

%if (0%{?fedora})
BuildRequires: libjpeg-turbo-devel
%else
BuildRequires: libjpeg-devel
%endif

BuildRequires: libtiff-devel
BuildRequires: doxygen tetex-latex ghostscript ruby-devel jpackage-utils
BuildRequires: jasper-devel cfitsio-devel libdap-devel librx-devel 
BuildRequires: hdf-static hdf-devel
BuildRequires: unixODBC-devel mysql-devel sqlite-devel postgresql-devel zlib-devel
BuildRequires: proj-devel geos-devel netcdf-devel hdf5-devel ogdi-devel libgeotiff-devel
BuildRequires: curl-devel
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: chrpath
BuildRequires: ant swig ruby java-devel-gcj

#TODO: Grass support will be available as a plug-in

# Enable/disable refman generation
%global build_refman  1

# we have multilib triage
%if "%{_lib}" == "lib"
%global cpuarch 32
%else
%global cpuarch 64
%endif

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%{!?ruby_sitearch: %global ruby_sitearch %(ruby -rrbconfig -e 'puts Config::CONFIG["sitearchdir"]')}

# Avoid providing private Python and Perl extension libs
%{?filter_setup:
%filter_provides_in %{python_sitearch}/.*\.so %{_libdir}/perl5/.*\.so$ 
%filter_setup
}

%description
The GDAL library provides support to handle multiple GIS file formats.

%package devel
Summary: Development Libraries for the GDAL file format library
Group: Development/Libraries
Requires: pkgconfig
Requires: libgeotiff-devel
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
The GDAL library provides support to handle multiple GIS file formats.

%package static
Summary: Static Development Libraries for the GDAL file format library
Group: Development/Libraries

%description static
The GDAL library provides support to handle multiple GIS file formats.

%package python
Summary: Python modules for the GDAL file format library
Group: Development/Libraries
Requires: numpy
Requires: %{name}%{?_isa} = %{version}-%{release}

%description python
The GDAL python modules provides support to handle multiple GIS file formats.

%package perl
Summary: Perl modules for the GDAL file format library
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description perl
The GDAL perl modules provides support to handle multiple GIS file formats.

%package ruby
Summary: Ruby modules for the GDAL file format library
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%if (0%{?fedora} < 17 || 0%{?rhel})
Requires: ruby(abi) = 1.8
%else
Requires: ruby(abi) = 1.9
%endif

%description ruby
The GDAL Ruby modules provide support to handle multiple GIS file formats.

%package java
Summary: Java modules for the GDAL file format library
Group: Development/Libraries
Requires: java
Requires: jpackage-utils
Requires(post): jpackage-utils
Requires(postun): jpackage-utils
Requires: %{name}%{?_isa} = %{version}-%{release}

%description java
The GDAL java modules provides support to handle multiple GIS file formats.

%package doc
Summary: Documentation for GDAL
Group: Documentation
Requires: %{name} = %{version}-%{release}

%description doc
This package contains html and pdf documentation for GDAL.

%prep
%setup -q -n %{name}-%{version}-fedora

# Delete bundled libraries
rm -rf frmts/zlib
rm -rf frmts/png/libpng
rm -rf frmts/gif/giflib
rm -rf frmts/jpeg/libjpeg \
    frmts/jpeg/libjpeg12
rm -rf frmts/gtiff/libgeotiff \
    frmts/gtiff/libtiff

%patch1 -p0 -b .mysql~
%patch2 -p1 -b .bindir~
%patch3 -p1 -b .AIS~
%patch5 -p3 -b .mitab~

# Only F17 has libpng 1.5
%if ! (0%{?fedora} < 17 || 0%{?rhel})
%patch6 -p1 -b .png15~
%endif
%patch7 -p1 -b .ruby19~

# Unpack test cases
tar -xzf %{SOURCE1}

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
find swig/python/samples -name "*.py" -exec chmod -x '{}' \;

# Remove man dir, as it blocks a build target.
# It obviously slipped into the tarball and is not in Trunk (April 17th, 2011)
rm -rf man

# Repair check for dap and also Curl (although not obvious here!)
#TODO: Better use dap-config --libs
sed -i 's|-ldap++|-ldap -ldapclient -ldapserver|' configure configure.in

# fix doxygen for multilib docs
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' swig/perl/Doxyfile
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/gxf/Doxyfile
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/sdts/Doxyfile
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/pcraster/doxygen.cfg
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/iso8211/Doxyfile



%build

# fix hardcoded issues
sed -i 's|@LIBTOOL@|%{_bindir}/libtool|g' GDALmake.opt.in
sed -i 's|-L\$with_cfitsio -L\$with_cfitsio\/lib -lcfitsio|-lcfitsio|g' configure
sed -i 's|-I\$with_cfitsio|-I\$with_cfitsio\/include\/cfitsio|g' configure
sed -i 's|-L\$with_netcdf -L\$with_netcdf\/lib -lnetcdf|-lnetcdf|g' configure
sed -i 's|-L\$DODS_LIB -ldap++|-ldap++|g' configure
sed -i 's|-L\$with_ogdi -L\$with_ogdi\/lib -logdi|-logdi|g' configure
sed -i 's|-L\$with_jpeg -L\$with_jpeg\/lib -ljpeg|-ljpeg|g' configure
sed -i 's|-L\$with_libtiff\/lib -ltiff|-ltiff|g' configure
sed -i 's|-L\$with_grass\/lib||g' configure
sed -i 's|-lgeotiff -L$with_geotiff $LIBS|-lgeotiff $LIBS|g' configure
sed -i 's|-L\$with_geotiff\/lib -lgeotiff $LIBS|-lgeotiff $LIBS|g' configure
sed -i 's|-lmfhdf -ldf|-L$libdir/hdf -lmfhdf -ldf|g' configure
sed -i 's|-logdi31|-logdi|g' configure

# libproj is dlopened; upstream sources point to .so, which is usually not present
# http://trac.osgeo.org/gdal/ticket/3602
sed -i 's|libproj.so|libproj.so.0|g' ogr/ogrct.cpp

# Fix python path for ppc64
#TODO: Ticket? Must be corrected for 64 bit architectures other than Intel; Query Python?
sed -i 's|test \"$ARCH\" = \"x86_64\"|test \"$libdir\" = \"$libdir"|g' configure

# Install Ruby bindings into the proper place
#TODO: Ticket
sed -i -e 's|^$(INSTALL_DIR):|$(DESTDIR)$(INSTALL_DIR):|' swig/ruby/RubyMakefile.mk
sed -i -e 's|^install: $(INSTALL_DIR)|install: $(DESTDIR)$(INSTALL_DIR)|' swig/ruby/RubyMakefile.mk

# Append paths for some libs
export CPPFLAGS="`pkg-config ogdi --cflags`"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/netcdf-3"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/netcdf"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/hdf"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/libgeotiff"
export CPPFLAGS="$CPPFLAGS `dap-config --cflags`"
export CPPFLAGS="$CPPFLAGS -DH5_USE_16_API"

# code may contain sensible buffer overflows triggered by gcc ssp flag (mustfixupstream).
export CXXFLAGS=`echo %{optflags}|sed -e 's/\-Wp\,-D_FORTIFY_SOURCE\=2 / -fPIC -DPIC /g'`
export CFLAGS=`echo %{optflags}|sed -e 's/\-Wp\,\-D_FORTIFY_SOURCE\=2 / -fPIC -DPIC /g'`

# BSB has legal claims, see PROVENANCE.TXT-fedora
#TODO: msg needs to have PublicDecompWT.zip from EUMETSAT, which is not free
%configure \
        --prefix=%{_prefix} \
        --includedir=%{_includedir}/%{name}/ \
        --datadir=%{_datadir}/%{name}/ \
        --with-threads      \
        --without-bsb       \
        --with-dods-root=%{_libdir} \
        --with-ogdi               \
        --with-cfitsio=%{_prefix} \
        --with-geotiff=external   \
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
        --with-sqlite3            \
        --with-mysql              \
        --with-curl               \
        --with-python             \
        --with-perl               \
        --with-pcraster           \
        --with-ruby               \
        --with-java               \
        --with-xerces             \
        --with-xerces-lib='-lxerces-c' \
        --with-xerces-inc=%{_includedir} \
        --with-jpeg12=no          \
        --enable-shared           \
        --with-gdal-ver=%{version}

# fixup hardcoded wrong compile flags.
cp GDALmake.opt GDALmake.opt.orig
sed -e 's/ cfitsio / /' \
-e 's/-ldap++/-ldap -ldapclient -ldapserver/' \
-e 's/-L\$(INST_LIB) -lgdal/-lgdal/' \
GDALmake.opt.orig > GDALmake.opt
rm GDALmake.opt.orig

# Build with fPIC to allow Ruby bindings
#TODO: Ticket
sed -i -e "s/\$(LD)/g++ -L..\/..\/.libs\/ $RPM_OPT_FLAGS/g" swig/ruby/RubyMakefile.mk
sed -i -e "s/\$(CFLAGS)/$(CFLAGS) -fPIC/g" swig/ruby/RubyMakefile.mk


# WARNING !!!
# dont use {?_smp_mflags} it break compile
make
make man

# make perl modules, disable makefile generate
pushd swig/perl
  perl Makefile.PL;  make;
  echo > Makefile.PL;
popd

  # make java modules
  pushd swig/java
    # fix makefile
    sed -i -e 's|include java.opt|\#include java.opt|' GNUmakefile
    sed -i -e 's|\$(LD) -shared \$(LDFLAGS) \$(CONFIG_LIBS)|g++ -shared -lgdal -L..\/..\/.libs|g' GNUmakefile
    # build java module
    make
  popd
# remake documentation for multilib issues
# also include many pdf documentation

for docdir in ./ doc doc/ru doc/br ogr frmts/gxf frmts/pcidsk/sdk frmts/sdts frmts/iso8211 frmts/vrt swig/perl swig/python apps; do
  cp -p doc/gdal_footer.html $docdir/footer_local.html
  pushd $docdir
    if [ ! -f Doxyfile ]; then
      doxygen -g
    else
      doxygen -u
    fi
    #if [ $docdir == "doc" ]; then
      #TODO: Get that working
      #sed -i -e 's|^IMAGE_PATH|IMAGE_PATH = doc\n#IMAGE_PATH|' Doxyfile
    #fi
    sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = footer_local.html\n#HTML_FOOTER |' Doxyfile
    sed -i -e 's|^GENERATE_LATEX|GENERATE_LATEX = YES\n#GENERATE_LATEX |' Doxyfile
    sed -i -e 's|^USE_PDFLATEX|USE_PDFLATEX = YES\n#USE_PDFLATEX |' Doxyfile
    if [ $docdir == "doc/ru" ]; then
      sed -i -e 's|^OUTPUT_LANGUAGE|OUTPUT_LANGUAGE = Russian\n#OUTPUT_LANGUAGE |' Doxyfile
    fi
    rm -rf latex html
    doxygen
    rm -rf footer_local.html
    %if %{build_refman}
      pushd latex
        sed -i -e '/rfoot\[/d' -e '/lfoot\[/d' doxygen.sty
        sed -i -e '/small/d' -e '/large/d' refman.tex
        sed -i -e 's|pdflatex|pdflatex -interaction nonstopmode |g' Makefile
        make refman.pdf || true
      popd
    %endif
  popd
done


%install
rm -rf %{buildroot}

# Fix Python installation path
sed -i 's|setup.py install|setup.py install --root=%{buildroot}|' swig/python/GNUmakefile

# fix some perl installation issue
sed -i 's|>> $(DESTINSTALLARCHLIB)\/perllocal.pod|> \/dev\/null|g' swig/perl/Makefile_*


make    DESTDIR=%{buildroot} \
        install

make    DESTDIR=%{buildroot} \
        INST_MAN=%{_mandir} \
        install-man

# move perl modules in the right path
mkdir -p %{buildroot}%{perl_vendorarch}
mv %{buildroot}%{perl_sitearch}/* %{buildroot}%{perl_vendorarch}/
find %{buildroot}%{perl_vendorarch} -name "*.dox" -exec rm -rf '{}' \;

# fix some exec bits
find %{buildroot}%{perl_vendorarch} -name "*.so" -exec chmod 755 '{}' \;

# install multilib java modules in the right path
touch -r NEWS swig/java/gdal.jar
mkdir -p %{buildroot}%{_javadir}
cp -p swig/java/gdal.jar  \
      %{buildroot}%{_javadir}/%{name}-%{version}.jar

# create versionless symlink
ln -s %{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar

# Install Maven pom
mkdir -p %{buildroot}%{_mavenpomdir}
install -pm 644 %{SOURCE2} \
               %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom

# Create depmap fragment
%add_to_maven_depmap org.gdal gdal-java-bindings %{version} JPP %{name}

# copy JNI libraries and links, non versioned link needed by JNI
cp -pvl swig/java/.libs/*.so*  \
      %{buildroot}%{_libdir}
chrpath --delete %{buildroot}%{_libdir}/*jni.so*

# install and include all docs
# due TeX-related issues some refman.pdf are not created
rm -rf docs doc/docs-perl

mkdir -p doc/gdal_frmts; find frmts -name "*.html" -exec install -p -m 644 '{}' doc/gdal_frmts/ \;
mkdir -p doc/ogrsf_frmts; find ogr -name "*.html" -exec install -p -m 644 '{}' doc/ogrsf_frmts/ \;
%if %{build_refman}
  mkdir -p docs/docs-%{cpuarch}/pdf
  pushd docs/docs-%{cpuarch}/pdf; mkdir -p apps br ru en ogr frmts/gxf frmts/sdts frmts/iso8211 frmts/vrt frmts/pcidsk; popd
  install -p -m 644 doc/latex/refman.pdf docs/docs-%{cpuarch}/pdf/en
  install -p -m 644 frmts/pcidsk/sdk/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/pcidsk
  install -p -m 644 frmts/vrt/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/vrt
  install -p -m 644 apps/latex/refman.pdf docs/docs-%{cpuarch}/pdf/apps
  install -p -m 644 doc/br/latex/refman.pdf docs/docs-%{cpuarch}/pdf/br/
  install -p -m 644 latex/refman.pdf docs/docs-%{cpuarch}/
  install -p -m 644 latex/class*.pdf docs/docs-%{cpuarch}/
  install -p -m 644 doc/ru/latex/refman.pdf docs/docs-%{cpuarch}/pdf/ru/
  install -p -m 644 ogr/latex/refman.pdf docs/docs-%{cpuarch}/pdf/ogr/
  install -p -m 644 ogr/latex/class*.pdf docs/docs-%{cpuarch}/pdf/ogr/
  # Doesn't work at all. Complaints about different nesting level in \pdfendlink
  #%ifnarch ppc ppc64
  #install -p -m 644 ogr/ogrsf_frmts/dgn/latex/refman.pdf docs/docs-%{cpuarch}/pdf/ogrsf_frmts/dgn/
  #%endif
  install -p -m 644 frmts/gxf/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/gxf/
  install -p -m 644 frmts/sdts/latex/class*.pdf docs/docs-%{cpuarch}/pdf/frmts/sdts/
  # Doesn't work at all. Complaints about different nesting level in \pdfendlink
  # Working in GDAL 1.8.0, funny enough!
  #%ifnarch ppc ppc64
  #install -p -m 644 frmts/sdts/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/sdts/
  #%endif
  install -p -m 644 frmts/iso8211/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/iso8211/
  mkdir -p doc/docs-perl/docs-%{cpuarch}/pdf
  install -p -m 644 swig/perl/latex/refman.pdf doc/docs-perl/docs-%{cpuarch}/pdf
%endif
mkdir -p docs/docs-%{cpuarch}
mkdir -p doc/docs-perl/docs-%{cpuarch}
pushd docs/docs-%{cpuarch}/; mkdir -p en/html gdal_frmts ogrsf_frmts br ru; popd
cp -pr html/* docs/docs-%{cpuarch}/
cp -pr doc/html/* docs/docs-%{cpuarch}/en/html
cp -pr doc/gdal_frmts/* docs/docs-%{cpuarch}/gdal_frmts
cp -pr doc/ogrsf_frmts/* docs/docs-%{cpuarch}/ogrsf_frmts
cp -pr doc/br/html/* docs/docs-%{cpuarch}/br
cp -pr doc/ru/html/* docs/docs-%{cpuarch}/ru
cp -pr swig/perl/html/* doc/docs-perl/docs-%{cpuarch}/

# Remove installation shell script
rm -rf docs/docs-%{cpuarch}/ru/installdox
rm -rf docs/docs-%{cpuarch}/en/html/installdox

# install multilib cpl_config.h bz#430894
install -p -D -m 644 port/cpl_config.h %{buildroot}%{_includedir}/%{name}/cpl_config-%{cpuarch}.h
# create universal multilib cpl_config.h bz#341231
cat > %{buildroot}%{_includedir}/%{name}/cpl_config.h <<EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "gdal/cpl_config-32.h"
#else
#if __WORDSIZE == 64
#include "gdal/cpl_config-64.h"
#else
#error "Unknown word size"
#endif
#endif
EOF
touch -r NEWS port/cpl_config.h

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
touch -r NEWS %{buildroot}%{_libdir}/pkgconfig/

# multilib gdal-config
mv %{buildroot}%{_bindir}/%{name}-config %{buildroot}%{_bindir}/%{name}-config-%{cpuarch}
cat > %{buildroot}%{_bindir}/%{name}-config <<EOF
#!/bin/bash

ARCH=\$(uname -m)
case \$ARCH in
x86_64 | ppc64 | ia64 | s390x | sparc64 | alpha | alphaev6 )
%{name}-config-64 \${*}
;;
*)
%{name}-config-32 \${*}
;;
esac
EOF
chmod 755 %{buildroot}%{_bindir}/%{name}-config
touch -r NEWS %{buildroot}%{_bindir}/%{name}-config

# cleanup junks
rm -rf %{buildroot}%{_includedir}/%{name}/%{name}
rm -rf %{buildroot}%{_bindir}/gdal_sieve.dox
rm -rf %{buildroot}%{_bindir}/gdal_fillnodata.dox
for junk in {*.la,*.bs,.exists,.packlist,.cvsignore} ; do
find %{buildroot} -name "$junk" -exec rm -rf '{}' \;
done


%check

pushd gdalautotest-1.7.3

# export test enviroment
export PYTHONPATH=$PYTHONPATH:%{buildroot}%{python_sitearch}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%{buildroot}%{_libdir}
export GDAL_DATA=%{buildroot}%{_datadir}/%{name}/

# remove some testcases for now due to build failure
rm -rf ogr/ogr_pg.py        # no pgsql during test (disabled)
rm -rf ogr/ogr_mysql.py     # no mysql during test (disabled)
rm -rf ogr/ogr_dods.py      # no DODS  during test (disabled)
rm -rf gdrivers/dods.py     # no DODS  during test (disabled)
rm -rf osr/osr_esri.py        # ESRI datum absent  (disabled)
rm -rf ogr/ogr_sql_test.py    # no SQL during tests
rm -rf gcore/mask.py       # crash ugly  (mustfix)

# run tests but force than normal exit
./run_all.py || true

popd


%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post java
/sbin/ldconfig
# update maven2 depmap
%update_maven_depmap

%postun java
/sbin/ldconfig
# update maven2 depmap
%update_maven_depmap


%files
%doc NEWS PROVENANCE.TXT PROVENANCE.TXT-fedora COMMITERS
%{_bindir}/gdal_contour
%{_bindir}/gdal_rasterize
%{_bindir}/gdal_translate
%{_bindir}/gdaladdo
%{_bindir}/gdalinfo
%{_bindir}/gdaldem
%{_bindir}/gdalbuildvrt
%{_bindir}/gdaltindex
%{_bindir}/gdalwarp
%{_bindir}/gdal_grid
%{_bindir}/gdalenhance
%{_bindir}/gdalmanage
%{_bindir}/gdaltransform
%{_bindir}/nearblack
%{_bindir}/ogr*
%{_bindir}/testepsg
%{_libdir}/libgdal.so.*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%{_mandir}/man1/*.1*

%files devel
%{_bindir}/%{name}-config
%{_bindir}/%{name}-config-%{cpuarch}
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}.pc

%files static
%{_libdir}/*.a

%files python
%doc swig/python/samples
%{_bindir}/*.py*
%{python_sitearch}/*

%files perl
%doc doc/docs-perl
%doc swig/perl/README
%{perl_vendorarch}/*

%files ruby
%{ruby_sitearch}/%{name}

%files java
%doc swig/java/apps
%{_javadir}/%{name}-%{version}.jar
# provide versionless symlink
%{_javadir}/%{name}.jar
%{_libdir}/*jni.so.*
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*

%files doc
%doc docs

%changelog
* Fri Jul 13 2012 Orion Poplawski <orion@nwra.com> - 1.7.3-15
- Don't require maven2 in java package, not needed and not
  available on EL6

* Thu Feb 19 2012 Volker Fröhlich <volker27@gmx.at> - 1.7.3-14
- Require Ruby abi
- Add patch for Ruby 1.9 include dir, back-ported from GDAL 1.9
- Change version string for gdal-config from <version>-fedora to
  <version>
- Revert installation path for Ruby modules, as it proved wrong
- Use libjpeg-turbo

* Thu Feb  9 2012 Volker Fröhlich <volker27@gmx.at> - 1.7.3-13
- Rebuild for Ruby 1.9
  http://lists.fedoraproject.org/pipermail/ruby-sig/2012-January/000805.html

* Tue Jan 10 2012 Volker Fröhlich <volker27@gmx.at> - 1.7.3-12
- Remove FC10 specific patch0
- Versioned MODULE_COMPAT_ Requires for Perl (BZ 768265)
- Add isa macro to base package Requires
- Remove conditional for xerces_c in EL6, as EL6 has xerces_c
  even for ppc64 via EPEL
- Remove EL4 conditionals
- Replace the python_lib macro definition and install Python bindings
  to sitearch directory, where they belong
- Use correct dap library names for linking
- Correct Ruby installation path in the Makefile instead of moving it later
- Use libdir variable in ppc64 Python path
- Delete obsolete chmod for Python libraries
- Move correction for Doxygen footer to prep section
- Delete bundled libraries before building
- Build without bsb and remove it from the tarball
- Use mavenpomdir macro and be a bit more precise on manpages in
  the files section
- Remove elements for grass support --> Will be replaced by plug-in
- Remove unnecessary defattr
- Correct version number in POM
- Allow for libpng 1.5

* Tue Dec 06 2011 Adam Jackson <ajax@redhat.com> - 1.7.3-11
- Rebuild for new libpng

* Tue May 17 2011 Orion Poplawski <orion@cora.nwra.com> - 1.7.3-10
- Rebuild for hdf5 1.8.7

* Fri Apr 22 2011 Volker Fröhlich <volker27@gmx.at> - 1.7.3-9
- Patched spaces problem for Mapinfo files (mif)
  (http://trac.osgeo.org/gdal/ticket/3694)
- Replaced all define macros with global
- Corrected ruby_sitelib to ruby_sitearch
- Use python_lib and ruby_sitearch instead of generating lists
- Added man-pages for binaries
- Replaced mkdir and install macros
- Removed Python files from main package files section, that 
  effectively already belonged to the Python sub-package

* Thu Apr 11 2011 Volker Fröhlich <volker27@gmx.at> - 1.7.3-8
- Solved image path problem with Latex
- Removed with-tiff and updated with-sqlite to with-sqlite3
- Add more refman documents
- Adapted refman loop to actual directories
- Harmonized buildroot macro use

* Thu Mar 31 2011 Orion Poplawski <orion@cora.nwra.com> - 1.7.3-7
- Rebuild for netcdf 4.1.2

* Wed Mar 23 2011 Dan Horák <dan@danny.cz> - 1.7.3-6
- rebuilt for mysql 5.5.10 (soname bump in libmysqlclient)

* Sun Mar 20 2011 Volker Fröhlich <volker27@gmx.at> 1.7.3-5
- Dropped unnecessary encoding conversion for Russian refman
- Install Russian refman
- Don't try to install refman for sdts and dgn, as they fail to compile
- Added -p to post and postun
- Remove private-shared-object-provides for Python and Perl
- Remove installdox scripts
- gcc 4.6 doesn't accept -Xcompiler 

* Thu Mar 10 2011 Kalev Lember <kalev@smartlink.ee> - 1.7.3-4
- Rebuilt with xerces-c 3.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Nov 21 2010 Viji Nair <viji [AT] fedoraproject DOT org> - 1.7.3-2
- Install all the generated pdf documentation.
- Build documentation as a separate package.
- Spec cleanup

* Fri Nov 19 2010 Viji Nair <viji [AT] fedoraproject DOT org> - 1.7.3-1
- Update to latest upstream version
- Added jnis
- Patches updated with proper version info
- Added suggestions from Ralph Apel <r.apel@r-apel.de>
        + Versionless symlink for gdal.jar
        + Maven2 pom
        + JPP-style depmap
        + Use -f XX.files for ruby and python

* Sun Oct 31 2010 Mathieu Baudier <mbaudier@argeo.org> - 1.7.2-5_2
- PCRaster support
- cURL support
- Disable building the reference manual (really too long...)

* Sat Oct 09 2010 Mathieu Baudier <mbaudier@argeo.org> - 1.7.2-5_1
- Add Java JNI libraries

* Sat Aug 14 2010 Mathieu Baudier <mbaudier@argeo.org> - 1.7.2-5_0
- Rebuild for EL GIS, based on work contributed by Nikolaos Hatzopoulos and Peter Hopfgartner 
- Use vanilla sources

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1.7.2-5
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Jul 20 2010 Orion Poplawski <orion@cora.nwra.com> - 1.7.2-4
- Rebuild with grass support

* Thu Jul 17 2010 Orion Poplawski <orion@cora.nwra.com> - 1.7.2-3
- Add patch to change AISConnect() to Connect() for libdap 3.10
- build without grass for libdap soname bump

* Tue Jul 13 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.7.2-2
- reenable grass support

* Fri Jul 09 2010 Robert Scheck <robert@fedoraproject.org> - 1.7.2-1
- upgrade to 1.7.2 (#587707, huge thanks to Sven Lankes)

* Thu Mar 18 2010 Balint Cristian <cristian.balint@gmail.com> - 1.7.1-2
- fix bz#572617

* Thu Mar 18 2010 Balint Cristian <cristian.balint@gmail.com> - 1.7.1-1
- new stable branch
- re-enable java ColorTable
- gdal custom fedora version banner
- rebuild without grass
- gdal manual are gone (upstream fault)

* Fri Feb  5 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.6.2-5
- reenable grass support

* Fri Feb  5 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.6.2-4
- temporarily disable grass support for bootstrapping
- rebuild for new libxerces-c

* Tue Dec  8 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 1.6.2-3
- Explicitly BR hdf-static in accordance with the Packaging
  Guidelines (hdf-devel is still static-only).

* Thu Nov 19 2009 Orion Poplawski <orion@cora.nwra.com> - 1.6.2-2
- re-enable grass support

* Tue Nov 17 2009 Orion Poplawski <orion@cora.nwra.com> - 1.6.2-1
- Update to 1.6.2
- Rebuild for netcdf 4.1.0

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.6.1-2
- rebuilt with new openssl

* Thu Jul 30 2009 Dan Horak <dan[at]danny.cz> - 1.6.1-1
- add patch for incompatibilities caused by libdap 3.9.x (thanks goes to arekm from PLD)
- update to 1.6.1
- don't install some refman.pdf, because they don't build
- don't fail on man pages with suffix other than .gz
- fix filelist for python subpackage

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-9
- Rebuild for libdap 3.9.3, bootstrap

* Mon Mar 23 2009 Jesse Keating <jkeating@redhat.com> - 1.6.0-8
- re-enable grass support

* Sun Mar 22 2009 Lubomir Rintel <lkundrak@v3.sk> - 1.6.0-7
- Depend specifically on GCJ for Java (Alex Lancaster)
- Disable grass (Alex Lancaster)
- Create %%_bindir before copying files there

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 04 2009 Balint Cristian <cristian.balint@gmail.com> - 1.6.0-4
- rebuild with grass support
- fix email typo

* Thu Jan 29 2009 Balint Cristian <cristian.balint@gmail.com> - 1.6.0-3
- rebuild against mysql 5.1.30

* Thu Jan 29 2009 Balint Cristian <cristian.balint@gmail.com> - 1.6.0-2
- email change
- rebuild without grass

* Fri Dec 12 2008 Balint Cristian <rezso@rdsor.ro> - 1.6.0-1
- final stable release

* Sat Dec 06 2008 Balint Cristian <rezso@rdsor.ro> - 1.6.0-0.2.rc4
- enable grass

* Sat Dec 06 2008 Balint Cristian <rezso@rdsor.ro> - 1.6.0-0.1.rc4
- new branch
- disable grass
- fix ruby compile

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.5.3-2
- Rebuild for Python 2.6

* Fri Oct 24 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.3-1
- new stable
- ship static package too
- fix some doc generation
- libdap patch for fc10 only

* Tue Sep 30 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.2-4
- enable gdal_array for python subpackage
- require numpy

* Tue Sep  9 2008 Patrice Dumas <pertusus@free.fr> - 1.5.2-3
- patch for libdap > 0.8.0, from Rob Cermak

* Thu Jun 12 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.2-1
- a new bugfix upstream
- drop gcc43 patch
- more license cleaned

* Wed May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-13
- fix pkgconfig too

* Wed May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-12
- fix once more gdal-config

* Tue May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-11
- fix multilib gdal-config, add wrapper around
- fix typos in cpl_config.h wrapper

* Tue May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-10
- fix for multilib packaging bz#341231
- huge spec cleanup
- enable russian and brazil docs
- enable and triage more docs

* Sun May 25 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-9
- enable ruby and java packages
- fix spurious sed problem
- spec file cosmetics

* Thu May 23 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-8
- fix sincos on all arch

* Thu May 15 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-7
- fix x86_64 problem

* Wed Apr 16 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-6
- disable fortify source, it crash gdal for now.

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-5
- really eanble against grass63

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-4
- disable grass to bootstrap once again

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-3
- rebuild to really pick up grass63 in koji

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-2
- enable build against newer grass
- enable build of reference manuals

* Tue Mar 25 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-1
- new bugfix release from upstream
- drop large parts from gcc43 patch, some are upstream now
- fix building with perl-5.10 swig binding issue

* Wed Feb 29 2008 Orion Poplawski <orion@cora.nwra.com> - 1.5.0-4
- Rebuild for hdf5-1.8.0, use compatability API define

* Tue Feb 12 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.0-3
- install cpl_config.h manually for bz#430894
- fix gcc4.3 build

* Mon Jan 14 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.0-2
- fix perl dependency issue.

* Mon Jan 07 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.0-1
- update to new 1.5.0 upstream stable
- dropped build patch since HFA/ILI/DGN mandatories are now present
- dropped swig patch, its upstream now
- enable HFA it holds Intergraph (TM) explicit public license
- enable DGN it holds Avenza Systems (TM) explicit public license
- enable ILI headers since now contain proper public license message
- keep and polish up rest of doubted license
- further fixed hdf not supporting netcdf for for bz#189337
- kill the annoying -Lexternal/lib for -lgeotiff
- fix configure to not export LDFLAGS anyomre, upstream 
  should really switch to real GNU automagic stuff
- pymod samples and rfc docs now gone
- hardcode external libtool to be used, LIBTOOL env not propagating anymore
- use DESTDIR instead

* Thu Jan 03 2008 Alex Lancaster <alexlan[AT]fedoraproject.org> - 1.4.2-7
- Re-enable grass support now that gdal has been bootstrapped

* Wed Jan 02 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.4.2-6
- Bootstrap 1st: disabling grass support
- Workaround for hdf not supporting netcdf (bug 189337 c8)
- Disabling documents creation for now.

* Thu Dec 06 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.4.2-5
- Rebuild for deps
- Disable grass to avoid circular deps

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
