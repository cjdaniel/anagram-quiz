#!/usr/bin/env python
#
# Finds anagram relationships between words in a word list
# Words are one-per line in $1

import sys
import random
from os import path
import time
import sqlite3

starting_length = 3
num_rels = 0
last_commit = 0

def sort(word):
	l = list(word)
	l.sort()
	return ''.join(l)
#} enddef sort

def is_child(parent, child):
	sorted_parent = sort(parent)
	sorted_child = sort(child)
	for i in range(len(child) - 1):
		l = list(sorted_child)
		l.pop(i)
		amputee_child = ''.join(l)
		if amputee_child == sorted_parent:
			return True
#} enddef is_child

def is_child_sorted(parent, child):
	sorted_parent = sort(parent)
	sorted_child = child
	for i in range(len(child) - 1):
		l = list(sorted_child)
		l.pop(i)
		amputee_child = ''.join(l)
		if amputee_child == sorted_parent:
			return True
#} enddef is_child_sorted

def find_children(parent, wordlist, level, dbh):
	sorted_parent = sort(parent)
	children = []
	tabs = ( "\t" * level )
	traversed = 0

	for word, wordhash in wordlist.iteritems():
		traversed = traversed + 1
		if len(word) != len(parent) + 1:
			continue
		if is_child(parent, wordhash['sorted']):
			print "%s %sparent:  %s  child: %s  traversed: %s" % (str(level).zfill(2), tabs, parent, word, traversed)
#			dbh.execute('insert into rels (parent, child) values (?, ?)', (wordlist[parent]['rowid'], wordhash['rowid']))
			dbh.execute('insert into relationships (parent, child) values (?, ?)', (parent, word))
			children.append(word)
			global num_rels
			num_rels = num_rels + 1
	
	for child in children:
		if not wordlist[child]['visited']:
			find_children(child, wordlist, level + 1, dbh)
	
	wordlist[parent]['visited'] = True

	global last_commit
	if time.time() - last_commit >= 300:
		dbh.commit()
		last_commit = time.time()
#} enddef find_children


try:
	sys.argv[1]
except IndexError:
	print "no input file given (arg 1)"
	sys.exit(1)
try:
	sys.argv[2]
except IndexError:
	print "no SQLite file given (arg 2)"
	sys.exit(1)

wordlist = sys.argv[1]
sqlfile = sys.argv[2]

if not path.exists(wordlist):
	print "word list file '%s' does not exist" % wordlist
	sys.exit(2)

if not path.exists(sqlfile):
	print "SQLite file '%s' does not exist" % sqlfile
	sys.exit(3)

dbh = sqlite3.connect(sqlfile)

words = {}

# build dictionary of dictionaries from the word list
# - entries are like: 'word': { 'sorted': 'dorw', 'visited': True/False }
with open(wordlist, 'r') as fh:
	for line in fh:
		word = line.strip()
		word_sorted = sort(word)
#		cur = dbh.cursor()
#		try:
#			cur.execute('insert into words (word, sorted) values (?, ?)', (word, word_sorted))
#		except sqlite3.Error, e:
#			print "Error: ", e.args[0]
#		words[word] = { 'sorted': word_sorted, 'visited': False, 'rowid': cur.lastrowid }
		words[word] = { 'sorted': word_sorted, 'visited': False }

#cur = dbh.cursor()
#cur.execute('select count(*) from words')
#print "words inserted: %s" % cur.fetchone()[0]
#print cur.fetchone()[0]

#dbh.commit()


for word, wordhash in words.iteritems():
	if len(word) == starting_length:
		print "\nStarting on new parent: %s" % word
		find_children(word, words, 0, dbh)


print "TOTAL relations found: %s" % num_rels
dbh.commit()
