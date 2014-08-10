#!/usr/bin/env python

import sys
from sentiment_analyzer import SentimentAnalyzer
from live_composer import LiveComposer, Sentiment
import os

SA_SERIAL_FILE='sentiment_analyzer.pickle'
SOUNDFONT_FILE='fluid-soundfont-3.1/FluidR3_GM.sf2'

def main():
  sa = prepareSentimentAnalyzer() 
  lc = LiveComposer(SOUNDFONT_FILE)
  lc.start()

  print 'Type a sentence and press enter. Music will change according to the perceieved sentiment.'
  print 'Type "exit" to terminate.'
  while True:
    sentence = sys.stdin.readline()
    if sentence.strip().lower() in ['exit', 'quit']:
      break

    sentiment = sa.analyze(sentence)
    if sentiment == 'pos':
      lc.sentiment = Sentiment.POSITIVE
    elif sentiment == 'neg':
      lc.sentiment = Sentiment.NEGATIVE

  # release live composer resources
  lc.close()

def prepareSentimentAnalyzer():
  # import serializer. try cPickle if available.
  try:
    import cPickle as pickle
  except:
    import pickle

  # try loading a previously serialized sentiment analyzer instance, if possible.
  # otherwise, train from scratch.
  try:
    with open(SA_SERIAL_FILE) as f:
      sa = pickle.load(f)
  except (IOError, pickle.PickleError):
    print 'Preparing sentiment analyzer for the first time. Please wait...'
    sa = SentimentAnalyzer()
    sa.train()
    print 'Done.\n'
    with open(SA_SERIAL_FILE, 'w') as f:
      pickle.dump(sa, f)
  return sa

if __name__ == '__main__':
  main()

