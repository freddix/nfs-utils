Summary:	Network File System utilities
Name:		nfs-utils
Version:	1.2.8
Release:	4
License:	GPL v2
Group:		Networking
Source0:	http://downloads.sourceforge.net/project/nfs/%{name}/%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	6e7d97de51e428a0b8698c16ca23db77
Source1:	rpc-statd.service
Patch0:		%{name}-mtab-sym.patch
Patch1:		%{name}-start-statd.patch
BuildRequires:	device-mapper-devel
BuildRequires:	keyutils-devel
BuildRequires:	libblkid-devel
BuildRequires:	libcap-devel
BuildRequires:	libevent-devel
BuildRequires:	libmount-devel
BuildRequires:	libnfsidmap-devel
BuildRequires:	libtirpc-devel
BuildRequires:	pkg-config
BuildRequires:	rpm-pythonprov
BuildRequires:	sqlite3-devel
Requires(post,preun,postun):	systemd-units
Requires(pre,postun):	pwdutils
Requires:	rpcbind
Provides:	group(rpcstatd)
Provides:	user(rpcstatd)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Network File System (NFS) is a distributed file system protocol
originally developed by Sun Microsystems in 1984,[1] allowing a user
on a client computer to access files over a network in a manner
similar to how local storage is accessed. NFS, like many other
protocols, builds on the Open Network Computing Remote Procedure Call
(ONC RPC) system. The Network File System is an open standard defined
in RFCs, allowing anyone to implement the protocol.

This package contains common parts used for client and server
packages.

%package server
Summary:	Network File System server and utilities
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description server
Network File System server and utilities.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%configure \
	--disable-gss			\
	--enable-libmount-mount		\
	--enable-mountconfig		\
	--with-statduser=rpcstatd	\
	--with-statedir=/var/lib/nfs	\
	--without-tcp-wrappers

# pre-built binaries in the tarball!
%{__make} clean
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/exports.d	\
	$RPM_BUILD_ROOT%{prefix}/lib/modules-load.d	\
	$RPM_BUILD_ROOT%{systemdunitdir}		\
	$RPM_BUILD_ROOT/var/lib/nfs/{rpc_pipefs,v4recovery}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	sbindir=%{_sbindir}

touch $RPM_BUILD_ROOT%{_sysconfdir}/exports

install %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 113 rpcstatd
%useradd -u 113 -d /var/lib/nfs -s /usr/bin/false -c "RPC statd user" -g rpcstatd rpcstatd

%post
%systemd_post rpc-statd.service

%preun
%systemd_preun rpc-statd.service

%postun
if [ "$1" = "0" ]; then
    %userremove rpcstatd
    %groupremove rpcstatd
fi
%systemd_postun

%files
%defattr(644,root,root,755)
%attr(4755,root,root) %{_sbindir}/mount.nfs
%attr(4755,root,root) %{_sbindir}/mount.nfs4
%attr(4755,root,root) %{_sbindir}/umount.nfs
%attr(4755,root,root) %{_sbindir}/umount.nfs4
%attr(755,root,root) %{_sbindir}/mountstats
%attr(755,root,root) %{_sbindir}/nfsiostat
%attr(755,root,root) %{_sbindir}/rpc.statd
%attr(755,root,root) %{_sbindir}/rpcdebug
%attr(755,root,root) %{_sbindir}/showmount
%attr(755,root,root) %{_sbindir}/start-statd

%attr(755,nobody,root) %dir /var/lib/nfs
%attr(600,rpcstatd,rpcstatd) %config(noreplace) %verify(not md5 mtime size) /var/lib/nfs/state
%attr(700,rpcstatd,rpcstatd) %dir /var/lib/nfs/sm
%attr(700,rpcstatd,rpcstatd) %dir /var/lib/nfs/sm.bak
%{systemdunitdir}/rpc-statd.service

%{_mandir}/man8/rpc.statd.8*
%{_mandir}/man8/statd.8*
%{_mandir}/man5/nfsmount.conf.5*
%{_mandir}/man8/mount.nfs.8*
%{_mandir}/man8/mountstats.8*
%{_mandir}/man8/nfsiostat.8*
%{_mandir}/man8/showmount.8*
%{_mandir}/man8/umount.nfs.8*

%files server
# TODO: finish server part
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/sm-notify
%attr(755,root,root) %{_sbindir}/blkmapd
%attr(755,root,root) %{_sbindir}/nfsidmap
%attr(755,root,root) %{_sbindir}/rpc.idmapd
%attr(755,root,root) %{_sbindir}/exportfs
%attr(755,root,root) %{_sbindir}/rpc.mountd
%attr(755,root,root) %{_sbindir}/rpc.nfsd
%attr(755,root,root) %{_sbindir}/nfsstat
%attr(755,root,root) %{_sbindir}/nfsdcltrack

%dir /var/lib/nfs/rpc_pipefs
%dir /var/lib/nfs/v4recovery

%attr(664,root,fileshare) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/exports
%dir %{_sysconfdir}/exports.d
%config(noreplace) %verify(not md5 mtime size) /var/lib/nfs/xtab
%config(noreplace) %verify(not md5 mtime size) /var/lib/nfs/etab
%config(noreplace) %verify(not md5 mtime size) /var/lib/nfs/rmtab

%{_mandir}/man5/exports.5*
%{_mandir}/man5/nfs.5*
%{_mandir}/man7/nfsd.7*
%{_mandir}/man8/blkmapd.8*
%{_mandir}/man8/exportfs.8*
%{_mandir}/man8/idmapd.8*
%{_mandir}/man8/mountd.8*
%{_mandir}/man8/nfsd.8*
%{_mandir}/man8/nfsdcltrack.8*
%{_mandir}/man8/nfsidmap.8*
%{_mandir}/man8/nfsstat.8*
%{_mandir}/man8/rpc.idmapd.8*
%{_mandir}/man8/rpc.mountd.8*
%{_mandir}/man8/rpc.nfsd.8*
%{_mandir}/man8/rpc.sm-notify.8*
%{_mandir}/man8/rpcdebug.8*
%{_mandir}/man8/sm-notify.8*

