# SentiStrengthID
Sentiment Strength Detection in Bahasa Indonesia. This is unsupervised version of SentiStrength (http://sentistrength.wlv.ac.uk/) in Bahasa Indonesia. 
Core Feature:
 - Sentiment Lookup
 - Negation Word Lookup
 - Booster Word Lookup
 - Emoticon Lookup
 - Idiom Lookup
 - Question Word Lookup
 - Spelling Correction (optional) using Pater Norvig (http://norvig.com/spell-correct.html)
 - Negative emotion ignored in question
 - Exclamation marks count as +2
 - Repeated Punctuation boosts sentiment
Ignored Additional Rule
 - repeated letters more than 2 boosts sentiment score. This rule do not applied due to my own pre-processing rule which removing word's extra character
 - score +2, -2 in word "miss". Do not apply in Bahasa Indonesia.
 
#Warning!
This is work in progress. Experimental for my Master Thesis

