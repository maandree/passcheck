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



all: command data doc shell


command: passcheck.install

passcheck.install: passcheck.py
	cp "$<" "$@"
	sed -i "s:'blacklist':'$(PREFIX)$(DATA)/misc/$(PKGNAME).blacklist':g" "$@"


data: blacklist

blacklist: blacklist.lrz
	@printf '\e[0;1;35m%s\e[0m\n' 'Decompression blacklist.lrz, this can take a very long time (over 1 CPU-hour)'
	lrzip -d "$<"


doc: info

info: passcheck.info

%.info: info/%.texinfo
	makeinfo "$<"


shell: bash fish zsh

bash: passcheck.bash-completion
fish: passcheck.fish-completion
zsh: passcheck.zsh-completion

passcheck.auto-completion.install: passcheck.auto-completion
	cp "$<" "$@"
	sed -i 's/^(passcheck$$/($(COMMAND)/' "$@"

passcheck.%sh-completion: passcheck.auto-completion.install
	auto-auto-complete "$*sh" --output "$@" --source "$<"



install: install-cmd install-data install-license install-doc install-shell

install-cmd: passcheck.install
	install -dm755 -- "$(DESTDIR)$(PREFIX)$(BIN)"
	install -m755 passcheck.install -- "$(DESTDIR)$(PREFIX)$(BIN)/$(COMMAND)"

install-data: install-blacklist

install-blacklist: blacklist
	install -dm755 -- "$(DESTDIR)$(PREFIX)$(DATA)/misc"
	install -m644 blacklist -- "$(DESTDIR)$(PREFIX)$(DATA)/misc/$(PKGNAME).blacklist"

install-license:
	install -dm755 -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)"
	install -m644 COPYING LICENSE -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)"

install-doc: install-info

install-info: passcheck.info
	install -dm755 -- "$(DESTDIR)$(PREFIX)$(DATA)/info"
	install -m644 passcheck.info -- "$(DESTDIR)$(PREFIX)$(DATA)/info/$(PKGNAME).info"

install-shell: install-bash install-fish install-zsh

install-bash: passcheck.bash-completion
	install -Dm644 passcheck.bash-completion -- "$(DESTDIR)$(PREFIX)$(DATA)/bash-completion/completions/$(COMMAND)"

install-fish: passcheck.fish-completion
	install -Dm644 passcheck.fish-completion -- "$(DESTDIR)$(PREFIX)$(DATA)/fish/completions/$(COMMAND).fish"

install-zsh: passcheck.zsh-completion
	install -Dm644 passcheck.zsh-completion -- "$(DESTDIR)$(PREFIX)$(DATA)/zsh/site-functions/_$(COMMAND)"



uninstall:
	-rm -- "$(DESTDIR)$(PREFIX)$(BIN)/$(COMMAND)"
	-rm -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)/COPYING"
	-rm -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)/LICENSE"
	-rmdir -- "$(DESTDIR)$(LICENSES)/$(PKGNAME)"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/info/$(PKGNAME).info"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/bash-completion/completions/$(COMMAND)"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/fish/completions/$(COMMAND).fish"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/zsh/site-functions/_$(COMMAND)"
	-rmdir -- "$(DESTDIR)$(PREFIX)$(DATA)/misc"
	-rm -- "$(DESTDIR)$(PREFIX)$(DATA)/misc/$(PKGNAME).blacklist"



clean:
	-rm -f passcheck.info.gz *.install passcheck.*sh-completion



.PHONY: all command data doc info shell bash fish zsh install install-cmd install-data install-blacklist install-license install-doc install-info install-shell install-bash install-fish install-zsh uninstall clean

