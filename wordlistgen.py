#!/usr/bin/env python
"""
This script uses the SCOWL word list compiled byKevin Atkinson to
generate an exceedingly simple SQLite database of words. Point the
DIR constant at SCOWL's "final" directory and run this script to
generate "words.db".

SCOWL is available from:
http://wordlist.sourceforge.net/
"""

import os
import re
import random
import sqlite3

DIR = 'final'
LANGUAGES = ('english', 'american')
SETS = ('words',)
SIZE_MIN = 10
SIZE_MAX = 50
FILTER_REGEX = r"^[^']+$"
SUFFICES = ('s', 'es', 'ed', 'd', 'ize', 'izes', 'ized', 'izer', 'izing',
            'er', 'est', 'ing', 'ation', 'ization', 'ly', 'ally')
SAMPLE = 5
OUT_DB = "words.db"

def files():
    for candf in os.listdir(DIR):
        if '.' not in candf and '-' not in candf:
            continue
        base, size = candf.split('.', 1)
        lang, set_ = base.split('-', 1)
        size = int(size)
        if SIZE_MIN <= size <= SIZE_MAX and set_ in SETS and lang in LANGUAGES:
            yield os.path.join(DIR, candf)

def words(fns):
    for fn in fns:
        f = open(fn)
        for l in f:
            w = l.strip()

            # Drop words with special characters for now.
            try:
                w.decode('utf8').encode('ascii')
            except UnicodeError:
                continue

            # Apply grep.
            if re.match(FILTER_REGEX, w):
                yield w

def wordset(words):
    good = set(words)
    bad = set()
    for word in good:
        # Poor man's stemming.
        forbidden = False
        for suffix in SUFFICES:
            if word.endswith(suffix):
                if word[:-len(suffix)] in good or \
                   word[:-len(suffix)] + 'e' in good or \
                   word[:-len(suffix)].endswith('i') and \
                        word[:-len(suffix)-1] +  'y' in good:
                    bad.add(word)
    return good - bad
    
if __name__ == '__main__':
    fns = files()
    s = wordset(words(fns))
    # print random.sample(list(s), SAMPLE)

    conn = sqlite3.Connection(OUT_DB)
    conn.execute('drop table if exists "words"')
    conn.execute('create table "words" (id integer primary key, word text)')
    for w in s:
        w = w.decode('utf8').encode('ascii')
        conn.execute('insert into "words" (word) values (?)', (w,))
    conn.commit()

