%global with_debug 1

%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%global gomodulesmode GO111MODULE=on

%global _gvisor_installdir %{_libexecdir}/podman

%global desc_gvforwarder Forward traffic from a tap interface over vsock

Name: gvisor-tap-vsock
%if %{defined copr_username}
Epoch: 103
%else
Epoch: 6
%endif
# DO NOT TOUCH the Version string!
# The TRUE source of this specfile is:
# https://github.com/containers/podman/blob/main/rpm/podman.spec
# If that's what you're reading, Version must be 0, and will be updated by Packit for
# copr and koji builds.
# If you're reading this on dist-git, the version is automatically filled in by Packit.
Version: 0.8.5
License: Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND MIT
Release: 2%{?dist}
%if %{defined golang_arches_future}
ExclusiveArch: %{golang_arches_future}
%else
ExclusiveArch: aarch64 ppc64le s390x x86_64
%endif
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
%if %{defined rhel} && 0%{?rhel} == 8
BuildRequires: go-srpm-macros
%else
BuildRequires: go-rpm-macros
%endif
BuildRequires: make
%if %{defined copr_username}
Obsoletes: podman-gvproxy < 102:4.7.0-1
%else
Obsoletes: podman-gvproxy < 5:4.7.0-1
%endif
Provides: podman-gvproxy = %{epoch}:%{version}-%{release}
Requires: %{name}-gvforwarder = %{epoch}:%{version}-%{release}

%description
A replacement for libslirp and VPNKit, written in pure Go.
It is based on the network stack of gVisor. Compared to libslirp,
gvisor-tap-vsock brings a configurable DNS server and
dynamic port forwarding.

%package gvforwarder
Summary: %{desc_gvforwarder}
Provides: gvforwarder = %{epoch}:%{version}-%{release}
Obsoletes: %{name} < 6:0.7.0-6
Recommends: %{name} = %{epoch}:%{version}-%{release}

%description gvforwarder
%{desc_gvforwarder}

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
install -dp %{buildroot}%{_gvisor_installdir}
install -p -m0755 bin/gvproxy %{buildroot}%{_gvisor_installdir}
install -p -m0755 bin/gvforwarder %{buildroot}%{_gvisor_installdir}

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc README.md
%dir %{_gvisor_installdir}
%{_gvisor_installdir}/gvproxy

%files gvforwarder
%dir %{_gvisor_installdir}
%{_gvisor_installdir}/gvforwarder

%changelog
* Wed Jun 11 2025 Jindrich Novy <jnovy@redhat.com> - 6:0.8.5-2
- rebuild for CVE-2025-22871
- Resolves: RHEL-90038

* Mon Apr 07 2025 Jindrich Novy <jnovy@redhat.com> - 6:0.8.5-1
- Fix CVE-2025-22869 by updating to 0.8.5
- Resolves: RHEL-81313

* Tue Feb 04 2025 Jindrich Novy <jnovy@redhat.com> - 6:0.8.3-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.8.3
- Related: RHEL-60277

* Mon Jan 20 2025 Jindrich Novy <jnovy@redhat.com> - 6:0.8.2-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.8.2
- Related: RHEL-60277

* Tue Dec 03 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.8.1-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.8.1
- Resolves: RHEL-69761

* Wed Nov 27 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.8.0-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.8.0
- Related: RHEL-60277

* Tue Aug 27 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.7.5-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.7.5
- Related: RHEL-27608

* Mon Aug 05 2024 Jindrich Novy <jnovy@redhat.com> - 6:0.7.4-1
- update to https://github.com/containers/gvisor-tap-vsock/releases/tag/v0.7.4
- Related: RHEL-27608

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
