%global _iconsbasedir %{?_iconsbasedir:/usr/share/icons/hicolor}
%global _desktopdir %{?_desktopdir:/usr/share/applications}

%global icon_cache_touch /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
%global icon_cache_gtk_update /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

Name:           enki
Version:        15.04.0
Release:        5%{?dist}
Summary:        Advanced text editor for programmers
Group:          Productivity/Text/Editors

License:        GPL-2.0
URL:            http://enki-editor.org/

Source0:        https://github.com/hlamer/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  desktop-file-utils
BuildRequires:  python-setuptools
BuildRequires:  python-qutepart >= 2.2
Requires:       python >= 2.7
Requires:       python-markdown
Requires:       python-qutepart >= 2.2
Requires:       python-docutils
Requires:       ctags


%if 0%{?fedora_version}
BuildRequires:  PyQt4
Requires:       PyQt4
%else
BuildRequires:  python-qt4
Requires:       python-qt4
%endif

%description
Enki is an advanced text editor for programmers. It is:
    - User friendly. Intuitive interface. Works out of the box.
      You don't have to read a lot of docs
    - Hacker friendly. Work as quickly as possible.
      You don't need your mouse for coding.
    - Lighweight. Some IDEs show splashscreen.
      Enki will never do it. It just starts quickly.
    - Advanced. You invent software. An editor helps you to do a routine job.
    - Extensible. Operating systems are designed for running applications.
      Enki is designed for running plugins.
    - Cross platform. Use your habitual editor on any OS.
      Currently has beeen tested on Linux, MacOS X, Windows.
    - High quality. No long list of fancy features.
      But, what is done, is done well.
    - Open source. In GitHub we trust.


%prep
%setup0 -q


%build
%{__python} setup.py build


%install
%{__python} setup.py install --force --skip-build --prefix=%{_prefix} --root %{buildroot}


%check
desktop-file-validate %{buildroot}%{_desktopdir}/%{name}.desktop


%files
%defattr(-,root,root)
%doc LICENSE.GPL2 README.md ChangeLog
%{python_sitelib}/%{name}*
%{_iconsbasedir}/*/apps/%{name}.*
%{_datarootdir}/pixmaps/%{name}.png
%{_desktopdir}/%{name}.desktop
%{_bindir}/%{name}

%dir /usr/share/icons/hicolor/32x32/apps
%dir /usr/share/icons/hicolor/32x32
%dir /usr/share/icons/hicolor/48x48/apps
%dir /usr/share/icons/hicolor/48x48
%dir /usr/share/icons/hicolor/scalable/apps
%dir /usr/share/icons/hicolor/scalable
%dir /usr/share/icons/hicolor/


%post
%{icon_cache_touch}


%postun
if [ $1 -eq 0 ] ; then
    %{icon_cache_touch}
    %{icon_cache_gtk_update}
fi


%posttrans
%{icon_cache_gtk_update}


%changelog
* Mon Apr 27 2015 Andrei Kopats <hlamer@tut.by> 15.04.0-11
 - Vim mode
 - Literate programming and preview enhancements
 - Improvements and bugfixes

* Mon Aug 18 2014 Andrei Kopats <hlamer@tut.by> 14.07.2-10
 - Fix pylint and navigator related bugs

* Tue Jul 22 2014 Andrei Kopats <hlamer@tut.by> 14.07.0-9
 - Draw incorrect indentation
 - Source code to HTML conversion support (literate programming) by Bryan Jones
 - Pylint support

* Thu Mar 13 2014 Andrei Kopats <hlamer@tut.by> 14.03.0-8
 - Open main menu with F10
 - Sort tags in the Navigator
 - Python REPL
 - Navigator tree filtering
 - Strip trailing whitespaces

* Mon Nov 25 2013 Andrei Kopats <hlamer@tut.by> 13.11.1-7
- Fix crash in Navigation
- Recursively create directories on file save

* Wed Nov 20 2013 Andrei Kopats <hlamer@tut.by> 13.11.0-6
- RPM release for Suse
- Navigation, based on ctags

* Sun Oct 6 2013 Jairo Llopis <yajo.sk8@gmail.com> 13.09.2-5
- Add dependency to python-docutils.

* Sun Oct 6 2013 Jairo Llopis <yajo.sk8@gmail.com> 13.09.2-4
- New upstream version.

* Sun Sep 8 2013 Jairo Llopis <yajo.sk8@gmail.com> 13.08.1-3
- New upstream version, now based on qutepart.
- Remove patch that has already been merged upstream.

* Tue Jul 16 2013 Jairo Llopis <yajo.sk8@gmail.com> 12.10.3-2
- Declare variables with global.
- Link patch0 to its upstream bug.
- Validate desktop file installation.
- Add icon cache scriptlets.
- Change Source tag for Source0.
- Fix requirements.

* Sat Jul 6 2013 Jairo Llopis <yajo.sk8@gmail.com> 12.10.3-1
- Initial release.
