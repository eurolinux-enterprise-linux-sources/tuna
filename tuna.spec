%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_ver: %define python_ver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name: tuna
Version: 0.13
Release: 6%{?dist}
License: GPLv2
Summary: Application tuning GUI & command line utility
Group: Applications/System
Source: https://www.kernel.org/pub/software/utils/tuna/%{name}-%{version}.tar.xz

Patch1: tuna-cpuview.py-Omit-offline-cpus-in-socket_ids-list.patch
Patch2: display-usage-instead-of-traceback-when-c-missing-args.patch
Patch3: CLI-start-a-process-from-tuna.patch
Patch4: docs-upgrade-tuna.8-man-page-with-option-r.patch
Patch5: tuna-Use-errno-codes-instead-of-numbers.patch
Patch6: tuna-isolate_cpus-exit-with-a-message.patch

URL: https://git.kernel.org/pub/scm/utils/tuna/tuna.git
BuildArch: noarch
BuildRequires: python-devel, gettext, desktop-file-utils
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
Requires: python-matplotlib
Requires: numpy
Requires: pygtk2
Requires: tuna = %{version}-%{release}

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
%patch6 -p1

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}
mkdir -p %{buildroot}/%{_sysconfdir}/tuna/
mkdir -p %{buildroot}/{%{_bindir},%{_datadir}/tuna/help/kthreads,%{_mandir}/man8}
mkdir -p %{buildroot}/%{_datadir}/polkit-1/actions/
install -p -m644 tuna/tuna_gui.glade %{buildroot}/%{_datadir}/tuna/
install -p -m755 tuna-cmd.py %{buildroot}/%{_bindir}/tuna
install -p -m755 oscilloscope-cmd.py %{buildroot}/%{_bindir}/oscilloscope
install -p -m644 help/kthreads/* %{buildroot}/%{_datadir}/tuna/help/kthreads/
install -p -m644 docs/tuna.8 %{buildroot}/%{_mandir}/man8/
install -p -m644 etc/tuna/example.conf %{buildroot}/%{_sysconfdir}/tuna/
install -p -m644 etc/tuna.conf %{buildroot}/%{_sysconfdir}/
install -p -m644 org.tuna.policy %{buildroot}/%{_datadir}/polkit-1/actions/
desktop-file-install --dir=%{buildroot}/%{_datadir}/applications tuna.desktop

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
%config(noreplace) %{_sysconfdir}/tuna.conf
%config %{_sysconfdir}/tuna/example.conf
%{_datadir}/polkit-1/actions/org.tuna.policy
%{_datadir}/applications/tuna.desktop

%files -n oscilloscope
%defattr(-,root,root,-)
%{_bindir}/oscilloscope
%doc docs/oscilloscope+tuna.html
%doc docs/oscilloscope+tuna.pdf

%changelog
* Wed Sep 13 2017 John Kacur - 0.13-6
- Use errno codes instead of plain numbers
- Exit with a message instead of a traceback in isolate_cpus
Resolves: rhbz#1472840

* Mon Jun 13 2016 John Kacur - 0.13-5
- Rebuild to document
  tuna thows an exception instead of an error message when sched_setaffinity returns EINVAL
  This was actually fixed in v0.13-1
Resolves: rhbz#1290445

* Mon May 30 2016 John Kacur - 0.13-4
- CLI-start-a-process-from-tuna
- docs: upgrade tuna.8 man page with option -r
Resolves: rhbz#1235829

* Mon May 30 2016 John Kacur - 0.13-3
- Display usage instead of traceback when -c missing args or args is incorrect
Resolves: rhbz#1268287

* Mon May 30 2016 John Kacur - 0.13-2
- tuna: cpuview.py: Omit offline cpus in socket_ids list
Resolves: rhbz#1036156

* Tue May 24 2016 John Kacur - 0.13-1
- Upgrade to v0.13
- Remove patches that are included in 0.13
Resolves: rhbz#1235828

* Mon Dec 21 2015 John Kacur - 0.11.1-11
- tuna-fix-the-check-of-PF_NO_SETAFFINITY-flag-for-thr.patch
Resolves: rhbz#1286221

* Thu Jun 25 2015 John Kacur <jkacur@redhat.com> - 0.11.1-10
- dropped the git housekeeping patch, not relevant here
- docs-Remove-stray-a.patch
- CLI-Introduce-nohz_full-N-entity.patch
- tuna-config-Fix-pygtk-import.patch
- tuna-Make-isolate-include-operations-affect-proc-irq.patch
- tuna-Decide-whether-to-isolate-a-thread-based-on-PF_.patch
- tuna-Fix-race-in-is_hardirq_handler.patch
- CLI-Do-not-show-column-headers-when-not-outputting-t.patch
- Correct-a-typo-in-the-net.ipv4.ipfrag_time-help-stri.patch
Resolves: rhbz#1234963

* Wed May 27 2015 John Kacur <jkacur@redhat.com> - 0.11.1-9
- Fix-behavior-for-dot-inside-proc-sys-path.patch
Resolves: rhbz#1178917

* Mon Oct 20 2014 John Kacur <jkacur@redhat.com> - 0.11.1-8
- CLI-fix-traceback-due-unavailable-display.patch
Resolves: rhbz#1035853

* Fri Sep 12 2014 John Kacur <jkacur@redhat.com> - 0.11.1-7
- Add a tuna.desktop file
Resolves: rhbz#996954

* Tue Mar 11 2014 John Kacur <jkacur@redhat.com> - 0.11.1-6
- tuna-modified-sysctl-settings-in-example.conf (1031582)
- CLI-fix-traceback-where-enter-p-policy-without-prio (1035794)
Resolves: rhbz#1035794

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.11.1-5
- Mass rebuild 2013-12-27

* Thu Nov 07 2013 John Kacur <jkacxur@redhat.com> - 0.11.1-4
- tuna: Do polkit auth for GUI BZ:919212,974027 (996885)
- tuna: Auto Correction for config file errors (1015062)
- Rebased to 0.11.1 upstream
Resolves: rhbz#996885
Resolves: rhbz#1015062

* Thu Aug 22 2013 John Kacur <jkacur@redhat.com> - 0.11-3
- spec: Mark configuration files with %config (998984)
- spec: Document the real location of the source in a comment (998987)
- CLI: fix ps_show_thread call with bad args count (1000025)

* Tue Jun 11 2013 Jiri Kastner <jkastner@redhat.com> - 0.11-2
- changed dependencies from python-numeric to numpy
- merged spec changes from upstream

* Thu Jun  6 2013 Jiri Kastner <jkastner@redhat.com> - 0.11-1
- New upstream release

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Aug 01 2010 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 0.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

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
