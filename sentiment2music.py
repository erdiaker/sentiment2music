#!/usr/bin/env python

import random
import sys
import fluidsynth
import time
from threading import Thread
from sentiment_analyzer import SentimentAnalyzer

_mod = 12
_instPos = 106 # banjo
_instNeg = 41 # violin
_keysPos = [9, 10] # A, Bb
_keysNeg = [0, 10, 11] # C, Bb, B

_debug = True if len(sys.argv) > 1 and sys.argv[1] == 'debug' else False 

class Sentiment:
  positive = 0
  negative = 1

class Constant:
  major = 1
  natural_minor = 2
  diatonic = 3
  chromatic = 4
  pentatonic = 5

def main():
  # start fluidsynth
  fs = fluidsynth.Synth()
  fs.start()
  sfid = fs.sfload('FluidR3_GM.sf2')
  fs.program_select(0, sfid, 0, 0)

  # set sentiment analyzer and initial sentiment
  global _sa, _sentiment
  _sa = SentimentAnalyzer()
  _sentiment = Sentiment.positive
  setSentimentSettings(_sentiment, fs)

  # start composition thread 
  t = Thread(target=compose, args=(fs,))
  t.daemon = True
  t.start()

  # read sentences from standard input
  # change composition settings wrt. sentiment of each sentence
  print 'Type sentences and press enter to change the mood of the music.'
  print 'Type "exit" to quit.\n'
  print 'So, how was your day?'
  f = sys.stdin
  while True:
    line = f.readline().strip()
    if line == 'exit':
      break

    curSentiment = extractSentiment(line)
    if curSentiment != _sentiment:
      _sentiment = curSentiment
      setSentimentSettings(_sentiment, fs)

  # deallocate fluidsynth resources
  fs.delete()

def extractSentiment(line):
  if _sa.analyze(line) == 'pos':
    return Sentiment.positive
  else:
    return Sentiment.negative

def compose(fs):
  while True:
    mn = pickMidiNote()
    dur = pickDuration()

    fs.noteon(0, mn, 120)
    time.sleep(dur)
    fs.noteoff(0, mn)

def pickMidiNote():
  return random.choice(_midiNotePool)

def pickDuration():
  return random.choice(_durationPool)

def setSentimentSettings(sentiment, fs):
  setInstrument(sentiment, fs)
  setKeyAndScale(sentiment)
  setDurations(sentiment)

def setInstrument(sentiment, fs):
  curInst = _instPos if _sentiment == Sentiment.positive else _instNeg
  fs.program_change(0, curInst)
  if _debug: print '[Debug] Instrument:', curInst

def setKeyAndScale(sentiment):
  if sentiment == Sentiment.positive:
    key = random.choice(_keysPos)
    intervals = generateScaleIntervals(Constant.diatonic, Constant.major) 
    scaleType = 'major'
    octave = 5
  else:
    key = random.choice(_keysNeg)
    intervals = generateScaleIntervals(Constant.diatonic, Constant.natural_minor) 
    scaleType = 'minor'
    octave = 5
  pcs = generateScalePitchClasses(key, intervals)
  global _midiNotePool
  _midiNotePool = generateMidiNotesFromPitchClasses(pcs, octave)
  if _debug: 
    print '[Debug] Key:', key
    print '[Debug] Scale:', scaleType
    print '[Debug] Octave:', octave

def setDurations(sentiment):
  global _durationPool
  if sentiment == Sentiment.positive:
    _durationPool = [0.5]*2 + [0.25]*4 + [0.125]*8
  else:
    _durationPool = [1.0]*1 + [0.5]*2
  if _debug: print '[Debug] Durations:', _durationPool, '\n'

def generateMidiNotesFromPitchClasses(pitchClasses, octave):
  return [getMidiNote(pc, octave) for pc in pitchClasses]

def getMidiNote(pitchClass, octave):
  return octave*12 + pitchClass

def generateScalePitchClasses(key, intervals):
  scale = [key]
  for step in intervals[:-1]:
    if step == 1:
      newPitch = (scale[-1] + 2) % _mod
    elif step == 0:
      newPitch = (scale[-1] + 1) % _mod
    scale.append(newPitch)
  return scale

def generateScaleIntervals(type1, type2):
  intervals = []
  #TODO: complete
  if type1 == Constant.diatonic:
    if type2 == Constant.major:
      intervals =  [1, 1, 0, 1, 1, 1, 0]
    elif type2 == Constant.natural_minor:
      intervals = [1, 0, 1, 1, 0, 1, 1]
  
  return intervals

if __name__ == '__main__':
  main()

