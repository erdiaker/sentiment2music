#!/usr/bin/env python

import sys
from sentiment_analyzer import SentimentAnalyzer
from live_composer import LiveComposer, Sentiment

def main():
  # prepare sentiment analyzer
  print 'Preparing sentiment analyzer. Please wait...'
  sa = SentimentAnalyzer()
  sa.train()
  print 'Done.\n'
  
  # prepare live composer
  lc = LiveComposer('fluid-soundfont-3.1/FluidR3_GM.sf2')
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

if __name__ == '__main__':
  main()

