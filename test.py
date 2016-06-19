import nltk
from nltk.book import *



if __name__ == "__main__":
    
   name = "my name is Wasif"
   
   #nltkText = nltk.Text(name.split())
   #fdist1 = FreqDist(nltkText)
   #print(type(fdist1))
   #nltk.download()
   
   
   
   words =  nltk.tokenize.word_tokenize(name)
   print  nltk.pos_tag(words)
    
