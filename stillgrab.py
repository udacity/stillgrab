#!/usr/bin/env python
#
# stillgrab - extract the last still from a bunch of movies

import os
import sys
import subprocess

movietypes = ['.mp4']

def ismovie(filename):
  (_, ext) = os.path.splitext(filename)
  return ext in movietypes

def stillname(moviename, extension='.jpg'):
  '''Make a filename for a still, based on a movie filename.'''
  (basename, _) = os.path.splitext(moviename)
  return basename + extension

def extract(moviepath, stillpath):
  '''Run avconv on a movie, extracting last frame into a still.'''
  cmdline = ['avconv', '-noaccurate_seek', '-ss', '999999', '-i', moviepath,
             '-frames', '1', stillpath]
  print cmdline
  ps = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ret = ps.wait()
  if ret != 0:
    print "avconv failed!"
    print ps.stdout.read()
    print ps.stderr.read()
    sys.exit(1)

def checkavconv():
  '''If avconv isn't installed, bail out.'''
  try:
    ret = subprocess.call(['avconv', '-version'], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
  except OSError:
    print 'avconv is not installed or not in your PATH.'
    sys.exit(1)
  if ret != 0:
    print 'avconv is installed but broken.'
    sys.exit(1)

def extractall(directory):
  '''Extract a still for each movie in directory.'''
  movies = filter(ismovie, os.listdir(directory))
  for fname in movies:
    moviepath = os.path.join(directory, fname)
    sname = stillname(fname)
    stillpath = os.path.join(directory, sname)
    if os.path.exists(stillpath):
      print "%s exists; skipping." % sname
      continue
    print fname,
    extract(moviepath, stillpath)
    print sname

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'Usage:  stillgrab.py directory'
    sys.exit(1)
  checkavconv()
  extractall(sys.argv[-1])

