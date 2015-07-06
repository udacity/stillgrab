#!/usr/bin/env python
#
# stillgrab - extract the last still from a bunch of movies

import os
import sys
import subprocess
import argparse
import re

movietypes = ['.mp4']
DEFAULT_FRAME_EXTENSION = '.png'
QUIZ_RE = re.compile("_q_")

def ismovie(filename):
  (_, ext) = os.path.splitext(filename)
  return ext in movietypes

def stillname(moviename, extension=DEFAULT_FRAME_EXTENSION):
  '''Make a filename for a still, based on a movie filename.'''
  (basename, _) = os.path.splitext(moviename)
  return basename + extension

def extract(moviepath, stillpath, ver):
  '''Run avconv on a movie, extracting last frame into a still.'''
  cmdline = ['avconv', '-noaccurate_seek', '-ss', '999999', '-i', moviepath,
             '-frames', '1', stillpath]
  if ver.startswith('0'):
    # Old avconv version, doesn't do accurate seek
    cmdline.remove('-noaccurate_seek')
  ps = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ret = ps.wait()
  if ret != 0:
    print "avconv failed!"
    print ps.stdout.read()
    print ps.stderr.read()
    sys.exit(1)

def checkavconv():
  '''If avconv isn't installed, bail out.  Otherwise, return its version.'''
  try:
    ps = subprocess.Popen(['avconv', '-version'], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    ret = ps.wait()
  except OSError:
    print 'avconv is not installed or not in your PATH.'
    sys.exit(1)
  if ret != 0:
    print 'avconv is installed but broken.'
    sys.exit(1)
  firstline = ps.stdout.readline().strip()
  if not firstline.startswith('avconv '):
    print 'Couldn\'t parse avconv version!'
  return firstline[7:]

def extractall(directory, ver, all, overwrite):
  '''Extract a still for each movie in directory.'''
  movies = filter(ismovie, os.listdir(directory))
  for fname in movies:
    if QUIZ_RE.search(fname) is None and not all:
      print fname, "is not a quiz, and we're not in --all mode. Skipping"
      continue
    moviepath = os.path.join(directory, fname)
    sname = stillname(fname)
    stillpath = os.path.join(directory, sname)
    if os.path.exists(stillpath) and not overwrite:
      print sname,"exists; skipping. Usee --overwrite to overwrite."
      continue
    print fname,
    extract(moviepath, stillpath, ver)
    print sname

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("directory", help="Directory of videos to process")
  parser.add_argument("-a","--all", help="Process all videos, not just quizzes",
                    action="store_true")
  parser.add_argument("-o","--overwrite", help="Overwrite existing framegrabs",
                      action="store_true")
  args = parser.parse_args()
  ver = checkavconv()
  extractall(args.directory, ver, args.all, args.overwrite)
