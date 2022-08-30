# Disable rpath check
# See https://fedoraproject.org/wiki/Changes/Broken_RPATH_will_fail_rpmbuild
%global __brp_check_rpaths %{nil}

%ifarch x86_64
%define _archflag -m64
%endif

%ifarch %{ix86}
%define _archflag -m32
%endif

# Set a macro to use for distribution variances
%if 0%{?fedora}
%define _distribution fedora
%endif

%if 0%{?rhel}
%define _distribution rhel
%endif

%if 0%{?epel}
%define _distribution epel
%endif

Name:                cde
Version:             2.5.0a
Release:             0%{?dist}
Summary:             Common Desktop Environment

Group:               User Interface/Desktops
License:             LGPLv2+
URL:                 http://cdesktopenv.sourceforge.net/
# Source is in git.  Actual releases can be found here:
#     http://sourceforge.net/projects/cdesktopenv/files/
# Source repo can be cloned this way:
#     git clone git://git.code.sf.net/p/cdesktopenv/code cdesktopenv-code
# The checkout-cde.sh generates the source archives used by this spec file.
Source0:             %{name}-%{version}.tar.gz
Source1:             checkout-cde.sh
Source2:             dt.conf
Source3:             dt.sh
Source4:             dt.csh
Source5:             dtspc
Source6:             cde.desktop
Source7:             fonts.alias
Source8:             fonts.dir
Source9:             dtlogin.service

BuildRoot:           %{_tmppath}/%{name}-%{version}-%{release}-root-%(id -u -n)

Requires:            xinetd
Requires:            ksh
%if "%{_distribution}" == "fedora"
Requires:            xstdcmap
Requires:            ( xorg-x11-utils or xdpyinfo or xwininfo or xvinfo or xprop or xlsfonts or xlsclients or xlsatoms or xev )
%else
Requires:            xorg-x11-server-utils
Requires:            xorg-x11-utils
%endif
%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
Requires:            xorg-x11-xinit
Requires:            xorg-x11-server-Xorg
Requires:            xorg-x11-fonts-ISO8859-1-100dpi
Requires:            xorg-x11-fonts-ISO8859-2-100dpi
Requires:            xorg-x11-fonts-ISO8859-9-100dpi
Requires:            xorg-x11-fonts-ISO8859-14-100dpi
Requires:            xorg-x11-fonts-ISO8859-15-100dpi
Requires:            xorg-x11-fonts-100dpi
Requires:            xorg-x11-fonts-misc
%endif
Requires:            ncompress
Requires:            rpcbind

%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
BuildRequires:       xorg-x11-proto-devel
%if 0%{?rhel} >= 7
%{?systemd_requires}
BuildRequires:       motif-devel
BuildRequires:       systemd
%endif
%endif
BuildRequires:       bdftopcf
BuildRequires:       file
BuildRequires:       ksh
BuildRequires:       m4
BuildRequires:       ncompress
BuildRequires:       bison
BuildRequires:       byacc
BuildRequires:       gcc
BuildRequires:       gcc-c++
BuildRequires:       g++
%if "%{_distribution}" == "fedora" || "%{_distribution}" == "rhel" || "%{_distribution}" == "epel"
BuildRequires:       libXp-devel
BuildRequires:       libXt-devel
BuildRequires:       libXmu-devel
BuildRequires:       libXft-devel
BuildRequires:       libXinerama-devel
BuildRequires:       libXpm-devel
BuildRequires:       libXaw-devel
BuildRequires:       libX11-devel
BuildRequires:       libXScrnSaver-devel
BuildRequires:       libjpeg-turbo-devel
BuildRequires:       libntirpc-devel
BuildRequires:       freetype-devel
BuildRequires:       openssl-devel
BuildRequires:       tcl-devel
BuildRequires:       xorg-x11-xbitmaps
BuildRequires:       libXdmcp-devel
BuildRequires:       libtirpc-devel
%endif
BuildRequires:       ncurses
BuildRequires:       rpcgen
BuildRequires:       mkfontdir
BuildRequires:       perl-SGMLSpm
BuildRequires:       xrdb
BuildRequires:       flex
# deps for autogen.sh
BuildRequires:       make
BuildRequires:       autoconf
BuildRequires:       automake
BuildRequires:       libtool

%description
CDE is the Common Desktop Environment from The Open Group.

%prep
%autosetup -p1
sed -i -e '1i #define FILE_MAP_OPTIMIZE' programs/dtfile/Utils.c

%build
./autogen.sh
%configure --disable-rpath
export MAKEFLAGS="-j$(nproc)"
%make_build

%install
mkdir -pm 0755 %{buildroot}%{_prefix}/dt/bin
mkdir -pm 0755 %{buildroot}%{_localstatedir}/dt
%make_install

# Configuration files
%{__install} -D -m 0644 %SOURCE2 %{buildroot}%{_sysconfdir}/ld.so.conf.d/dt.conf
%{__install} -D -m 0755 %SOURCE3 %{buildroot}%{_sysconfdir}/profile.d/dt.sh
%{__install} -D -m 0755 %SOURCE4 %{buildroot}%{_sysconfdir}/profile.d/dt.csh
%{__install} -D -m 0600 contrib/xinetd/ttdbserver %{buildroot}%{_sysconfdir}/xinetd.d/ttdbserver
%{__install} -D -m 0600 contrib/xinetd/cmsd %{buildroot}%{_sysconfdir}/xinetd.d/cmsd
%{__install} -D -m 0600 %SOURCE5 %{buildroot}%{_sysconfdir}/xinetd.d/dtspc
%{__install} -D -m 0644 %SOURCE6 %{buildroot}%{_datadir}/xsessions/cde.desktop
%{__install} -D -m 0644 %SOURCE7 %{buildroot}%{_sysconfdir}/dt/config/xfonts/C/fonts.alias
%{__install} -D -m 0644 %SOURCE8 %{buildroot}%{_sysconfdir}/dt/config/xfonts/C/fonts.dir
%{__install} -D -m 0644 %SOURCE9 %{buildroot}%{_unitdir}/dtlogin.service

# Create terminfo file for dtterm
pushd programs/dtterm
./terminfoCreate < terminfoChecklist > dtterm.terminfo
tic dtterm.terminfo
%{__install} -D -m 0644 dtterm %{buildroot}%{_datadir}/terminfo/d/dtterm
popd

%clean
rm -rf %{buildroot}

%post
# Specific permissions required on some things
chmod 2555 %{_bindir}/dtmail

PATH=/bin:/usr/bin

# Add 'dtspc' line to /etc/services
grep -qE "^dtspc" /etc/services >/dev/null 2>&1
if [ $? -eq 1 ]; then
    echo -e "dtspc\t6112/tcp\t#subprocess control" >> /etc/services
fi

# Make sure rpcbind runs with -i
if [ -f /etc/sysconfig/rpcbind ]; then
    . /etc/sysconfig/rpcbind
    echo "$RPCBIND_ARGS" | grep -q "\-i" >/dev/null 2>&1
    [ $? -eq 1 ] && echo "RPCBIND_ARGS=\"-i\"" >> /etc/sysconfig/rpcbind
else
    echo "RPCBIND_ARGS=\"-i\"" >> /etc/sysconfig/rpcbind
fi

%systemd_post rpcbind.service
%systemd_post xinetd.service

%postun
%systemd_postun_with_restart rpcbind.service
%systemd_postun_with_restart xinetd.service

PATH=/bin:/usr/bin
TMPDIR="$(mktemp -d)"

# Remove 'dtspc' line from /etc/services
grep -qE "^dtspc" /etc/services >/dev/null 2>&1
if [ $? -eq 0 ]; then
    grep -vE "^dtspc\s+6112" /etc/services > $TMPDIR/services
    mv $TMPDIR/services /etc/services
fi

rm -rf $TMPDIR

%files
%defattr(-,root,root,-)
%doc CONTRIBUTORS COPYING README.md copyright HISTORY
%{_prefix}/dt
%attr(1777, root, root) %{_localstatedir}/dt
%config %{_sysconfdir}/ld.so.conf.d/dt.conf
%config %{_sysconfdir}/profile.d/dt.sh
%config %{_sysconfdir}/profile.d/dt.csh
%config %{_sysconfdir}/dt
%config %{_sysconfdir}/xinetd.d/cmsd
%config %{_sysconfdir}/xinetd.d/dtspc
%config %{_sysconfdir}/xinetd.d/ttdbserver
%config %{_sysconfdir}/dt/config/xfonts/C/fonts.alias
%config %{_sysconfdir}/dt/config/xfonts/C/fonts.dir
%config %{_sysconfdir}/cde/fontaliases/fonts.alias
%docdir %{_mandir}/man1
%docdir %{_mandir}/man1n
%docdir %{_mandir}/man3
%docdir %{_mandir}/man4
%docdir %{_mandir}/man5
%docdir %{_mandir}/man6
%{_datadir}/cde/*
%{_libexecdir}/cde/*
%{_libdir}/*
%dir %{_includedir}/Dt
%dir %{_includedir}/Tt
%dir %{_includedir}/csa
%{_bindir}/*
%config %{_prefix}/app-defaults/C/Dtbuilder
%dir %{_prefix}/lib/debug


%{_datadir}/xsessions
%{_datadir}/terminfo
%{_unitdir}/dtlogin.service

%changelog
* Tue Aug 30 2022 Trung Le <trung.le@ruby-journal.com> - 2.5.0a-0
- Upgrade to CDE 2.5.0a
- Remove support for RHEL v6 or older
- Remove support for CentOS
- Remove support for Fedora 34 or older

* Wed Aug 22 2018 David Cantrell <dcantrell@redhat.com> - 2.3.0-2
- Conditionalize the BR on rpcgen for only recent systems

* Thu Aug 16 2018 David Cantrell <dcantrell@redhat.com> - 2.3.0-1
- Upgrade to CDE 2.3.0
- Use patchelf rather than chrpath in %%install
- Build requires rpcgen
- Replace deprecated/removed ustat(2) calls with statfs(2)

* Tue Sep 05 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-9
- Create /usr/share/terminfo/d/dtterm entry

* Tue Sep 05 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-8
- In the postinstall script, check for systemctl in /usr/bin
- Build with libtirpc-devel since that does not work correctly for CDE
  on 64-bit platforms right now
- Add systemd unit file for dtlogin for EL-7 and Fedora

* Tue Sep 05 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-7
- Small fix for libast/ast.h in the dtksh source
- Require xorg-x11-fonts-misc to map to default CDE fonts

* Thu Aug 24 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-6
- Add fonts.alias and fonts.dir files for /etc/dt/config/xfonts/C
- Patch /etc/xinetd.d/ttdbserver file to enable by default
- Ensure /var/dt is installed with 1777 permissions
- In the RPM postinstall script, tell the user to make sure rpcbind
  and xinetd services are enabled

* Tue May 30 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-5
- Updated spec file for CentOS 7.x building

* Tue May 16 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-4
- Complete packaging using the installCDE script
- Initial set of configuration files and control scripts
- Runtime requirement on xinetd
- xsession file to support launching CDE from gdm login screen

* Thu May 11 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-3
- Shift to using installCDE to install the build
- Add ksh as a BuildRequires

* Wed May 10 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-2
- Sort out the file list and get things moved to the correct place

* Thu Apr 27 2017 David Cantrell <dcantrell@redhat.com> - 2.2.4-1
- First update of this package to CDE 2.2.4

* Thu Aug 23 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-3.20120816gitce4004f
- Unpack dt.tar in the buildroot, create required directories
- Disable the use of -Wl,-rpath,PATH during the build

* Fri Aug 17 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-2.20120816gitce4004f
- Use /bin/sh in installation scripts, not /bin/ksh
- Use -m64 and -m32 in BOOTSTRAPCFLAGS to get correct linking

* Thu Aug 16 2012 David Cantrell <dcantrell@redhat.com> - 2.2.0-1.20120816gitce4004f
- Initial packaging attempt
