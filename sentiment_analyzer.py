#!/usr/bin/env python

import nltk

class SentimentAnalyzer:
  def __init__(self):
    self.train()
  
  def train(self):
    db = nltk.corpus.movie_reviews
    filesPos = db.fileids('pos')
    filesNeg = db.fileids('neg')
    instancesPos = [(self.extractFeats(db.words(fileids=[f])), 'pos') for f in filesPos]
    instancesNeg = [(self.extractFeats(db.words(fileids=[f])), 'neg') for f in filesNeg]
    instancesAll = instancesPos + instancesNeg
    self.classifier = nltk.classify.NaiveBayesClassifier.train(instancesAll)

  def analyze(self, s):
    words = s.split()
    feats = self.extractFeats(words)
    return self.classifier.classify(feats)

  def extractFeats(self, words):
    return {w: True for w in words}

