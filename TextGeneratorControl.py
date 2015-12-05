import os
import re
from collections import defaultdict
from random import uniform
import random
import cPickle as pickle
#import pickle

BEGIN_WORD = '$'
DIVIDERS = '.?!;:'
RE_SENTENCE = re.compile(u'[a-z0-9-,:; "\']+[?!.;:]+')
RE_WORD = re.compile(u'[a-z]+|.\'')
lEN_GEN_TEXT = 5000
MIN_SENT_LEN = 5
NAME_OF_MODEL_FILE = 'statistic.data'


def pick_word(next_words):
    sum_freq, freq = 0, 0
    for word, freq in next_words:
        sum_freq += freq
    rand_freq = uniform(0, sum_freq)
    sum_freq = 0
    for word, freq in next_words:
        sum_freq += freq
        if rand_freq < sum_freq:
            return word


class TextGeneratorControl(object):
    def __init__(self):
        self.model = {}
        self.has_model = False

    def load_corpus(self):
        self.words = []
        self.number_of_words = 0
        for author_dir in os.listdir('corpus'):
            for book_file in os.listdir('corpus\\' + author_dir):
                text = open('corpus\\' + author_dir + "\\" + book_file)
                print("-----Loading " + 'corpus\\' + author_dir + "\\" + book_file)
                for line in text:
                    line = line.lower()
                    for sentence in RE_SENTENCE.findall(line):
                        for word in RE_WORD.findall(sentence):
                            if not re.match(u'[0-9-, "\n]+', word):
                                self.words.append(word)
                                self.number_of_words += 1

    def make_triples(self):
        pre_pre_word, pre_word = BEGIN_WORD, BEGIN_WORD
        hundredth_number_of_words = self.number_of_words / 100
        number_of_processed_words = 0;
        self.triples = []
        self.number_of_triples = 0
        for word in self.words:
            number_of_processed_words += 1
            if number_of_processed_words % hundredth_number_of_words == 0:
                print "-----" + str(number_of_processed_words / hundredth_number_of_words) + "% are done"
            self.triples.append((pre_pre_word, pre_word, word))
            self.number_of_triples += 1
            if word in DIVIDERS:
                self.triples.append((pre_word, word, BEGIN_WORD))
                self.number_of_triples += 1
                pre_pre_word, pre_word = BEGIN_WORD, BEGIN_WORD
            else:
                pre_pre_word, pre_word = pre_word, word

    def make_model(self):
        bi, tri = defaultdict(lambda: 0.0), defaultdict(lambda: 0.0)
        hundredth_number_of_triples = self.number_of_triples / 100
        number_of_processed_triples = 0;
        for t0, t1, t2 in self.triples:
            bi[t0, t1] += 1
            tri[t0, t1, t2] += 1
            number_of_processed_triples += 1
            if number_of_processed_triples % hundredth_number_of_triples == 0:
                print "-----" + str(number_of_processed_triples / hundredth_number_of_triples) + "% are done"
        for (t0, t1, t2), freq in tri.iteritems():
            if (t0, t1) in self.model:
                self.model[t0, t1].append((t2, freq / bi[t0, t1]))
            else:
                self.model[t0, t1] = [(t2, freq / bi[t0, t1])]

    def save_model(self):
        with open(NAME_OF_MODEL_FILE, 'wb') as outfile:
            pickle.dump(self.model, outfile, pickle.HIGHEST_PROTOCOL)

    def build_stat(self):
        print("-----Loading texts...")
        self.load_corpus()
        print("-----Have loaded texts")
        print("-----Have loaded " + str(self.number_of_words) + "words")
        print("-----Making triples...")
        self.make_triples()
        print("-----Have made triples")
        print("-----Making model...")
        self.make_model()
        print("-----Have made model")
        print("-----Saving model...")
        self.save_model()
        print("-----Have saved model")
        self.hasModel = True

    def generate_sentence(self):
        phrase = ''
        t0, t1 = '$', '$'
        while 1:
            t0, t1 = t1, pick_word(self.model[t0, t1])
            if t1 == '$': break
            if t1 in (DIVIDERS) or t0 == '$':
                phrase += t1
            else:
                phrase += ' ' + t1
        phrase += ' '
        return phrase.capitalize()

    def gen_text(self):
        print("-----Generating text...")
        file = open("Generated text.txt", "w")
        file.write("        ")
        count_sentences = 0
        paragraph_len = random.randint(5, 15)
        for i in range(lEN_GEN_TEXT):
            cur_str = self.generate_sentence()
            if len(cur_str) >= MIN_SENT_LEN:
                file.write(cur_str)
                count_sentences += 1
                if count_sentences == paragraph_len:
                    file.write("\n        ")
                    count_sentences = 0
                    paragraph_len = random.randint(5, 15)
            else:
                i -= 1
        file.close()
        print("-----Have generated text")

    def does_has_model(self):
        if self.has_model:
            return True
        for item in os.listdir('.'):
            if str(item) == NAME_OF_MODEL_FILE:
                return True
        return False

    def load_model(self):
        print("-----Loading model...")
        with open(NAME_OF_MODEL_FILE, 'rb') as inputfile:
            self.model = pickle.load(inputfile)
        print("-----Have loaded model")


text_gen = TextGeneratorControl()
if not text_gen.does_has_model():
    text_gen.build_stat()
else:
    text_gen.load_model()
text_gen.gen_text()
