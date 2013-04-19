#!/usr/bin/env python
"""
svg-objects-export

@link https://gist.github.com/berteh/5416973/

Export SVG elements to other formats (png, pdf, ps, eps, svg), selecting them 
based on their ID with regular expressions.

Useful for designing multiple icons in single file, sprite sheets, or multi-page 
documents with Inkscape (or another SVG editor). Easily generate low-resolution 
and high-resolution renders of some of the objects included in various SVG files
... and more. 

This script requires Inkscape (tested with 0.48)

 * This software is release under the terms of FRESH-JUICE-WARE LICENSE
 *
 * Berteh <https://gist.github.com/berteh/> wrote this file. You can do whatever 
 * you want with this stuff. If we meet some day, and you think this stuff is worth 
 * it, you can offer me a nice fresh juice.
 *
 * The author of this work hereby waives all claim of copyright (economic and moral)
 * in this work and immediately places it in the public domain; it may be used, 
 * distorted or destroyed in any manner whatsoever without further attribution or
 * notice to the creator. Constructive feedback is always welcome nevertheless.
"""
import argparse
import sys, os, subprocess
import re

#constants
default_pattern = '^(rect|layer|path|use|g\d|svg|text|tspan)\d'
if (sys.platform == 'win32'): inkscape_prog = 'C:\Progra~1\Inkscape\inkscape.com'
else: inkscape_prog = 'inkscape'

#parse options
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
	description='''Exports objects from an SVG file, based on their ID, to various formats
(PNG, SVG, PS, EPS, PDF).''', 	
	usage="%(prog)s [-h] [-p PATTERN] [options] infiles+",
	epilog='''requirements
	This program requires Inkscape 0.48+ and Python 2.7+

default behaviour:
	The program exports by default all objects with an ID that has not
	been generated automatically by Inkscape.

	If you provide a custom pattern (-p), then exclude (-e) is by default
	turned off.

examples:

  %(prog)s --pattern '^export' in.svg
 	exports all objects with an ID starting with 'export' from in.svg
 	to PNG files in the current directory.

  %(prog)s --silent --force --type eps --destdir vector/  ~/*.svg ~/tmp/*.svg
	exports all objects with an ID that does not ressemble Inkscape
	default IDs, from any SVG file in user's home and tmp directories,
	to ./vector/ directory as EPS files, with no information displayed and
	overwritting existing files

  %(prog)s --exclude --pattern '[0-9]' --extra '--export-dpi 900' in.svg
	exports all objects with an ID containing no digit, from in.svg file,
	as PNG images with a resolution for	rasterization of 900 dpi. As 
	Inkscape uses 90 by default, this results in 10-times bigger images.
''')
parser.add_argument('infiles', nargs='+', 
	help='SVG file(s) to export objects from, wildcards are supported')
parser.add_argument('-p', '--pattern', default=default_pattern, 
	help='pattern (regular expression) to identify which objects to export or exclude from export (depending on --exclude). Default pattern matches most ID generated automatically by Inkscape (in exclude mode).')	
parser.add_argument('-e','--exclude', action='store_true', default=0,
	help='use pattern to determine which objects to exclude from export, instead of include')
parser.add_argument ('-d', '--destdir', default='./',
	help='directory where images are exported to. default is working directory')
parser.add_argument('-s','--silent', action='store_true', default=False,
	help='do not print information to command line')
parser.add_argument('-f','--force', action='store_true', default=False,
	help='do not prevent existing files from being overwritten')
parser.add_argument('-i', '--inkscape', default=inkscape_prog,#  metavar='path_to_inkscape',
	help='path to inkscape command line executable')
parser.add_argument('-t', '--type', default='png', choices=['png', 'ps', 'eps', 'pdf', 'plain-svg'],
	help='export type (and suffix). png by default. See Inkscape --help for supported formats (png, ps, eps, pdf, plain-svg).')
parser.add_argument('-x', '--extra', metavar='Inkscape_Export_Options', default=' ',
	help='Extra options passed through (litterally) to inkscape for export. See Inkscape --help for more.')


## handle arguments
args = parser.parse_args()
if (args.silent):
	run = subprocess.check_output #
else:
	run = subprocess.check_call
# verify inkscape path
try:
	run([args.inkscape, "-V"])	
except Exception:
	print  '''Could not find inkscape command line executable, set --inkscape option accordingly.
It is usually /usr/bin/inkscape in linux and C:\Progra~1\Inkscape\inkscape.com in windows.'''
	sys.exit(2);
# set 'include' mode by default for custom pattern
if (args.exclude == 0):
	args.exclude = (args.pattern == default_pattern)
# fix 'plain-svg' extension
if (args.type == 'plain-svg'): extension = '.plain-svg.svg'
else: extension = args.type
# create destdir if needed
if not os.path.exists(args.destdir):
    os.makedirs(args.destdir)


def message(*msg):
	""" Utility "print" function that handles verbosity level of messages """
	if (not args.silent):
		print ''.join(msg)
	return

## process files
for infile in args.infiles:
	message("exporting from ", infile)
	objects = subprocess.check_output([args.inkscape, "--query-all", infile])
	for obj in objects.splitlines():
		obj = obj.split(',')[0] #keep only ID
		match = re.search(args.pattern, obj)
		if ((args.exclude and (match == None)) or (not args.exclude and (match != None)) ):
			destfile = ''.join([args.destdir, obj, '.', extension])
			command = ''.join([args.inkscape, ' -i ', obj, ' --export-', args.type, ' ', destfile, ' ', args.extra, ' ', infile])			
			run(command, shell=True)
			message('  ', obj, ' to ', destfile)
		