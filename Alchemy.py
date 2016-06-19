try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    
from bs4 import BeautifulSoup
import json
import MySQLdb
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

db = MySQLdb.connect("localhost","root","1105026","ThesisDatabase")
cursor = db.cursor()
keyWordSeparator = "+-+-"
fileNamingStartIndex = 1

def deleteTable():
    stmt = "SHOW TABLES LIKE 'NewsTable'"
    cursor.execute(stmt)
    result = cursor.fetchone()
    if result:
        # there is a table named "NewsTable"
        print("Table is present already")
        cursor.execute("DROP TABLE IF EXISTS NewsTable ")
   


def createNewTable():
	sql = """\
		    CREATE TABLE NewsTable (\
		    row_id INT NOT NULL AUTO_INCREMENT,\
		    news_id VARCHAR(50) NOT NULL,\
		    newsURL VARCHAR(200) NOT NULL,\
		    titleFileName VARCHAR(50) NOT NULL,\
		    keywordsFileName VARCHAR(50) NOT NULL,\
		    textFileName VARCHAR(50) NOT NULL,\
		    PRIMARY KEY ( row_id )\
		    )"""
	cursor.execute(sql)


def doesRowExist(newsId):
    cursor.execute("SELECT COUNT(*) from NewsTable where news_id ='%s'"% (newsId))
    result=cursor.fetchone()
    if(result[0]==1):
        return True
    return False
        
def insertInDatabase(newsId,url,title,keyWordString,entireText,fileIndex):
   
        
     
    textFileName = "textFiles/text"+ str(fileIndex)
    keyWordFileName = "keywordFiles/keys"+str(fileIndex)
    titleFileName = "titleFiles/keys"+str(fileIndex)
    
    textFile = open(textFileName, "wb")
    keyWordFile= open(keyWordFileName, "wb")
    titleFile= open(titleFileName, "wb")
    
    entireText = entireText.encode('ascii', 'ignore')
    keyWordString= keyWordString.encode('ascii', 'ignore')
    title= title.encode('ascii', 'ignore')
    
    textFile.write(entireText)
    keyWordFile.write(keyWordString)
    titleFile.write(title)
    
    titleFile.close()
    textFile.close()
    keyWordFile.close()
    
    if(doesRowExist(newsId)):
        print("this row has been inserted before")
        return
         
    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO NewsTable(news_id,newsURL,\
         titleFileName, keywordsFileName,textFileName)\
         VALUES('%s','%s', '%s', '%s', '%s')" % \
         (newsId,url,titleFileName,keyWordFileName,textFileName)
    cursor.execute(sql)     
       
         
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
        print("Row inserted "+newsId)
    except:
        # Rollback in case there is any error
        print("Row not inserted")
        db.rollback()
        
        
 
        
 
def writeSampleHTML(entireText,fileNamingStartIndex):

	htmlFileName = "htmlFiles/html"+ str(fileNamingStartIndex)
	


	htmlFile = open(htmlFileName, "wb")


	entireText = entireText.encode('ascii', 'ignore')

	htmlFile.write(entireText)

	htmlFile.close()



#removes all the tags of the news through html and just returns the main content and more things
def parseHTMLofTheNews(url):
	
		

	try:
		html =urlopen(url).read() 
		writeSampleHTML(html)
		
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
   
	
  
def readDatabase():
    
    # Prepare SQL query to INSERT a record into the database.
    sql = "SELECT * FROM NewsTable"
    try:
       # Execute the SQL command
        cursor.execute(sql)
        print(cursor.rowcount)
        '''
        
       # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
           fname = row[0]
           lname = row[1]
           age = row[2]
           sex = row[3]
           income = row[4]
           income1 = row[4]
           # Now print fetched result
           print "fname=%d,lname=%s,age=%s,sex=%s,income=%s,income1=%s" % \
             (fname, lname, age, sex, income,income1 )
             '''
            
    except:
           print "Error: unable to fetch data"


def main():
    

      #json =urlopen("https://gateway-a.watsonplatform.net/calls/data/GetNews? apikey="your won key"&outputMode=json&start=now-1d&end=now&maxResults=15&return=enriched.url.text,enriched.url")
      returnedJson =urlopen("https://gateway-a.watsonplatform.net/calls/data/GetNews?apikey=c4c9edc33ff0c219f9eba3dea28eb8f557cbe4ef&outputMode=json&start=now-10d&end=now&maxResults=15&return=enriched.url.url,enriched.url.keywords,enriched.url.title").read()
      
      print(returnedJson)
      parsed_json = json.loads(returnedJson)
      #fo = open("json.txt", "wb")
    
      #fo.write(returnedJson)
      N = len(parsed_json["result"]["docs"])
      for i in range(N):
      
          newsId = parsed_json["result"]["docs"][i]["id"]
          url = parsed_json["result"]["docs"][i]["source"]["enriched"]["url"]["url"]
          title = parsed_json["result"]["docs"][i]["source"]["enriched"]["url"]["title"]
          allKeyWords = parsed_json["result"]["docs"][i]["source"]["enriched"]["url"]["keywords"]
      
          keyWordString=""
          for index in range(len(allKeyWords)):
             keyWord = allKeyWords[index]
             keyWordString+=keyWord["text"]
             if(index != (len(allKeyWords)-1)):
                 keyWordString+=keyWordSeparator
          #print keyWord["text"]
          #print url
          #print title
          #print keyWordString
          entireText = parseHTMLofTheNews(url)
          
          
      
          if(entireText == "-1"):
              continue
          #print entireText
          fileIndex = 0
          print "Inserting news with id: "+newsId
          insertInDatabase(newsId,url,title,keyWordString,entireText,fileNamingStartIndex + i)
          
         
   
    
if __name__ == "__main__":
    
    #deleteTable()
    #createNewTable()
    main()  
    #readDatabase()  
    


