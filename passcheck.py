#!/usr/bin/env python
# 
# passcheck – passphrase strenght evaluater
# 
# Copyright © 2013  Mattias Andrée (maandree@member.fsf.org)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import sys


def evaluate(data):
    rc = 4.5
    return rc // 1


raw = ('--raw' in sys.argv[1:]) or ('-r' in sys.argv[1:])
while True:
    line = []
    try:
        while True:
            c = sys.stdin.buffer.read(1)[0]
            if c == 10:
                break
            line.append(c)
    except:
        break
    passphrase = []
    if raw:
        passphrase = line
    else:
        escape = False
        for c in line:
            if escape:
                if (c == ord('~')) or (ord('a') <= c <= ord('z')) or (ord('A') <= c <= ord('Z')):
                    escape = False
            elif c == ord('\033'):
                escape = True
            else:
                passphrase.append(c)
    rating = evaluate(passphrase)
    sys.stdout.buffer.write(('%i \033[34m' % rating).encode('utf-8'))
    sys.stdout.buffer.write(bytes(line))
    sys.stdout.buffer.write('\033[00m\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

