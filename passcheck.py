#!/usr/bin/env python
# 
# passcheck – passphrase strenght evaluator
# 
# Copyright © 2013, 2015  Mattias Andrée (maandree@member.fsf.org)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version, or under the New BSD LICENSE
# as published by the Regents of the University of California.
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
import os


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
    a, b = a.lower(), b.lower()
    if a == b:
        return 0
    L1 = '1234567890'
    L2 = 'qwertyuiop'
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


def search_cmp(haystack, needle):
    haystack = haystack + [10]
    h, n = 0, 0
    too_low = False
    too_high = False
    while True:
        while True:
            hh, nn = haystack[h], needle[n]
            if (hh == 10) or (nn == 10):
                if hh == nn:
                    return 0
                break
            else:
                d = hh - nn
                if d != 0:
                    if d < 0:
                        too_low = True
                        break
                    else:
                        return None if too_low else 1
            h, n = h + 1, n + 1
        h, n = h + haystack[h:].index(10) + 1, 0
        too_low  = too_low  or (hh == 10)
        too_high = too_high or (nn == 10)
        if h == len(haystack):
            return None if (too_low and too_high) else (-1 if too_low else 1)

def pread_full(fd, bs, offset, output):
    got_total = 0
    while got_total < bs:
        got = list(os.pread(fd, bs - got_total, offset + got_total))
        if len(got) == 0:
            break
        got_total += len(got)
        output.extend(got)

def search_file(fd, filesize, passphrase):
    blocksize = 4096
    minimum = 0
    maximum = filesize - 1
    passphrase = passphrase + [10]
    while minimum <= maximum:
        middle = (minimum + maximum) // 2
        middle -= middle % blocksize
        middle_low = None
        continues = 0
        data = []
        while True:
            pread_full(fd, blocksize, middle + continues * blocksize, data)
            if middle_low is None:
                middle_low = 0
                if middle > 0:
                    try:
                        middle_low = data.index(10)
                    except ValueError:
                        middle_low = None
                        continue
            if middle + len(data) >= filesize:
                middle_high = len(data)
            else:
                middle_high = len(data) - 1
                while (middle_high > middle_low) and (data[middle_high] != 10):
                    middle_high -= 1
                if middle_high <= middle_low:
                    continue
            if middle > 0:
                middle_low += 1
            break
        v = search_cmp(data[middle_low : middle_high], passphrase)
        if v is None:
            return False
        elif v < 0:
            minimum = middle + middle_low + 1
        elif v > 0:
            maximum = middle + middle_high
        else:
            return True
    return False


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



waste_ram = ('--waste-ram' in sys.argv[1:]) or ('-w' in sys.argv[1:])
raw = ('--raw' in sys.argv[1:]) or ('-r' in sys.argv[1:])


blacklist_files = []
if waste_ram:
    try:
        with open('blacklist', 'rb') as file:
            blacklist = set(file.read().decode('utf-8', 'replace').split('\n'))
    except FileNotFoundError:
        sys.stderr.write('File "blacklist" from the git branch "large-files" is not present.\n');
        sys.exit(1)
else:
    blacklist = set([])
    fd = os.open('blacklist', os.O_RDONLY)
    blacklist_files.append((fd, os.fstat(fd).st_size))
for directory in ['/usr/share/dict/', '/usr/local/share/dict/']:
    dictionaries = None
    try:
        dictionaries = os.listdir(directory)
    except FileNotFoundError:
        pass
    if dictionaries is not None:
        for dictionary in dictionaries:
            if not os.path.isdir(directory + dictionary):
                with open(directory + dictionary, 'rb') as file:
                    blacklist.update(set(file.read().decode('utf-8', 'replace').split('\n')))


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
    rating = None
    if ''.join([chr(c) for c in passphrase]) in blacklist:
        rating = 0
    else:
        for fd, filesize in blacklist_files:
            if search_file(fd, filesize, passphrase):
                rating = 0
                break
    if rating is None:
        rating = evaluate(passphrase)
    sys.stdout.buffer.write(('%i \033[34m' % rating).encode('utf-8'))
    sys.stdout.buffer.write(bytes(line))
    sys.stdout.buffer.write('\033[00m\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

