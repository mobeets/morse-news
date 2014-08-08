import sys
import math
import struct
import wave
from random import random
from copy import copy
from optparse import OptionParser
from itertools import izip_longest

from unidecode import unidecode

class Morse:
    def __init__(self, message, wpm, goal_wpm=None):
        """
        wpm is int, the words per minute
        goal_wpm is int, the goal wpm (i.e. farnsworth)
        """
        self.units_per_PARIS = 50
        self.message = self.clean_and_translate(message)
        self.wpm = wpm
        self.goal_wpm = goal_wpm if goal_wpm else self.wpm

        self.unit = self.seconds_per_unit(self.wpm)
        self.unit_word = self.seconds_per_unit(self.goal_wpm)
        
        self.delim = ' '
        self.dit = self.unit
        self.dah = 3.0*self.unit

        self.key_pause = 1.0*self.unit
        self.char_pause = 3.0*self.unit
        self.word_pause = 7.0*self.unit_word

        self.message_length_ms = self.seconds_per_message(self.message)
        # print '{0} seconds per unit'.format(self.unit)
        # print '{0} seconds for message'.format(self.message_length_ms)
    
    def clean_and_translate(self, message):
        """
        message is str
        returns ascii version of message translated to dits, dahs, and spaces
        """
        try:
            message = message.decode('ascii')
        except UnicodeDecodeError, e:
            message = unidecode(message)
        return self.translate(message)

    def seconds_per_unit(self, wpm):
        """
        wpm is int
        returns unit length, in seconds
            assumes unit_time = split_time
            "PARIS" + word_pause = 50 units (ms)
        """
        wps = wpm/60.0 # words per second
        mspw = 1000/wps # ms per word
        return (mspw/self.units_per_PARIS)/1000.0 # seconds per unit
    
    def seconds_per_message(self, message):
        """
        message is str
        returns the estimated time in milliseconds to send the message
        """
        wc = len(message.split())
        return wc*self.units_per_PARIS*self.unit
                 
    def translate(self, message):
        # need symbol to signal paragraph boundaries
        lookup = {
            ' ': ' ',
            '!': '-.-.--',
            "'": '.----.',
            '"': '.-..-.',
            '$': '...-..-',
            '#': '......',
            '&': '.-...',
            '(': '-.--.',
            ')': '-.--.-',
            '+': '.-.-.',
            ',': '--..--',
            '-': '-....-',
            '.': '.-.-.-',
            '/': '-..-.',
            '0': '-----',
            '1': '.----',
            '2': '..---',
            '3': '...--',
            '4': '....-',
            '5': '.....',
            '6': '-....',
            '7': '--...',
            '8': '---..',
            '9': '----.',
            ':': '---...',
            ';': '-.-.-.',
            '=': '-...-',
            '?': '..--..',
            '@': '.--.-.',
            'A': '.-',
            'B': '-...',
            'C': '-.-.',
            'D': '-..',
            'E': '.',
            'F': '..-.',
            'G': '--.',
            'H': '....',
            'I': '..',
            'J': '.---',
            'K': '-.-',
            'L': '.-..',
            'M': '--',
            'N': '-.',
            'O': '---',
            'P': '.--.',
            'Q': '--.-',
            'R': '.-.',
            'S': '...',
            'T': '-',
            'U': '..-',
            'V': '...-',
            'W': '.--',
            'X': '-..-',
            'Y': '-.--',
            'Z': '--..',
            '_': '..--.-',
        }
        return ' '.join([lookup.get(c, ' ') for c in message.upper()])
                      
class SoundFile:
    def  __init__(self, dit_length, pitch_varies, sample_rate=44100, frequency=440):
         self.sample_rate = sample_rate
         self.frequency = frequency
         self.pitch_varies = pitch_varies
         self.dit_length = dit_length
         self.signal = ''
         self.samples = []
         self.signal_length = 0

    def add(self, sound, duration):
        self.samples.extend(sound)
        self.signal_length += duration

    def tone(self, duration):
        nsamples = int(float(duration)*self.sample_rate)
        if self.pitch_varies: # each pitch is random moment to moment
            self.frequency = 200 + 100*random()
            if duration == self.dit_length:
                self.frequency += 400
        period = self.sample_rate/float(self.frequency) # in sample points
        n_oscillations = int(math.ceil(float(nsamples)/int(period)))

        omega = 2.0*math.pi/period
        xs = [x*omega for x in range(int(period))]
        ys = [16384*math.sin(x) for i in range(n_oscillations) for x in xs][:nsamples]
        self.add(ys, duration)
    
    def silence(self, duration):
        nsamples = int(float(duration)*self.sample_rate)
        ys = [0]*nsamples
        self.add(ys, duration)

    def write(self, outfile, nchannels=1, sampwidth=2, bufsize=2048):
        def grouper(n, iterable, fillvalue=None):
            """
            e.g. grouper(3, 'ABCDEFG', 'x') == ABC DEF Gxx
            """
            args = [iter(iterable)] * n
            return izip_longest(fillvalue=fillvalue, *args)

        w = wave.open(outfile, 'wb')
        w.setparams((nchannels, sampwidth, self.sample_rate, self.signal_length, 'NONE', 'uncompressed')) # don't bother setting nframes

        for chunk in grouper(bufsize, self.samples):
            frames = ''.join(struct.pack('h', int(sample)) for sample in chunk if sample is not None)
            w.writeframes(frames) # writeframesraw expects the nframes parameter to be set correctly
        w.close()

def create_wav(outfile, message, wpm, wpm_word, pitch_varies, max_time):
    morse = Morse(message, wpm, wpm_word)
    S = SoundFile(morse.dit, pitch_varies)
    for c in morse.message:
        if max_time > 0 and S.signal_length >= max_time and c == ' ':
            break
        elif c == ' ':
            S.silence(morse.word_pause)
        elif c == '.':
            S.tone(morse.dit)
        elif c == '-':
            S.tone(morse.dah)
        S.silence(morse.key_pause)
    S.write(outfile)

def main():
    parser = OptionParser()
    parser.add_option("-i", "--infile", dest="infile", help="message file (.txt)", metavar="FILE")
    parser.add_option("-o", "--outfile", dest="outfile", help="morse file (.wav)", metavar="FILE")
    parser.add_option("-w", "--wpm", dest="wpm", help="words per minute (wpm)", type="int")
    parser.add_option("-g", "--goalwpm", dest="goal_wpm", help="goal words per minute (wpm)", type="int", default=0)
    parser.add_option("-p", "--pitchvar", dest="pitch_var", help="pitch variation [TRUE/FALSE]", action="store_true", default=False)
    parser.add_option("-t", "--maxsecs", dest="max_time_in_seconds", help="maximum allowed .wav length (sec)", type="int")
    (opts, args) = parser.parse_args()

    mandatory_opts = ['infile', 'outfile', 'wpm']
    for m in mandatory_opts:
        if not opts.__dict__[m]:
            print 'Missing mandatory option: {0}'.format(m)
            parser.print_help()
            exit(-1)

    with open(opts.infile) as f:
        create_wav(opts.outfile, f.read(), opts.wpm, opts.goal_wpm, opts.pitch_var, opts.max_time_in_seconds)
    
if __name__ == "__main__":
     main() 
     