# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 01:32:33 2019

@author: 63184
this code is modificated from: 苏剑林. (2017, Mar 11). 《【中文分词系列】 8. 更好的新词发现算法 》[Blog post]. Retrieved from https://kexue.fm/archives/4256
不同之处在于step3，作者没把token长度大于n的部分校验每个长度为n的切片进行验证写上去。还有filter1的条件语句逻辑不严谨，进行了改进。
"""

from collections import defaultdict
import numpy as np
import json

def generator(fname):
    with open(fname, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield line

def get_words(fname, token_size=4, appear=5):
    prob_dict={k: 5 ** (k - 1) for k in range(2, token_size + 1)}
    word_dict = defaultdict(int)
    for sen in generator(fname):
        for token_len in range(1, token_size + 1):
            for st in range(len(sen) - (token_len - 1)):
                word_dict[sen[st: st + token_len]] += 1
    word_dict = {k: v for k, v in word_dict.items() if v >= appear}
    print(len(word_dict))
    single_sum = sum([v for k, v in word_dict.items() if len(k) == 1])
    print(single_sum)
    def filter1(word, prob_dict):
        return True if len(word) >= 2 and min([single_sum * word_dict[word] / (word_dict[word[:idx]] * word_dict[word[idx:]]) for idx in range(1, len(word))]) >= prob_dict[len(word)] else False
    word_set = set(k for k, v in word_dict.items() if filter1(k, prob_dict))
    print(len(word_set))
    def sentence2words(sen, token_size, word_set):
        pos = np.array([0] * len(sen))
        #print(pos)
        for token_len in range(2, token_size + 1):
            for st in range(len(sen) - (token_len - 1)):
                if sen[st: st + token_len] in word_set:
                    pos[st + 1: st + token_len] += 1#除了起点st之外，其他的都+1。原因在于，只准切割起点，后面连续的都不切了。
        #print(pos)
        words = [sen[0]]
        for i in range(1, len(sen)):
            if pos[i] == 0:
                words.append(sen[i])
            else:
                words[-1] += sen[i]
        return words
    result = defaultdict(int)
    for sen in generator(fname):
        for word in sentence2words(sen, token_size, word_set):
            result[word] += 1
    print(len(result))
    result = {k: v for k, v in result.items() if v >= appear}
    print(len(result))
    def filter2(word, token_size, word_set):
        if len(word) <= token_size:
            return True if word in word_set else False
        else:
            return True if all([sen[st: st + token_size] in word_set for st in range(len(word) - (token_size - 1))]) else False
    def filter3(word):
        if any([err in word for err in '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM，。、？：；、——-‘’“”《》￥@！（）【】']):
            return False
        else:
            return True
    return {k: v for k, v in result.items() if filter2(k, token_size, word_set) and filter3(k)}

def save_words(path, myDict):
    jsObj = json.dumps(myDict)
    fileObj = open(path, 'w')
    fileObj.write(jsObj)
    fileObj.close()
    print('words have been saved to', path)
    
def load_words(path):
    with open(path) as f:
        myDict = json.load(f)
    return myDict

def main(srcPath, dstPath):
    save_words(dstPath, get_words(srcPath))

if __name__ == '__main__':
    main('icwb2-data/testing/as_test.utf8', 'as_test.json')
    words = load_words('as_test.json')
    for k, v in words.items():
        print(k, v)