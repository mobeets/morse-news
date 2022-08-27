import os
import re
import math
import subprocess
from datetime import datetime
from tempfile import NamedTemporaryFile

import feedparser
from unidecode import unidecode

from .twitter_search import tweets_from_query

OUTDIR = 'media'
N_RSS_TITLES = 10
N_TWEETS = 5
MAX_WAV_SECONDS = 300

def approx_ascii(text):
    return unidecode(str(text))

def article_titles_from_rss(url, n=N_RSS_TITLES):
    print(url)
    content = feedparser.parse(url)
    print(len(content['entries']))
    titles = [item.title for item in content['entries']]
    if n:
        titles = titles[:n]
    return '...'.join(titles)

def query_to_content(query, is_rss, twitter_handle):
    if is_rss:
        content = article_titles_from_rss(query)
    else:
        content = tweets_from_query(twitter_handle, query, N_TWEETS)
    return approx_ascii(content)

class MorseWavTask(object):
    def __init__(self, exec_path, outdir, feed_name, params, content):
        self.exec_path = exec_path
        self.outdir = outdir
        self.feed_name = feed_name
        self.params = params
        self.content = content
        self.wavfile = self.make_wav(params, content)
        self.txtfile = self.make_txt(content, self.wavfile)
        self.item = MorseWavItem(feed_name, params, self.outdir, self.wavfile, self.txtfile)
        self.begin(self.txtfile, self.wavfile, params)

    def begin(self, txtfile, wavfile, params):
        subprocess.Popen(['python', self.exec_path, '-i', txtfile, '-o', wavfile, '-w', str(params.speed), '-g', str(params.goal_speed), '-p' if params.pitch_var else '', '-t', str(MAX_WAV_SECONDS)])

    def make_wav(self, params, content):
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        f = NamedTemporaryFile(suffix='.wav', dir=self.outdir + '/', delete=False)
        f.close()
        return f.name

    def make_txt(self, content, wavfile):
        fname = wavfile.replace('.wav', '.txt')
        with open(fname, 'w') as f:
            f.write(content.encode('utf-8'))
        return fname

    def exec_time_est(self, wc, wpm):
        # magic numbers from empirical tests of run-time
        A = 0.1136
        B = -1.5857
        C = 1.9602
        D = 12.0239
        spw = ((A-D)/(1+(math.pow((wpm/C),B))))+D # seconds per word
        return wc*spw

    def msg(self):
        est = self.exec_time_est(len(self.content.split(' ')), self.item.params.speed)
        mins = int(est / 60)
        secs = int(est % 60)
        return 'Patience! Your .wav may appear to be empty for a few minutes.'.format(mins, secs)

class MorseParamItem(object):
    def __init__(self, speed, goal_speed, pitch_var):
        self.speed = speed
        self.goal_speed = goal_speed
        self.pitch_var = pitch_var

class MorseWavItem(object):
    def __init__(self, feed_name, params, outdir, wav_path, txt_path):
        self.dt = datetime.now()
        self.id = hex(hash(tuple([feed_name, wav_path, self.dt])))[2:]
        self.feed_name = feed_name
        self.outdir = outdir
        self.wav_path = wav_path
        self.txt_path = txt_path
        self.rel_wav_path, self.rel_txt_path = self.rel_paths(self.outdir, self.wav_path, self.txt_path)
        self.params = params

    def rel_paths(self, outdir, wav_path, txt_path):
        return [os.path.join(outdir, os.path.split(fname)[-1]) for fname in [wav_path, txt_path]]

    def print_speed(self):
        goal = '/{0}'.format(self.params.goal_speed) if self.params.goal_speed else ''
        var = '*' if self.params.pitch_var else ''
        return '{0}{1}{2} wpm'.format(self.params.speed, goal, var)

    def print_dt(self):
        return self.dt.strftime('%Y-%m-%d, %H:%M')

    def __str__(self):
        return self.feed_name

