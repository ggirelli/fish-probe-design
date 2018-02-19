#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# 
# Author: Gabriele Girelli
# Email: gigi.ga90@gmail.com
# Version: 0.0.1
# Date: 180219
# Description: extract all oligos in a given genomic window.
# 
# ------------------------------------------------------------------------------



# DEPENDENCIES =================================================================

import argparse
import os
import sqlite3
import sys

# INPUT ========================================================================

# Add script description
parser = argparse.ArgumentParser(
	description = 'Convert uniqueOligo database to chr-files.'
)

# Add params
parser.add_argument('db', metavar = 'db', type = str, nargs = 1,
	help = 'Sqlite3 database path.')
parser.add_argument('table', metavar = 'table', type = str, nargs = 1,
	help = 'Table name.')
parser.add_argument('chr', metavar = 'chr', type = str, nargs = 1,
	help = 'Chromosome name (e.g., 1, 2, X).')
parser.add_argument('start', metavar = 'start', type = int, nargs = 1,
	help = 'Start coordinate.')
parser.add_argument('stop', metavar = 'stop', type = int, nargs = 1,
	help = 'Stop coordinate.')
parser.add_argument('--outdir', metavar = 'od', type = str, nargs = 1,
	default = ['.'], help = 'Database directory path.')

parser.add_argument('-r', '--rna', action = 'store_const',
	help = """Input database from transcriptome pipeline.
	Uses GSTART as positional column.""",
	const = True, default = False)

# Parse arguments
args = parser.parse_args()

# Retrieve arguments
dbpath = args.db[0]
table = args.table[0]
chrom = args.chr[0]
start = args.start[0]
stop = args.stop[0]
outdir = args.outdir[0]
trans = args.rna

# FUNCTIONS ====================================================================

# RUN ==========================================================================

print('\nExtracting information from unique oligo databases.')
print('Database: ' + dbpath)
print('Table: %s' % (table,))
print('Region: chr%s:%d-%d\n' % (chrom, start, stop,))

# Connect to databases
print(' · Connecting to database...')
conn = sqlite3.connect(dbpath)
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [str(x[0]) for x in (c.fetchall())]
if not table in tables:
	msg = "ERROR: the provided table does not exist."
	msg += " Available tables: %s" % (str(tables))
	sys.exit(msg)

# Create output folder
print(' · Creating output folder...')
outdir = outdir + '/' + table + '/'
if not os.path.exists(outdir):
    os.makedirs(outdir)

# Extracting table per chromosome
print(' · Extracting oligos from region %s:%d-%d...' % (chrom, start, stop))

# Output file path
fpath = "%schr%s_%d_%d.tsv" % (outdir, chrom, start, stop)

# Remove file if it exists
try:
	os.remove(fpath)
except OSError:
	pass

# Open file connection
outf = open(fpath, 'a+')

# Prepare query to get positions
if not trans:
	q = 'SELECT CHR,START,STOP,SEQ,NAME,GC,TM,DG FROM %s ' % (table,)
	q += 'WHERE CHR=? AND START >= ? AND STOP <= ? ORDER BY START'
else:
	q = 'SELECT CHR,GSTART,GSTOP,SEQ,NAME,GC,TM,DG FROM %s ' % (table,)
	q += 'WHERE CHR=? AND GSTART >= ? AND GSTOP <= ? ORDER BY GSTART'

# Run query
outf.write('\t'.join(
	["CHR", "START", "STOP", "SEQ", "NAME", "GC", "TM", "DG"]) + "\n")
for row in c.execute(q, (chrom, start, stop)):
	# Output position
	outf.write('\t'.join([str(i) for i in row]) + '\n')

# Close file connection
outf.close()

# END ==========================================================================

print('\n~ DONE ~\n')

################################################################################
