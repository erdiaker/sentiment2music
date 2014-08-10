#!/usr/bin/env python

import nltk
from nltk.corpus import movie_reviews
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures
from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus.reader import CategorizedPlaintextCorpusReader
import random
from operator import itemgetter

POS_TAG='pos'
NEG_TAG='neg'

class SentimentAnalyzer:
  def __init__(self):
    '''Initialize the sentiment analyzer.'''
    self._splitRatio = 1.0
    self._dbName = 'movie_reviews'
    self._db = None
    self._trainingFiles = {}
    self._testFiles = {}
    self._highInfoWords = set()
    self._highInfoWordLimit = 10000
    self._classifier = None

  def __getstate__(self):
    '''Store state for serialization.'''
    state = self.__dict__.copy()
    state['_db'] = None
    state['_trainingFiles'] = {}
    state['_testFiles'] = {}
    return state

  def __setstate__(self, value):
    '''Restore instance from given state.'''
    self.__dict__ = value

  @property
  def splitRatio(self):
    '''Training set/total data set ratio.'''
    return self._splitRatio

  @splitRatio.setter
  def splitRatio(self, value):
    self._splitRatio = value

  @property
  def db(self):
    '''Database to train on.'''
    if self._db: 
      return self._db
    else:
      return LazyCorpusLoader(
        self._dbName, CategorizedPlaintextCorpusReader,
        r'(?!\.).*\.txt', cat_pattern=r'(neg|pos)/.*',
        encoding='ascii')

  @db.setter
  def db(self, value):
    self._db = value

  def _splitData(self):
    '''Split data for training and testing.'''
    filesPos = set(self.db.fileids(POS_TAG))
    filesNeg = set(self.db.fileids(NEG_TAG))

    testSizePos = int(len(filesPos) * (1 - self.splitRatio))
    self._testFiles[POS_TAG] = set(random.sample(filesPos, testSizePos))
    self._trainingFiles[POS_TAG] = filesPos - self._testFiles[POS_TAG]

    testSizeNeg = int(len(filesNeg) * (1 - self.splitRatio))
    self._testFiles[NEG_TAG] = set(random.sample(filesNeg, testSizeNeg))
    self._trainingFiles[NEG_TAG] = filesNeg - self._testFiles[NEG_TAG]

  def _collectHighInfoWords(self):
    '''Collect high-information words from the data.'''
    wordFreqs = FreqDist()
    condFreqs = ConditionalFreqDist()

    for w in self.db.words(categories=POS_TAG):
      w = w.lower()
      wordFreqs.inc(w)
      condFreqs[POS_TAG].inc(w)

    for w in self.db.words(categories=NEG_TAG):
      w = w.lower()
      wordFreqs.inc(w)
      condFreqs[NEG_TAG].inc(w)

    posCount = condFreqs[POS_TAG].N()
    negCount = condFreqs[NEG_TAG].N()
    totalCount = posCount + negCount

    wordScores = {}
    for w, wordFreq in wordFreqs.iteritems():
      posFreq = condFreqs[POS_TAG][w]
      posScore = BigramAssocMeasures.chi_sq(posFreq, (wordFreq, posCount), totalCount)
      negFreq = condFreqs[NEG_TAG][w]
      negScore = BigramAssocMeasures.chi_sq(negFreq, (wordFreq, posCount), totalCount)
      wordScores[w] = posScore + negScore
      
    sortedWords = [w for w, _ in sorted(wordScores.items(), key=itemgetter(1), reverse=True)]
    self._highInfoWords = set(sortedWords[:self._highInfoWordLimit])

  def _extractFeatures(self, s):
    '''Extract features from the given sentence.'''
    words = [w.lower() for w in word_tokenize(s) if w in self._highInfoWords]
    return {w: True for w in words}

  def _prepareInstances(self, files, tag):
    '''Prepare a list of instances from given files.'''
    instances = []
    for f in files:
      features = self._extractFeatures(self.db.raw(fileids=[f]))
      tagged = (features, tag)
      instances.append(tagged)
    return instances

  def train(self):
    '''Train the classifier.'''
    self._splitData()
    self._collectHighInfoWords()

    instances = self._prepareInstances(self._trainingFiles[POS_TAG], POS_TAG)
    instances += self._prepareInstances(self._trainingFiles[NEG_TAG], NEG_TAG)
    self._classifier = NaiveBayesClassifier.train(instances)

  def analyze(self, s):
    '''Analyze given sentence to extract a sentiment.'''
    feats = self._extractFeatures(s)
    return self._classifier.classify(feats)

  def calculateAccuracy(self):
    '''Calculate the accuracy of the classifier on test instances.'''
    instances = self._prepareInstances(self._testFiles[POS_TAG], POS_TAG)
    instances += self._prepareInstances(self._testFiles[NEG_TAG], NEG_TAG)
    return nltk.classify.accuracy(self._classifier, instances)


def _test():
  sa = SentimentAnalyzer()
  sa.splitRatio = 0.9
  print 'Calculating accuracy with respect to test data. Please wait...'
  sa.train()
  print 'Accuracy:', sa.calculateAccuracy()


if __name__ == '__main__': 
  _test()

