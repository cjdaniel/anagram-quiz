#!/usr/bin/env python
# graphs word relationships in sqlite file given on command line

import sys
from os import path
import sqlite3
import networkx
import matplotlib.pyplot as plt

def find_children(word, dbh, level, graph):
	tabs = ( "\t" * level )
	query = """
select \
  child \
from relationships \
where parent = '%s'
	""" % word
	cur = dbh.cursor()
	cur.execute(query)
	graph.add_node(word)
	for row in cur.fetchall():
		print "%s %sparent: %s  child: %s" % (str(level).zfill(2), tabs, word, row[0])
		graph.add_edge(word, row[0])
		find_children(row[0], dbh, level + 1, graph)
		
#} enddef find_children

try:
	sys.argv[1]
except IndexError:
	print "no SQLite file given (arg 1)"

try:
	sys.argv[2]
except IndexError:
	print "no word given (arg 2)"

word = sys.argv[2].strip()
sqlfile = sys.argv[1]

if not path.exists(sqlfile):
        print "SQLite file '%s' does not exist" % sqlfile
        sys.exit(1)

dbh = sqlite3.connect(sqlfile)

#children_query = """
#select \
#  children.word as child \
#from rels \
#  inner join words as parents \
#    on rels.parent = parents.rowid \
#  inner join words as children \
#    on rels.child = children.rowid \
#where parents.word = '%s'
#""" % word
#
#parents_query = """
#select \
#  parents.word as parent \
#from rels \
#  inner join words as parents \
#    on rels.parent = parents.rowid \
#  inner join words as children \
#    on rels.child = children.rowid \
#where children.word = '%s'
#""" % word

graph = networkx.DiGraph()

print "parent word: %s" % word

find_children(word, dbh, 0, graph)

networkx.draw(graph)
plt.show()
