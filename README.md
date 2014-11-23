Sentiment2Music
===============

This simple program analyzes the sentiment of sentences typed by the user, and
composes music on-the-fly based on the extracted sentiment.

## Dependencies

* `Python 2.7`
* `NLTK 3.0`, a natural language processing library. [Installation](http://www.nltk.org/install.html).
* `FluidSynth 1.1`, a real-time synthesizer. [Installation](http://www.fluidsynth.org/). Also available via [Homebrew](http://brew.sh/).
* `PyFluidSynth 1.2`, Python wrapper for FluidSynth. [Installation](https://code.google.com/p/pyfluidsynth/). Also available via [pip](https://pypi.python.org/pypi/pip).

## Installation
After installing the dependency tools/libraries mentioned above, clone this
repository into a directory of your choice:

```sh
git clone git@github.com:erdiaker/sentiment2music.git
```

Sentiment analyzer needs some data (~15 MB) to train. Download it by typing the
following in terminal:

```sh
python -m nltk.downloader movie_reviews punkt
```

FluidSynth needs some soundfont files (~145 MB) in order to synthesize sound. Download
it into your installation directory as follows: 

```sh
wget -O - http://ftp.de.debian.org/debian/pool/main/f/fluid-soundfont/fluid-soundfont_3.1.orig.tar.gz | tar -xzf -
```

## Running Sentiment2Music
To start the program, type the following in your installation directory:

```sh
python sentiment2music.py
```

After a few seconds, you should start hearing something. The program will also
prompt you to type a sentence. Do as instructed, and the music will change
according to the sentiment of the sentence. Have fun!

## License
MIT
