#!/usr/bin/env python
# 
# passcheck – passphrase strenght evaluater
# 
# Copyright © 2013  Mattias Andrée (maandree@member.fsf.org)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import sys


def _class(char):
    char = ord(char)
    if ord('0') <= char <= ord('9'):
        return 1
    elif ord('a') <= char <= ord('z'):
        return 2
    elif ord('A') <= char <= ord('Z'):
        return 2.5
    elif char < (1 << 7):
        return 3
    elif char < (1 << 8):
        return 3.5
    elif char < (1 << 10):
        return 4
    elif char < (1 << 14):
        return 5
    elif char < (1 << 16):
        return 6
    elif char < (1 << 18):
        return 7
    elif char < (1 << 22):
        return 8
    elif char < (1 << 26):
        return 9
    else:
        return 10


def distance(a, b):
    if a == b:
        return 0
    L1 = '1234567890'
    L2 = 'wertyuiop'
    L3 = 'asdfghjkl'
    L4 = 'zxcvbnm'
    keys = {}
    for x in range(len(L1)):
        keys[L1[x]] = (x, 0)
    for x in range(len(L2)):
        keys[L2[x]] = (x + 0.5, 1)
    for x in range(len(L3)):
        keys[L3[x]] = (x + 0.75, 2)
    for x in range(len(L4)):
        keys[L4[x]] = (x + 1, 3)
    for c in (a, b):
        if c not in keys:
            return 15
    return ((keys[a][0] - keys[b][0]) ** 2 + (keys[a][1] - keys[b][1]) ** 2) ** 0.5



def evaluate(data):
    rc = 0
    last = None
    data = bytes(data).decode('utf-8', 'replace')
    used = {}
    classes = [0] * 12
    for c in data:
        r = _class(c)
        if c not in used:
            used[c] = 1
        else:
            used[c] += 1
        rc += r ** 2
        rc += 5 / used[c]
        if r >= 4:
            r += 2
        elif r > 3:
            r = 5
        elif r == 3:
            r = 4
        elif r > 2:
            r = 3
        classes[r - 1] += 1
        if last is not None:
            r = distance(c, last)
            rc += r ** 0.5
        last = c
    if rc >= 0:
        rc += 30
    (a, b, c, d) = classes[:4]
    if a + b + c + d == 0:
        rc += 30
    else:
        r = a ** 2 + b ** 2 + c ** 2 + d ** 2
        rc += 30 * len(data) / (r ** 0.5)
    return (rc + 0.5) // 1


blacklist = None
with open('blacklist', 'rb') as file:
    blacklist = set(file.read().decode('utf-8', 'replace').split('\n'))


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
    rating = 0 if ''.join([chr(c) for c in passphrase]) in blacklist else evaluate(passphrase)
    sys.stdout.buffer.write(('%i \033[34m' % rating).encode('utf-8'))
    sys.stdout.buffer.write(bytes(line))
    sys.stdout.buffer.write('\033[00m\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

