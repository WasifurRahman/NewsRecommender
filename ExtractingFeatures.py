import MySQLdb
import nltk
from nltk.book import *
from sklearn import svm
from xml.dom.minidom import parse
import xml.dom.minidom
from bs4 import BeautifulSoup

db = MySQLdb.connect("localhost","root","1105026","ThesisDatabase")
cursor = db.cursor()

keyWordSeparator = "+-+-"
trainPercentage = 1.0
numMostCommonWord = 15
minLenForSignleWordKeyWord = 6
numTestArticle = 10
tagToId = {'NN':1, 'JJ':2,'IN':3,'CC':4,'CD':5,'VB':6,'VBD':7,'VBZ':8,'VBG':9, 'NNP':10,'NNS':11,'OTHER':12}
KEYWORD = 1
NOT_KEYWORD = 0
trainFileIndexLimit = 170;



fileOut = open("testData", "wb")

#feature array
X = []
#value array
y = []
#phrases
phrases=[]
#test Array
testX=[]
testArticle = []
testPhrases=[]
testSingleWords=[]
testNames=[]

def readFileContent(fileName):
	#open up the file and read its content
	
	# Open a file
	fo = open(fileName, "r+")
	fullText =  fo.read()
	
	#tokens = word_tokenize(fullText)
	#print tokens
	return fullText
	
def formatKeyWordFileContent(keyWordsUnFormatted):
	#print type(keyWordsUnFormatted)
	keyWords = keyWordsUnFormatted.split(keyWordSeparator)
	return keyWords
		

def formatTaggedSentence(taggedSentence):

	
	tokens = [(word,tag) for (word,tag) in taggedSentence if word.isalnum()]
	
	#print tokens
	
	#removing all the stopping  words
	stopwords = nltk.corpus.stopwords.words('english')
	tokens = [(word,tag) for (word,tag) in tokens if word.lower() not in stopwords]
	#print len(tokens),tokens
	return tokens


def getAllTheLines(mainTextFileName):
	
	#getting the main content of the file
	mainContent = readFileContent(mainTextFileName)
	#print (mainContent)

	tokens = mainContent.split(".")
	return tokens



def getNumChars(word):
	return len(word)

def getNamedEntities(word):
	words = word.split(" ")
	cnt = 0
	
	for word in words:
		if(word.istitle() or word[0].isupper()):
			cnt += 1;
	return cnt


def getNumUpper(word):
	cnt = 0;
	
	for i in range(len(word)):
		if(word[i].isupper()):
			cnt+=1;
	return cnt

def getMostCommonWords(nltkText):
	fdist = FreqDist(nltkText)
	#print(type(fdist))
	mostCommon  = fdist.most_common(numMostCommonWord)
	print mostCommon
	longWords = [w for (w,count) in mostCommon if len(w)>=minLenForSignleWordKeyWord]
	print longWords
	return longWords


def getKeyWordsSet(keyWordsFileName):
	
	keyWordsUnFormatted = readFileContent(keyWordsFileName)
	keyWords = formatKeyWordFileContent(keyWordsUnFormatted)
	#return keyWords
	return set(keyWords)

def getTagIdForWord(word):

	if tagToId.has_key(word):
		return tagToId[word]
	
	return tagToId['OTHER']
	
def getTagIdOfPhrase(tokens,fromIn,toIn):
	totId = 0
	mult = [29,89,167]
	
	curInd = 0
	
	for tag in [token[1] for token in tokens[fromIn:toIn+1]]:
		totId += getTagIdForWord(tag)*mult[curInd]
		curInd += 1
		
	return totId
	
	
def buildFeatureForAPhrase(tokens,fromIn,toIn,keyWordsSet):
		
	phrase = " ".join(token[0] for token in tokens[fromIn:toIn+1])
	
	numChars = getNumChars(phrase)
	
	numNamedEntities = getNamedEntities(phrase)
	
	numUpperCases = getNumUpper(phrase)
	
	tagIdOfPhrase = getTagIdOfPhrase(tokens,fromIn,toIn)
	 
	#print phrase,tagIdOfPhrase
	X.append([numChars,numNamedEntities,numUpperCases,tagIdOfPhrase])
	if(phrase in keyWordsSet):
		y.append(KEYWORD)
	else:
		y.append(NOT_KEYWORD)
	
	phrases.append(phrase)
			
			
def buildFeatureSetForASentence(tokens,keyWordsSet):

	#now extract features one by one.
	#the plan is to go through one, two, three words at a time and extract various features from them"
	N = len(tokens)
	oneWord=""
	twoWords=""
	threeWords=""
	
	#mostCommonWords = getMostCommonWords(nltkText)
	#print mostCommonWords
	
	for i in range(N):
		oneWord = tokens[i][0]
		buildFeatureForAPhrase(tokens,i,i,keyWordsSet)
		
		if(i < N-1):

			buildFeatureForAPhrase(tokens,i,i+1,keyWordsSet)
			
		if(i < N-2):
			buildFeatureForAPhrase(tokens,i,i+2,keyWordsSet)
		
		
	
def processFile(mainTextFileName,keyWordsFileName):
	

	keyWordsSet = getKeyWordsSet(keyWordsFileName)
	#allCommonWords = getMostCommonWords(mainTextFileName)
	allSentences = getAllTheLines(mainTextFileName)
	
	#if there is no sentence, then just abort it
	if(len(allSentences)==0):
		return
		
	#print tokens
	for sentence in allSentences:
		try:
			#nltkText = nltk.Text(line)
			nltkText = nltk.word_tokenize(sentence)
			taggedSentence =  nltk.pos_tag(nltkText)
			
			#print type(taggedSentence)
			#maintaining the entire sentence structure
			formattedWordList = taggedSentence
			#formattedWordList = formatTaggedSentence(taggedSentence)
			
			#print formattedWordList
						
			#print "\n\n"
			buildFeatureSetForASentence(formattedWordList,keyWordsSet)
		except:
			continue;
	#print type(nltkText)
	
	
	#print keyWordsSet
	
	
	#print X,y
		

def refineKeyWordList(probableKeyWords):
	stopwords = nltk.corpus.stopwords.words('english')
	
	keyWordSet = set(probableKeyWords)
	tobeRemoved=set([])
	#we will check if a phrase is a substrign of other, if not, we will not return it
	for curKey in keyWordSet:
		for otherKey in keyWordSet:
			if(curKey!=otherKey):
				#check if otherKey is a substr of curkey, if so, remove it and vice versa
				if (curKey.find(otherKey) != -1):
					tobeRemoved.add(otherKey)
				elif (otherKey.find(curKey) !=-1):
					tobeRemoved.add(curKey)
	
	finalKeyWordList=[]
	
	for key in keyWordSet:
		if(key not in tobeRemoved and key.lower() not in stopwords and len(key)>=minLenForSignleWordKeyWord):
			finalKeyWordList.append(key)
	
	return finalKeyWordList
		
					
		
	
	
	
def testSVM(clf):
	for i in range(numTestArticle):
		allTheSelectedPhrasesForKeyWord = []
		article = testArticle[i]
		featuresOfArticle = testX[i]
		phrasesOfArticle = testPhrases[i]
		
		ans = clf.predict(featuresOfArticle)
		fileOut.write("Article:\n")
		
		fileOut.write(article)
		fileOut.write("\n\n\nKeywords:\n")
		for j in range(len(ans)):
			if (ans[j] == KEYWORD):
				#fileOut.write(phrasesOfArticle[j]+",")
				allTheSelectedPhrasesForKeyWord.append(phrasesOfArticle[j])
		
		allProbableSingleWords = testSingleWords[i];
		mostProbableSingleWords = getMostCommonWords(allProbableSingleWords)
		allTheSelectedPhrasesForKeyWord.extend(mostProbableSingleWords)
		allProbableNames = testNames[i]
		allTheSelectedPhrasesForKeyWord.extend(allProbableNames)
		refinedKeyWords = refineKeyWordList(allTheSelectedPhrasesForKeyWord)
	
		fileOut.write(','.join(refinedKeyWords))
		
		fileOut.write("\n\n")
def teachSVM():
	print "teaching svm\n"
	clf = svm.SVC()
	trainLen = (int) ( trainPercentage * len(X))
	
	clf.fit(X[:trainLen],y[:trainLen])	
	print "teaching complete\n"
	testSVM(clf)
	'''
	ans = clf.predict(X[trainLen:len(X)])
	for i in range(len(ans)):
		print ans[i],phrases[i+trainLen]
	#print ans
		'''
	
	
def readDatabase():

	# Prepare SQL query to INSERT a record into the database.
	sql = "SELECT * FROM NewsTable where row_id <"+str(3*trainFileIndexLimit)

	# Execute the SQL command
	cursor.execute(sql)
	#print(cursor.rowcount)
	# Fetch all the rows in a list of lists.
	limit = 0;
	count=-1;
	results = cursor.fetchall()
	for row in results:

		#print(count)
		count +=1

		if(count%2 == 1):
			continue



		rowId = row[0]
		newsId = row[1]
		newsURL = row[2]
		titleFileName = row[3]
		keyWordsFileName = row[4]
		mainTextFileName = row[5]

		# Now print fetched result
		'''
		print "rowId=%d,newsId=%s,newsURL=%s,titleFileName=%s,keyWordsFileName=%s,mainTextFileName=%s" % \
		 (rowId,newsId,newsURL,titleFileName,keyWordsFileName,mainTextFileName)
		'''
		
		processFile(mainTextFileName,keyWordsFileName)
		
		limit +=1
		if(limit >trainFileIndexLimit):
			break
		print count," processed\n"
		
	teachSVM()
		#print len(X)    
		#print X[:100],y[:100]
		
def removeHTMLTags(html):
	try:
		#html =urlopen(url).read() 
		soup = BeautifulSoup(html)
		# kill all script and style elements
		for script in soup(["script", "style"]):
		    script.extract()    # rip it out

		# get text
		text = soup.body.get_text()
		text = text.encode('ascii', 'ignore')

		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		# drop blank lines
		text = '\n'.join(chunk for chunk in chunks if chunk)
	except:
		return "-1"

	return text
    


def buildFeatureForATestPhrase(tokens,fromIn,toIn,index):
		
	phrase = " ".join(token[0] for token in tokens[fromIn:toIn+1])
	
	numChars = getNumChars(phrase)
	
	numNamedEntities = getNamedEntities(phrase)
	
	numUpperCases = getNumUpper(phrase)
	
	tagIdOfPhrase = getTagIdOfPhrase(tokens,fromIn,toIn)
	 
	#print phrase,tagIdOfPhrase
	testX[index].append([numChars,numNamedEntities,numUpperCases,tagIdOfPhrase])
	testPhrases[index].append(phrase)
	
	
def buildFeatureSetForATestSentence(tokens,index):

	#now extract features one by one.
	#the plan is to go through one, two, three words at a time and extract various features from them"
	N = len(tokens)
	oneWord=""
	twoWords=""
	threeWords=""
	
	#mostCommonWords = getMostCommonWords(nltkText)
	#print mostCommonWords
	
	for i in range(N):
		#oneWord = tokens[i][0]
		buildFeatureForATestPhrase(tokens,i,i,index)
		
		if(i < N-1):

			buildFeatureForATestPhrase(tokens,i,i+1,index)
			
		if(i < N-2):
			buildFeatureForATestPhrase(tokens,i,i+2,index)
		
#it will also try to find names of organizations and people
def findProbableSingleWords(taggedSentence):
	singleWordKeyWords=[]
	NamesOfPeopleAndOrgs=[]
	stopwords = nltk.corpus.stopwords.words('english')
	N = len(taggedSentence)
	for i in range(N -1):
		curWordWithTag = taggedSentence[i]
		nextWordWithTag = taggedSentence[i+1]
		#the pattern is word,tag
		curWord = curWordWithTag[0]
		curTag = curWordWithTag[1]
		nextWord = nextWordWithTag[0]
		nextTag = nextWordWithTag[1]
		
		if(curWord.lower() in stopwords):
			continue
		
		if(curTag in ['NN','NNP','NNS'] and nextTag in ['VB','VBD','VBG','VBZ']):
			singleWordKeyWords.append(curWord)
		elif(curWord[0].isupper() and nextWord[0].isupper() and nextWord.lower() not in stopwords):
			NamesOfPeopleAndOrgs.append(curWord + " "+ nextWord)
		elif(curWord[0].isupper()):
			NamesOfPeopleAndOrgs.append(curWord)
			
		#catching three words
		
		if(i<N-2):
			nextNextWord = taggedSentence[i+2][0]
			if(curWord[0].isupper() and nextWord[0].isupper() and nextNextWord[0].isupper() and nextWord.lower() not in stopwords and nextNextWord.lower() not in stopwords):
				NamesOfPeopleAndOrgs.append(curWord + " "+ nextWord+" "+nextNextWord)
			

	return singleWordKeyWords,NamesOfPeopleAndOrgs
		
		
def buildFeatureForTestArticle(index, title, description):
 	#print testX
 	#print "\n\n"
 	testX.append([])
 	testPhrases.append([])
 	testSingleWords.append([])
 	testNames.append([])
 	
 	allSentences = description.split(".")
	#print tokens
	for sentence in allSentences:
		
			#nltkText = nltk.Text(line)
			nltkText = nltk.word_tokenize(sentence)
			taggedSentence =  nltk.pos_tag(nltkText)
			#As it seems, we need to find out the single word patterns manually.so we will go through the tagged sentence and look 
			#for patterns like noun + verb and then declare the noun as a keyword
			
			singleWords,names = findProbableSingleWords(taggedSentence)
			testSingleWords[index].extend(singleWords)
			testNames[index].extend(names)
			
			#print type(taggedSentence)
			
			#hust keep the original structure
			#formattedWordList = formatTaggedSentence(taggedSentence)
			formattedWordList = taggedSentence
			#print formattedWordList
						
			#print "\n\n"
			buildFeatureSetForATestSentence(formattedWordList,index)
		
			

def parseNewscredXMLFile():
	
	DOMTree = xml.dom.minidom.parse("articles-by-categories.xml")
	collection = DOMTree.documentElement
	
	articles = collection.getElementsByTagName("article")
	count = 0;
	for article in articles:
		title = article.getElementsByTagName('title')[0]
		description = article.getElementsByTagName('description')[0]
		
		title = removeHTMLTags(title.childNodes[0].data)
		description = removeHTMLTags(description.childNodes[0].data)
		
		testArticle.append(description)
		
		buildFeatureForTestArticle(count,title,description)
		count += 1
		'''if(count == numTestArticle ):
			break
			'''

if __name__ == "__main__":
    
    #deleteTable()
    #createNewTable()
    #main()  
    #nltk.download()
    parseNewscredXMLFile() 
    readDatabase()
    
    
