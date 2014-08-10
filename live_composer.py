#/usr/bin/env python

from fluidsynth import Synth
from threading import Thread, Lock
import random
import time
import sys

def _makeType(name, *args, **kwargs):
  d = dict([(arg, i) for i, arg in enumerate(args)] + kwargs.items())
  return type(name, (), d)

Instrument = _makeType("Instrument", BANJO=106, VIOLIN=41)
Scale = _makeType("Scale", "MAJOR", "MINOR")
Interval = _makeType("Interval", \
  MAJOR=[1, 1, 0, 1, 1, 1, 0], \
  MINOR=[1, 0, 1, 1, 0, 1, 1])
Constant = _makeType("Constant", MOD=12, OCTAVE=5, \
  SLOW_DURATIONS=[1.0]*1 + [0.5]*2, \
  FAST_DURATIONS=[0.5]*2 + [0.25]*4 + [0.125]*8)
Sentiment = _makeType("Sentiment", POSITIVE="pos", NEGATIVE="neg")


class LiveComposer(Thread):
  '''Music composer and player class.''' 
  def __init__(self, fontFile):  
    '''Initialize live composer.'''
    super(LiveComposer, self).__init__()
    self.daemon = True
    self._lock = Lock()

    self._fs = Synth()
    self._fs.start()
    self._sfid = self._fs.sfload(fontFile)
    self._fs.program_select(0, self._sfid, 0, 0)

    self._midiNotePool = []
    self._durationPool = []
    self._sentiment = None
    self.sentiment = Sentiment.POSITIVE

  @property
  def sentiment(self):
    '''Sentiment of the music.'''
    return self._sentiment

  @sentiment.setter
  def sentiment(self, value):
    if self._sentiment != value:
      with self._lock:
        self._sentiment = value
        self._updateInstrument()
        self._updateKeyAndScale()
        self._updateDurations()

  def close(self):
    '''Deallocate resources.'''
    self._fs.delete()

  def run(self):
    '''Play live composition.'''
    while True:
      self._playNext()

  def _playNext(self):
    '''Play the next note.'''
    with self._lock:
      mn = self._pickMidiNote()
      dur = self._pickDuration()

    self._fs.noteon(0, mn, 120)
    time.sleep(dur)
    self._fs.noteoff(0, mn)

  def _pickMidiNote(self):
    '''Pick next midi note from the pool.'''
    return random.choice(self._midiNotePool)

  def _pickDuration(self):
    '''Pick duration of the next note from the pool.'''
    return random.choice(self._durationPool)

  def _updateInstrument(self):
    '''Update instrument according to current sentiment.'''
    inst = Instrument.BANJO if self.sentiment == Sentiment.POSITIVE else Instrument.VIOLIN
    self._fs.program_change(0, inst)

  def _updateKeyAndScale(self):
    '''Update key and scale according to current sentiment.'''
    intervals = Interval.MAJOR if self.sentiment == Sentiment.POSITIVE else Interval.MINOR
    key = random.randint(0, Constant.MOD)
    pcs = LiveComposer.generatePitchClasses(key, intervals)
    self._midiNotePool = LiveComposer.generateMidiNotesFromPitchClasses(pcs, Constant.OCTAVE)

  def _updateDurations(self):
    '''Update midi note durations according to current sentiment.'''
    if self.sentiment == Sentiment.POSITIVE:
      self._durationPool = Constant.FAST_DURATIONS
    else:
      self._durationPool = Constant.SLOW_DURATIONS

  @staticmethod
  def generateMidiNotesFromPitchClasses(pitchClasses, octave):
    '''Generate a list of midi notes, given pitch classes and an octave.'''
    return [LiveComposer.getMidiNote(pc, octave) for pc in pitchClasses]

  @staticmethod
  def getMidiNote(pitchClass, octave):
    '''Get midi note number, given a pitch class and an octave.'''
    return octave*Constant.MOD + pitchClass

  @staticmethod
  def generatePitchClasses(key, intervals):
    '''Geenerate a list of pitch classes given a key and scale intervals.'''
    scale = [key]
    for step in intervals[:-1]:
      if step == 1:
        newPitch = (scale[-1] + 2) % Constant.MOD
      elif step == 0:
        newPitch = (scale[-1] + 1) % Constant.MOD
      scale.append(newPitch)
    return scale

def _test():
  lc = LiveComposer('fluid-soundfont-3.1/FluidR3_GM.sf2')
  print 'Enter sentiment as "positive" or "negative".'
  print 'Type "exit" to terminate.'
  try:
    lc.start()
    while True:
      sentiment = sys.stdin.readline().strip().lower()
      if sentiment in ['exit', 'quit']:
        break
      elif sentiment in ['positive', 'pos']:
        lc.sentiment = Sentiment.POSITIVE
      elif sentiment in ['negative', 'neg']:
        lc.sentiment = Sentiment.NEGATIVE
  except KeyboardInterrupt:
    pass
  finally:
    lc.close()

if __name__ == '__main__':
  _test()

