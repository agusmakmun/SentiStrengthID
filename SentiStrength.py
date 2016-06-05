
# coding: utf-8

# In[1]:

import pymongo, requests, json, urllib, re, collections
from pymongo import MongoClient
from collections import OrderedDict

client = MongoClient('mongodb://localhost:27017/')
#mongodb database and collection
db = client.dataset_agnezmo
dbPre = db.preprocessing

class spellCheck:
    #Peter Norvig Spelling Correction Algorithm based on Bayes' Theorem
    #http://norvig.com/spell-correct.html
    def train(self,features):
        model = collections.defaultdict(lambda: 1)
        for f in features:
            model[f] += 1
        return model
    
    def __init__(self):
        self.NWORDS = self.train(self.words(file('id_dict/spellingset.txt').read()))
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
        
    def words(self,text): return re.findall('[a-z]+', text.lower()) 
    
    def edits1(self, word):
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)

    def known_edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.NWORDS)

    def known(self,words): return set(w for w in words if w in self.NWORDS)

    def correct(self, word):
        candidates = self.known([word]) or self.known(self.edits1(word)) or self.known_edits2(word) or [word]
        return max(candidates, key=self.NWORDS.get)

class sentiStrength:
    #Unsupervised SentiStrength Bahasa Indonesia created by Devid Haryalesmana Wahid ~please don't remove it
    #https://github.com/masdevid
    def __init__(self):
        self.__sentiDict = [line.replace('\n','') for line in open('id_dict/sentimentword.txt').read().splitlines()]
        self.__emotDict = [line.replace('\n','') for line in open("id_dict/emoticon.txt").read().splitlines()]
        self.__negatingDict = [line.replace('\n','') for line in open("id_dict/negatingword.txt").read().splitlines()]
        self.__boosterDict = [line.replace('\n','') for line in open("id_dict/boosterword.txt").read().splitlines()]
        self.__idiomDict = [line.replace('\n','') for line in open("id_dict/idiom.txt").read().splitlines()]
        self.__questionDict = [line.replace('\n','') for line in open("id_dict/questionword.txt").read().splitlines()]
        self.__katadasar = [line.replace('\n','') for line in open('id_dict/rootword.txt').read().splitlines()]
        self.p = 0
        self.n = 0
        self.nn = 0
        
    def correctSpelling(self,text):
        sc = spellCheck()
        return sc.correct(text) if text not in self.__katadasar else text #for t in text.split()
    def createBoosterDict(self):
        scores={}
        for line in self.__boosterDict:
            term, score= line.split()
            scores[term] = int(score)
        return scores
    def createSentiDict(self):
        scores={}
        for line in self.__sentiDict:
            term, score= line.split()
            scores[term] = int(score)
        return scores
    def createEmoticonDict(self):
        scores={}
        for line in self.__emotDict:
            term, score= line.split("\t")
            scores[term] = int(score)
        return scores
    def createIdiomDict(self):
        scores={}
        for line in self.__idiomDict:
            term, score= line.split("\t")
            scores[term] = int(score)
        return scores
    def main(self, text):
        sentimen = self.createSentiDict()
        senti_keys = sentimen.keys()
        
        emoticon = self.createEmoticonDict()
        emo_keys = emoticon.keys()
        
        booster = self.createBoosterDict()
        boost_keys = booster.keys()
        
        idiom = self.createIdiomDict()
        idiom_keys = idiom.keys()
        
        neg = -1
        pos = 1
        
        sentence_score =[]
        questionTerm = []
        
        tweet = text.split()
        
        for term in tweet:
            score = 0
            term_index = tweet.index(term)
            #spelling correction (optional) - it slows down processing time
            #term = self.correctSpelling(term)            
            count_term = len(tweet)
            bigram = "{} {}".format(tweet[term_index-1],term)
            #filter indonesian plural form, ex: keren-keren -> keren
            term = re.sub('(\w+)-(\w+)',r'\1',term)
            if term.isalpha():                
                if term in senti_keys:
                    score = sentimen[term]
                    #handle negating words
                    if tweet[term_index-1] in self.__negatingDict:
                        score = -abs(score) if score>0 else abs(score)
                    #handle boosting words
                    if term_index > 0 and term_index < count_term-1:
                        if tweet[term_index-1] in boost_keys:
                            #print tweet[term_index-1], term
                            score += booster[tweet[term_index-1]]
                        elif tweet[term_index+1] in boost_keys:
                            #print term, tweet[term_index+1]
                            score += booster[tweet[term_index+1]]
                   
                    #increase by 1 consecutive term with minimum score 3 in positive term and -3 in negative term
                    if tweet[term_index-1] in senti_keys:
                        if score >= 3:
                            score+=1
                        elif score<= -3:
                            score-=1
                        else:
                            score
                        #print tweet[term_index-1], term, score
                
                #handle idiom
                if bigram in idiom_keys:
                    score = idiom[bigram] 
                #handle question
                if term in self.__questionDict:
                    isQuestion = True
                    questionTerm.append(term)
                    
            else:
                #handle emoticon
                if term.encode('utf-8',errors='ignore') in emoticon.keys():                    
                    score = emoticon[term]
                #check if (?) sign exist
                elif re.search(r'\?',term):
                    isQuestion = True
                    questionTerm.append(term)
                    
                #exclamation mark give minimum +2
                elif re.search('!',term):
                    score = 2
                    
                #more exclamation mark boost preceeding word by 1, ex: good!!!        
                elif re.sub('(\w+)[!]+$',r'\1',term) in senti_keys:
                    #print term
                    score = sentimen[term]
                    if score > 0:
                        score +=1
                    elif score <0:
                        score -=1
                else:
                    score = 0
                    
            #max(positive), max(negative)
            pos= score if score > pos else pos
            neg= score if score < neg else neg
            
            if score <> 0:
                #insert score between term
                term = "{} [{}]".format(term, score)
            sentence_score.append(term)
            
        isQuestion = True if len(questionTerm)>0 else False
        
        if abs(pos) > abs(neg):               
            self.countSentimen("+")
            senti_result = "result: +positive"
        elif abs(pos) < abs(neg) and not isQuestion:
            self.countSentimen("-")
            senti_result = "result: -negative"
            #ignoring negative sentiment in question as neutral
        elif abs(pos) < abs(neg) and isQuestion:
            self.countSentimen("?")
            senti_result = "result: neutral"
        else:
            self.countSentimen("?")
            senti_result = "result: neutral"
        
        result = ' '.join(sentence_score)
        result = "{} [score:{},{}][{}]".format(result,neg, pos, senti_result)
        return result
    def countSentimen(self, res):
        if res=="+":
            self.p+=1
        elif res =="-":
            self.n+=1
        else:
            self.nn+=1
        return
    def getSentimenScore(self):
        return "[Positive:{}] [Negative:{}] [Neutral:{}]".format(self.p,self.n,self.nn)
def main():
    ss = sentiStrength()
    sc = spellCheck()
    tweets = dbPre.find().skip(0).limit(100)
    for t in tweets:
        print ss.main(t['text'])
    print "====================="        
    print ss.getSentimenScore()
    
main()


# In[ ]:



