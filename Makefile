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



all: command doc shell


command: passcheck.install

passcheck.install: passcheck.py
	cp "$<" "$@"
	sed -i "s:'blacklist':'$(PREFIX)$(DATA)/misc/$(PKGNAME).blacklist':g" "$@"


doc: info

info: passcheck.info.gz

%.info.gz: info/%.texinfo
	makeinfo "$<"
	gzip -9 -f "$*.info"


shell: bash fish zsh

bash: passcheck.bash-completion
fish: passcheck.fish-completion
zsh: passcheck.zsh-completion

passcheck.auto-completion.install: passcheck.auto-completion
	cp "$<" "$@"
	sed -i 's/^(passcheck$$/($(COMMAND)/' "$@"

passcheck.%sh-completion: passcheck.auto-completion.install
	auto-auto-complete "$*sh" --output "$@" --source "$<"



.PHONY:  install-cmd install-license install-info install-bash install-fish install-zsh
install: install-cmd install-license install-info install-bash install-fish install-zsh

install-cmd:
	install -dm755 -- "$(DESTDIR)$(PREFIX)$(BIN)"
	install -dm755 -- "$(DESTDIR)$(PREFIX)$(DATA)/misc"
	install -m755 passcheck.install -- "$(DESTDIR)$(PREFIX)$(BIN)/$(COMMAND)"
	install -m644 blacklist -- "$(DESTDIR)$(PREFIX)$(DATA)/misc/$(PKGNAME).blacklist"

install-license:
	install -dm755 -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)"
	install -m644 COPYING LICENSE -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)"

install-info: passcheck.info.gz
	install -dm755 -- "$(DESTDIR)$(PREFIX)$(DATA)/info"
	install -m644 passcheck.info.gz -- "$(DESTDIR)$(PREFIX)$(DATA)/info/$(PKGNAME).info.gz"

install-bash: bash
	install -Dm644 passcheck.bash-completion -- "$(DESTDIR)$(PREFIX)$(DATA)/bash-completion/completions/$(COMMAND)"

install-fish: fish
	install -Dm644 passcheck.fish-completion -- "$(DESTDIR)$(PREFIX)$(DATA)/fish/completions/$(COMMAND).fish"

install-zsh: zsh
	install -Dm644 passcheck.zsh-completion -- "$(DESTDIR)$(PREFIX)$(DATA)/zsh/site-functions/_$(COMMAND)"



uninstall:
	-rm -- "$(DESTDIR)$(PREFIX)$(BIN)/$(COMMAND)"
	-rm -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)/COPYING"
	-rm -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)/LICENSE"
	-rmdir -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/info/$(PKGNAME).info.gz"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/bash-completion/completions/$(COMMAND)"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/fish/completions/$(COMMAND).fish"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/zsh/site-functions/_$(COMMAND)"



clean:
	-rm -f passcheck.info.gz *.install passcheck.*sh-completion



.PHONY: all cmd doc info shell bash fish zsh install uninstall clean

