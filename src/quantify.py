#!/usr/bin/env python

'''
    quantify.py created by Kol Zuo, July 2019
'''

import sys

import numpy as np
import scipy as sci
import matplotlib
import matplotlib.pyplot as plt
import json
import pandas as pd
import librosa
import IPython
import jams
from utils import exportJAM

def quantify(sound_file, alignment_file, phoneme_dict_file):
    y, sr = librosa.load(sound_file, sr=44100)
    # track tempo estimate
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # load files into json format
    with open(alignment_file, 'r') as reader:
    #     lines = reader.readlines()
        lines = json.load(reader)

    # trascript
    transcript = lines['transcript']
    words = lines['words']

    case = 'case'
    fails = [words[i] for i in range(len(words)) if words[i][case] == 'not-found-in-audio']

    # fail_nums / all_nums ratio
    fail_ratio = len(fails) / len(words)
    print("{0:.2%}".format(fail_ratio))   

    phoneme_dict = {}
    # phoneme_dict_file = 'cmudict.txt' 

    with open(phoneme_dict_file, 'r') as reader:
        lines = reader.readlines()

    for line in lines:
        line = line.split()
        phoneme_dict[line[0].lower()] = line[1:]

    start_word = 'start'
    fail_dict = {}
    word_interval = ''
    fail_words = []
    flag = True
    for i in range(len(words)):
        word = words[i]
        case = word['case']
        if case == 'success' and flag:
            continue
        elif case == 'success' and not flag:
            word_interval += '%.2f' % (word['start'])
            flag = True
            fail_dict[word_interval] = fail_words
            word_interval = ''
            fail_words = []
        if case != 'success':
            if flag and not i: # if the first word is not successfully aligned, then the start time will be 'start'
                word_interval += 'start-'
            elif flag and i:
                word_interval += '%.2f' % (words[i - 1]['end']) + '-'
            flag = False
            fail_word = word['word']
            if fail_word in phoneme_dict:
                s = fail_word, phoneme_dict[fail_word]
            else:
                s = fail_word, ['<unk>']
            fail_words += [s]

    # miss alignment statistics
    fail_nums = {}
    for vals in fail_dict.values():
    #     print(vals)
        for val in vals:
            if val[0] not in fail_nums:
                fail_nums[val[0]] = 1
            else:
                fail_nums[val[0]] += 1
    
    # turn the quantification outputs into json file 
    fail_nums = sorted(fail_nums.items(), key=lambda kv: kv[1], reverse=True)
    fail_nums = [dict((f,)) for f in fail_nums]
    fail_dict = [dict((d,)) for d in fail_dict.items()]

    res = {}
    res['tempo'] = tempo
    fail_ratio = "{0:.2%}".format(fail_ratio)
    res['fail_percentage'] = fail_ratio
    res['fail_alignment'] = fail_dict
    res['fail_nums'] = fail_nums
    with open('test.txt', 'w') as file:
        json.dump(res, file)


if __name__ == "__main__":
    sound_file = '../tracks/BN_One/AllForOne.mp3'
    alignment_file = sys.argv[1]
    phoneme_dict_file = sys.argv[2]

    quantify(sound_file, alignment_file, phoneme_dict_file)