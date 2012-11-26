from DataHandler import DataHandler
import csv, copy, codecs

class preProcessor:
  def __init__(self, dataFile, userJoins, activeForums):
    self.dataHandler = DataHandler(dataFile, userJoins)
    self.dataHandler.loadActiveForums(activeForums)
    self.tokenizedData =[]
  
  def prepareTokenizedCSV(self):
    self.tokenizedData = self.dataHandler.getTokenizedCSV()
  
  def prepareTokenizedUserMonthCSV(self):
    self.tokenizedData = self.dataHandler.getTokenizedUserMonthCSV()
  
  def prepareTokenizedUserMonthForumCSV(self):
    self.tokenizedData = self.dataHandler.getTokenizedUserMonthForumCSV()
  
  def printDataForTMT(self, outFile):
    outFile = csv.writer(open(outFile,'w'))
    index = 1
    for record in self.tokenizedData:
      record.insert(0,index)
      outFile.writerow(record)
      index += 1
  
  def getRequiredDataFromRecord(self, record):
    indices = [0,]

  def initializeUserMonthRecord(self, user, month):
    return self.dataHandler.getBasicUserMonthRecord(user, month)

  def isProperUnicode(self, text):
    try:
      dummy = unicode(text)
      return True
    except:
      return False

  def printInferDataForTMT(self, outFile):
    f = codecs.open(outFile, encoding='utf-8', mode='w+')
    outFile = csv.writer(f)
    index = 1
    for user in self.tokenizedData.iterkeys():
      for month in self.tokenizedData[user].iterkeys():
        numPosts = 0
        userMonthRecord = self.initializeUserMonthRecord(user, month)
        for recordText in self.tokenizedData[user][month]:
          if self.isProperUnicode(recordText):
            userMonthRecord[-1].append(recordText)
            numPosts += 1
        userMonthRecord[-1] = ' '.join(userMonthRecord[-1])
        userMonthRecord.insert(0, index)
        userMonthRecord.append(numPosts)
        try:
          outFile.writerow([unicode(s).encode("utf-8") for s in userMonthRecord])
          index += 1
        except:
          pass
        
  def printInferDataForTMTWithForum(self, outFile):
    f = codecs.open(outFile, encoding='utf-8', mode='w+')
    outFile = csv.writer(f)
    index = 1
    for user in self.tokenizedData.iterkeys():
      for month in self.tokenizedData[user].iterkeys():
        totalPosts = 0
        allForumsRecord  = self.initializeUserMonthRecord(user, month)
        for forum in self.tokenizedData[user][month]:
          numPosts = 0
          userMonthRecord = self.initializeUserMonthRecord(user, month)
          for recordText in self.tokenizedData[user][month][forum]:
            if self.isProperUnicode(recordText):
              userMonthRecord[-1].append(recordText)
              numPosts += 1
          forumPosts = copy.deepcopy(userMonthRecord[-1])
          userMonthRecord[-1] = ' '.join(userMonthRecord[-1])
          userMonthRecord.insert(0, index)
          userMonthRecord.append(numPosts)
          userMonthRecord.append(forum)
          try:
            outFile.writerow([unicode(s).encode("utf-8") for s in userMonthRecord])
            index += 1
            totalPosts += numPosts
            allForumsRecord[-1].extend(forumPosts)
          except:
            pass
        allForumsRecord[-1] = ' '.join(allForumsRecord[-1])
        allForumsRecord.insert(0, index)
        index += 1
        allForumsRecord.append(totalPosts)
        allForumsRecord.append("AllForums")
        outFile.writerow([unicode(s).encode("utf-8") for s in allForumsRecord])
        
if __name__ == '__main__':
  baseDir = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/TopicChange/Data/"
  dataFile = baseDir + "allThreads.csv"
  userJoins = baseDir + "userJoins"
  activeForums = baseDir + "activeForums.csv"
  PP = preProcessor(dataFile, userJoins, activeForums)
  #PP.prepareTokenizedCSV()
  PP.prepareTokenizedUserMonthForumCSV()
  dataForTMT = baseDir+"tmtInputATUserMonthDocsWithForum.csv"
  PP.printInferDataForTMTWithForum(dataForTMT)
