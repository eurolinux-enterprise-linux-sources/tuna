%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_ver: %define python_ver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name: tuna
Version: 0.10.4
Release: 9%{?dist}
License: GPLv2
Summary: Application tuning GUI & command line utility
Group: Applications/System
Source: http://userweb.kernel.org/~acme/tuna/%{name}-%{version}.tar.bz2
# Actual Source: https://git.kernel.org/cgit/utils/tuna/tuna.git
URL: http://userweb.kernel.org/~acme/tuna/

Patch1: CLI-fix-ps_show_thread-call-with-bad-args-count.patch
Patch2: spec-Update-the-Source-in-tuna.spec.patch
Patch3: procview-Added-column-for-SystemD-CGroup-monitoring.patch
Patch4: tuna-cmd-New-command-line-params-for-tuning-profiles.patch
Patch5: CLI-fix-traceback-where-enter-p-policy-without-prio.patch

BuildArch: noarch
BuildRequires: python-devel, gettext
Requires: python-ethtool
Requires: python-linux-procfs >= 0.4.5
Requires: python-schedutils >= 0.2
# This really should be a Suggests...
# Requires: python-inet_diag
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%description
Provides interface for changing scheduler and IRQ tunables, at whole CPU and at
per thread/IRQ level. Allows isolating CPUs for use by a specific application
and moving threads and interrupts to a CPU by just dragging and dropping them.
Operations can be done on CPU sockets, understanding CPU topology.

Can be used as a command line utility without requiring the GUI libraries to be
installed.

%package -n oscilloscope
Summary: Generic graphical signal plotting tool
Group: Applications/System
Requires: tuna
Requires: python-matplotlib
Requires: numpy
Requires: pygtk2

%description -n oscilloscope
Plots stream of values read from standard input on the screen together with
statistics and a histogram.

Allows to instantly see how a signal generator, such as cyclictest, signaltest
or even ping, reacts when, for instance, its scheduling policy or real time
priority is changed, be it using tuna or plain chrt & taskset.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}
mkdir -p %{buildroot}/{%{_bindir},%{_datadir}/tuna/help/kthreads,%{_mandir}/man8}
install -p -m644 tuna/tuna_gui.glade %{buildroot}/%{_datadir}/tuna/
install -p -m755 tuna-cmd.py %{buildroot}/%{_bindir}/tuna
install -p -m755 oscilloscope-cmd.py %{buildroot}/%{_bindir}/oscilloscope
install -p -m644 help/kthreads/* %{buildroot}/%{_datadir}/tuna/help/kthreads/
install -p -m644 docs/tuna.8 %{buildroot}/%{_mandir}/man8/

# l10n-ed message catalogues
for lng in `cat po/LINGUAS`; do
        po=po/"$lng.po"
        mkdir -p %{buildroot}/%{_datadir}/locale/${lng}/LC_MESSAGES
        msgfmt $po -o %{buildroot}/%{_datadir}/locale/${lng}/LC_MESSAGES/%{name}.mo
done

%find_lang %name

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc ChangeLog
%if "%{python_ver}" >= "2.5"
%{python_sitelib}/*.egg-info
%endif
%{_bindir}/tuna
%{_datadir}/tuna/
%{python_sitelib}/tuna/
%{_mandir}/man8/tuna.8*

%files -n oscilloscope
%defattr(-,root,root,-)
%{_bindir}/oscilloscope
%doc docs/oscilloscope+tuna.html
%doc docs/oscilloscope+tuna.pdf

%changelog
* Tue Dec 16 2014 John Kacur <jkacur@redhat.com> - 0.10.4-9
- There is still an import of tuna, but the version is unimportant
- Readd the requires without the version release dependency.
- Resolves: rhbz#914366

* Tue Dec 16 2014 John Kacur <jkacur@redhat.com> - 0.10.4-8
- Removed the Requires of tuna from oscilloscope in this spec file.
- Resolves: rhbz#914366

* Mon Aug 25 2014 John Kacur <jkacur@redhat.com> - 0.10.4-7
- CLI-fix-traceback-where-enter-p-policy-without-prio.patch
- Resolves: rhbz#1035795

* Thu Mar 27 2014 John Kacur <jkacur@redhat.com> - 0.10.4-5
- CLI: fix traceback where enter -p policy without prio (1035795)
- tuna-cmd: New command line params for tuning profiles
- Resolves: rhbz#1059685
- Resolves: rhbz#1035795

* Thu Dec 05 2013 John Kacur <jkacur@redhat.com> - 0.10.4-4
- Rebuilt for rhel6.6
- spec: Explicitly use separate patches for non-upstream changes
- Resolves: rhbz#1029591

* Fri May 17 2013 John Kacur <jkacur@redhat.com> - 0.10.4-3
- Rebuilt for rhel6.5
- Resolves: rhbz#957855

* Fri Sep 14 2012 John Kacur <jkacur@redhat.com> - 0.10.3-2
- Rebuilt for rhel6.4
- Resolves: rhbz#812455

* Fri Aug 24 2012 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.10.3-1
- New upstream release

* Thu Jul 28 2011 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.10.2-1
- New upstream release

* Wed Feb 23 2011 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.10.1-1
- New upstream release

* Wed Feb 23 2011 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.10-1
- New upstream release

* Mon May 17 2010 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.9.3-1
- New upstream release
- Fixes the folowing bugzilla.redhat.com tickets:
- 563355 error in tuna --help output
- 574950 cannot use cpu ranges in the tuna GUI
- 559770 tuna backtrace when moving threads
- 563352 tuna backtrace when no thread list is given for --priority
- 563350 tuna backtrace when scheduler is mis-typed.

* Thu Nov 12 2009 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.9.2-1
- New upstream release

* Thu Sep 03 2009 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.9.1-1
- New upstream release

* Wed Aug 26 2009 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.9-3
- Rewrite the oscilloscope package summary
- Remove the shebang in tuna/oscilloscope.py

* Mon Aug 17 2009 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.9-2
- Use install -p
- Add BuildRequires for gettext

* Fri Jul 10 2009 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.9-1
- Fedora package reviewing changes: introduce ChangeLog file
