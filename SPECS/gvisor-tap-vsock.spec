%global with_debug 1

%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%global gomodulesmode GO111MODULE=on

Name: gvisor-tap-vsock
Epoch: 6
Version: 0.7.3
License: Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND MIT
Release: 3%{?dist}
ExclusiveArch: %{golang_arches_future}
Summary: Go replacement for libslirp and VPNKit
URL: https://github.com/containers/%{name}
# All SourceN files fetched from upstream
Source0: %{url}/archive/refs/tags/v%{version}.tar.gz
BuildRequires: gcc
BuildRequires: glib2-devel
BuildRequires: glibc-devel
BuildRequires: glibc-static
BuildRequires: golang
BuildRequires: git-core
BuildRequires: go-rpm-macros
BuildRequires: make
Obsoletes: podman-gvproxy < 5:4.7.0-1
Provides: podman-gvproxy = %{epoch}:%{version}-%{release}

%description
A replacement for libslirp and VPNKit, written in pure Go.
It is based on the network stack of gVisor and is used to provide
networking for podman-machine virtual machines. Compared to libslirp,
gvisor-tap-vsock brings a configurable DNS server and dynamic
port forwarding.

%prep
%autosetup -Sgit -n %{name}-%{version}

%build
%set_build_flags
export CGO_CFLAGS=$CFLAGS

# These extra flags present in $CFLAGS have been skipped for now as they break the build
CGO_CFLAGS=$(echo $CGO_CFLAGS | sed 's/-flto=auto//g')
CGO_CFLAGS=$(echo $CGO_CFLAGS | sed 's/-Wp,D_GLIBCXX_ASSERTIONS//g')
CGO_CFLAGS=$(echo $CGO_CFLAGS | sed 's/-specs=\/usr\/lib\/rpm\/redhat\/redhat-annobin-cc1//g')

%ifarch x86_64
export CGO_CFLAGS+=" -m64 -mtune=generic -fcf-protection=full"
%endif

# reset LDFLAGS for plugins and gvisor binaries
LDFLAGS=''

# build gvisor-tap-vsock binaries
%gobuild -o bin/gvproxy ./cmd/gvproxy
%gobuild -o bin/gvforwarder ./cmd/vm

%install
# install gvproxy
install -dp %{buildroot}%{_libexecdir}/podman
install -p -m0755 bin/gvproxy %{buildroot}%{_libexecdir}/podman
install -p -m0755 bin/gvforwarder %{buildroot}%{_libexecdir}/podman

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc README.md
%dir %{_libexecdir}/podman
%{_libexecdir}/podman/gvproxy
%{_libexecdir}/podman/gvforwarder

%changelog
* Thu May 02 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.7.3-3
- rebuild for CVE-2023-45290
- Resolves: RHEL-28388

* Mon Feb 12 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.7.3-2
- Add gating.yaml
- Related: Jira:RHEL-2112

* Fri Feb 09 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.7.3-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.7.3
- Related: RHEL-2112

* Wed Jan 31 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.7.2-2
- Update description - thanks to Derrick Ornelas
- Resolves: RHELPLAN-168385

* Fri Jan 19 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.7.2-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.7.2
- Related: RHEL-2112

* Mon Oct 02 2023 Jindrich Novy <jnovy@redhat.com> - 6:0.7.1-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.7.1
- Related: Jira:RHEL-2112

* Wed Sep 27 2023 Jindrich Novy <jnovy@redhat.com> - 6:0.7.0-2
- initial import
- Resolves: Jira:RHELPLAN-167882

* Tue Aug 01 2023 Lokesh Mandvekar <lsm5@fedoraproject.org> - 6:0.7.0-3
- correctly obsolete older podman-gvproxy

* Tue Aug 01 2023 Lokesh Mandvekar <lsm5@fedoraproject.org> - 6:0.7.0-2
- fix install paths

* Tue Aug 01 2023 Lokesh Mandvekar <lsm5@fedoraproject.org> - 6:0.7.0-1
- Resolves: #2224434 - initial upload
