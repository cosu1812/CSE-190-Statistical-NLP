#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
from itertools import izip
from itertools import izip_longest
import numpy as np
import math
import codecs
import pickle

class IBM:
    def __init__(self, n=1):
        self.t_params = defaultdict(float)
        self.corpus_pairs = defaultdict()
        self.vocab_e = set()
        self.vocab_f = set()
        self.n = n
        self.q_params = defaultdict(float)

    def find_tparams(self, counts):
        for key in self.t_params:
            e = key[1]
            f = key[0]
            self.t_params[(f, e)] = counts[(e, f)]/ counts[(e,)]
    
    def find_qparams(self, counts):
        for key in self.q_params:
            j = key[0]
            i = key[1]
            l = key[2]
            m = key[3]
            self.q_params[(j, i, l, m)] = float(counts[(j, i, l, m)]/counts[(i, l, m)])
    
    def initialize(self):
        #print ("Initializing parameters...")
        if self.n == 1:
            n = defaultdict(set)
            for e in self.vocab_e:
                for k in self.corpus_pairs:
                    if e in self.corpus_pairs[k][0]:
                        n[e].update(set(self.corpus_pairs[k][1]))
            
            for f in self.vocab_f:
                for e in n:
                    if f in n[e]:
                        self.t_params[(f,e)] = float(1.0/(len(n[e])))
         
        else:
            with open('params.pkl', "rb") as f:
                params = pickle.load(f)
            self.t_params = params 
            for k in self.corpus_pairs:
                e_s = self.corpus_pairs[k][0]
                f_s = self.corpus_pairs[k][1]
                uniform = float(1.0/(len(e_s)))
                for i in xrange(len(f_s)):
                    for j in xrange(len(e_s)):
                        self.q_params[(j, i, len(e_s), len(f_s))] = uniform

    def param_estimation(self, params, T=5):
        #print ("Starting expectation maximization...")
        self.initialize()
        for t in xrange(T):
            #print ("iteration: %d" % (t))
            counts = defaultdict(float)
            for k in xrange(len(self.corpus_pairs)):
                e = self.corpus_pairs[k][0]
                f = self.corpus_pairs[k][1]
                m = len(f)
                l = len(e)
                for i in xrange(m):
                    if self.n == 1:
                        denom = sum([self.t_params[(f[i], e_w)] for e_w in e])                  
                    else:
                        denom = sum([self.t_params[(f[i], e[j])] * self.q_params[j, i, l, m] for j in xrange(l)])
                    for j in xrange(l):
                        if self.n == 1:
                            d = float(self.t_params[(f[i], e[j])]/denom)
                        else:
                            d = float((self.q_params[j, i, l, m] * self.t_params[(f[i], e[j])])/denom)
                            counts[(j, i, l, m)] = counts[(j, i, l, m)] + d
                            counts[(i, l, m)] = counts[(i, l, m)] + d
                        counts[(e[j], f[i])] = counts[(e[j], f[i])] + d
                        counts[(e[j],)] = counts[(e[j],)] + d
                            
            self.find_tparams(counts);
            if self.n == 2:
                self.find_qparams(counts)    
        
        #print ("Pickling parameters...")
        f = open(params, 'wb') 
        if self.n == 1:
            pickle.dump(dict(self.t_params), f, pickle.HIGHEST_PROTOCOL)
        else:
            pickle.dump((dict(self.t_params), dict(self.q_params)), f, pickle.HIGHEST_PROTOCOL)

    def train(self, corpus1, corpus2, params):
        #print ("Reading corpuses...")
        i = 0
        with codecs.open(corpus1,"rb","utf-8") as E, codecs.open(corpus2,"rb","utf-8") as F:
            for e, f in izip(E, F):
                e = e.strip()
                e = "NULL " + e
                e = e.split(" ")
                f = f.strip().split(" ")
                self.corpus_pairs[i] = (e, f)
                self.vocab_e.update(set(e))
                self.vocab_f.update(set(f))
                i += 1
        self.param_estimation(params, 5)
    
    def write_align(self, dev_e, dev_f, params):
        #print ("Getting parameters...")
        with open(params, "rb") as f:
            params = pickle.load(f)
        if self.n == 1:
            self.t_params = params
        else:
            self.t_params = defaultdict(float, params[0])
            self.q_params = defaultdict(float, params[1])
        
        #print ("Reading corpuses and writing alignments...")
        k = 1
        out = open('align.out', 'wb')
        with codecs.open(dev_e,"rb","utf-8") as E, codecs.open(dev_f,"rb","utf-8") as F:
            for e, f in izip(E, F):
                e = e.strip().split(" ")
                f = f.strip().split(" ")
                l = len(e)
                m = len(f)
                for i in xrange(m):
                    if self.n == 1:
                        max = self.t_params[(f[i], 'NULL')]
                    else:
                        max = float(self.t_params[(f[i], 'NULL')] * self.q_params[(0, i, l + 1, m)])
                    max_j = 0 
                    for j in xrange(l):
                        if self.n == 1 and max < self.t_params[(f[i], e[j])]:
                            max = self.t_params[(f[i], e[j])] 
                            max_j = j + 1
                        elif self.n == 2 and max < float(self.t_params[(f[i], e[j])] * self.q_params[(j + 1, i, l + 1, m)]):
                            max = float(self.t_params[(f[i], e[j])] * self.q_params[(j + 1, i, l + 1, m)])
                            max_j = j + 1
                            
                    out.write("%d %d %d\n" % (k, max_j, i + 1))
                k += 1

                
def grow_align(align_fe, align_ef):
    #print ("Getting Alignments...")
    a_fe = defaultdict(list)
    a_ef = defaultdict(list)
    with open(align_fe, "rb") as fe:
        for l in fe:
            l = l.strip().split(" ")
            a_fe[int(l[0])].append((int(l[1]), int(l[2])))

    with open(align_ef, "rb") as ef:
        for l in ef:
            l = l.strip().split(" ")
            a_ef[int(l[0])].append((int(l[2]), int(l[1])))

    #print ("Getting Union and Intersection...")
    union_a = defaultdict(set)
    intersection_a = defaultdict(set)
    
    for i in xrange(1, len(a_fe) + 1):
        union_a[i] = set(a_fe[i]) | set(a_ef[i])
        intersection_a[i] = set(a_fe[i]) & set(a_ef[i])
    
    # keeps track which word is already aligned
    num_aligns = defaultdict()
    for i in xrange(1, len(intersection_a) + 1):
        num_aligns[i] = (set(), set())
        for j in intersection_a[i]:
            num_aligns[i][0].add(j[0])
            num_aligns[i][1].add(j[1])
    
    #print ("Adding Alignments...")
    growth = intersection_a
    
    for x in xrange(1, len(union_a) + 1):
        maybe = []
        for y in union_a[x]:
            if y not in growth[x]:
                # check if source and target words are already aligned
                if (y[0] not in num_aligns[x][0]) or (y[1] not in num_aligns[x][1]):
                    # check if there are neighbors
                    if ((y[0]+1, y[1]+1) in growth[x]) or ((y[0]-1, y[1]-1) in growth[x]) \
                        or ((y[0]+1, y[1]-1) in growth[x]) or ((y[0]-1, y[1]+1) in growth[x]):
                            growth[x].add(y)
                            num_aligns[x][0].add(y[0])
                            num_aligns[x][1].add(y[1])
                    else:
                        maybe.append(y)
        # goes through other word pairs to see if there are still not aligned
        for z in maybe:
            if (z[0] not in num_aligns[x][0]) or (z[1] not in num_aligns[x][1]):
                growth[x].add(y)
                num_aligns[x][0].add(z[0])
                num_aligns[x][1].add(z[1])
    
    #print ("Writing alignments...")
    out = open("g_align.out", "wb")
    for a in xrange(1, len(growth) + 1):
        for b in growth[a]:
            out.write("%d %d %d\n" % (a, b[0], b[1]))
            
if __name__ == "__main__":
    if len(sys.argv) < 2: # Expect exactly one argument: the training data file
        print ("Missing input file(s)\n")
        sys.exit(2)
     
    ibm = IBM(2)
    
    # train IBM model
    #ibm.train(sys.argv[1], sys.argv[2], sys.argv[3])
    
    # write alignments
    #ibm.write_align(sys.argv[1], sys.argv[2], sys.argv[3])
    
    grow_align(sys.argv[1], sys.argv[2])