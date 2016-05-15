import MySQLdb
import nltk

db = MySQLdb.connect("localhost","root","1105026","ThesisDatabase")
cursor = db.cursor()

keyWordSeparator = "+-+-"

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
		

def formatMainFileContent(mainTextFileName):

	#getting the main content of the file
	mainContent = readFileContent(mainTextFileName)
	#print (mainContent)
	# type(mainContent)
	#separating out all the tokens
	tokens = nltk.tokenize.word_tokenize(mainContent)
	#print len(tokens),tokens
	#print "\n\n\n"
	#removing all the punctutations
	tokens = [w for w in tokens if w.isalnum()]
	#print tokens
	
	#removing all the stopping  words
	stopwords = nltk.corpus.stopwords.words('english')
	tokens = [w for w in tokens if w.lower() not in stopwords]
	#print len(tokens),tokens
	return tokens

def processFile(mainTextFileName,keyWordsFileName):
	
	tokens = formatMainFileContent(mainTextFileName)
	print tokens
	
	nltkText = nltk.Text(tokens)
	print type(nltkText)
	
	
	keyWordsUnFormatted = readFileContent(keyWordsFileName)
	keyWords = formatKeyWordFileContent(keyWordsUnFormatted)
	#print keyWords
	#print(keyWords)
	#print("\n\n")

def readDatabase():
    
    # Prepare SQL query to INSERT a record into the database.
    sql = "SELECT * FROM NewsTable"
    try:
       # Execute the SQL command
        cursor.execute(sql)
        #print(cursor.rowcount)
       # Fetch all the rows in a list of lists.
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
           if(count == 0):  
           
           		processFile(mainTextFileName,keyWordsFileName)
            
    except:
           print "Error: unable to fetch data"



if __name__ == "__main__":
    
    #deleteTable()
    #createNewTable()
    #main()  
    #nltk.download()
    readDatabase()  
    
