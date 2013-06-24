# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

PREFIX = /usr
DATA = /share
BIN = /bin
PKGNAME = passcheck
COMMAND = passcheck
LICENSES = $(PREFIX)$(DATA)


all: passcheck.install doc

doc: info

info: passcheck.info.gz

%.info.gz: info/%.texinfo
	makeinfo "$<"
	gzip -9 -f "$*.info"

passcheck.install: passcheck.py
	cp "$<" "$@"
	sed -i "s:'blacklist':'$(DESTDIR)$(PREFIX)$(SHARE)/misc/$(PKGNAME).blacklist':g" "$@"

install: install-cmd install-license install-info

install-cmd:
	install -dm755 "$(DESTDIR)$(PREFIX)$(BIN)"
	install -dm755 "$(DESTDIR)$(PREFIX)$(SHARE)/misc"
	install -m755 passcheck.install "$(DESTDIR)$(PREFIX)$(BIN)/$(COMMAND)"
	install -m644 blacklist "$(DESTDIR)$(PREFIX)$(SHARE)/misc/$(PKGNAME).blacklist"

install-license:
	install -dm755 "$(DESTDIR)$(LICENSES)/$(PKGNAME)"
	install -m644 COPYING LICENSE "$(DESTDIR)$(LICENSES)/$(PKGNAME)"

install-info: passcheck.info.gz
	install -dm755 "$(DESTDIR)$(PREFIX)$(DATA)/info"
	install -m644 passcheck.info.gz "$(DESTDIR)$(PREFIX)$(DATA)/info/$(PKGNAME).info.gz"

uninstall:
	-rm -- "$(DESTDIR)$(PREFIX)$(BIN)/$(COMMAND)"
	-rm -- "$(DESTDIR)$(PREFIX)$(LIBEXEC)/$(COMMAND).py"
	-rm -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)/COPYING"
	-rm -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)/LICENSE"
	-rmdir -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/info/$(PKGNAME).info.gz"

.PHONY: clean
clean:
	-rm -f passcheck.info.gz passcheck.install

