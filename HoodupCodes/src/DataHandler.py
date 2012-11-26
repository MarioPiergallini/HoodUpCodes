import sys, copy, csv, re
from UserSampler import userSampling
from happyfuntokenizing import Tokenizer
from collections import defaultdict as dd
from TimeHandler import TimeHandler

class DataHandler:
  def __init__(self, dataFile, usersData):
    self.__data = []
    self.__vocab = dd(int)
    self.__vocabDocCount = dd(int)
    self.__backGround = {}
    self.__commWiseIndices = {}
    self.__commWiseTimeSplitIndices = {}
    self.__communutyWiseVocab = dd(lambda:dd(int))
    self.__users = set()
    self.__userWiseIndices = {}
    self.__userWiseTimeSplitIndices = {}
    self.__timeWiseUserSplitIndices = dd(lambda:dd(int))
    self._tok = Tokenizer(preserve_case=False)
    self.__userJoins = dd(lambda:-1)
    self.timeHandler = TimeHandler()
    self.sampledUsers = set()
    self.activeForums = {}
    self.activeUsersInForums = dd(set)
    
    ## Processing/dealing with data
    #self.__read(dataFile)
    self.__justRead(dataFile)
    self.__loadUsersJoins(usersData)
    self.__splitUserWise()
    self.__userWiseTimeSplit()
    #self.__timeWiseUserSplit()
    #self.__commWiseTimeSplit()
    
    ## Extra data structures
    self.postingFreq = dd(int)
  
  def printMonthlyDataForUser(self, user, outFile):
    userTimeIndices = self.__userWiseTimeSplitIndices[user]
    for month in userTimeIndices.iterkeys():
      f = csv.writer(open(outFile+"."+str(month),"w"))
      for index in userTimeIndices[month]:
        f.writerow(self.__data[index])
  
  def tokenizeRecord(self, record):
    record = list(copy.deepcopy(record))
    #print record
    try:
      text = record[1]
      tokenizedText = ' '.join(self._tokenize(text))
      record[1] = tokenizedText
      #print tokenizedText
      return record
    except:
      return -1
  
  def getTokenizedCSV(self):
    tokenizedRecords = []
    for index in range(len(self.__data)):
      newRecord = self.tokenizeRecord(self.__data[index])
      if newRecord != -1:
        tokenizedRecords.append(newRecord)
    return tokenizedRecords
 
  def getBasicUserMonthRecord(self, user, month):
    record = []
    record.append(user)
    record.append(month)
    record.append(self.activeForums[user])
    record.append([])
    return record

  def getTokenizedUserMonthCSV(self):
    tokenizedRecords = dd(lambda:dd(list))
    for user in self.__userWiseTimeSplitIndices.iterkeys():
      for month in self.__userWiseTimeSplitIndices[user].iterkeys():
        for index in self.__userWiseTimeSplitIndices[user][month]:
          newRecord = self.tokenizeRecord(self.__data[index])
          if newRecord != -1:
            tokenizedRecords[user][month].append(newRecord[1]) ## Only postBody being given!
    return tokenizedRecords
  
  def getTokenizedUserMonthForumCSV(self):
    tokenizedRecords = dd(lambda:dd(lambda:dd(list)))
    for user in self.__userWiseTimeSplitIndices.iterkeys():
      for month in self.__userWiseTimeSplitIndices[user].iterkeys():
        for index in self.__userWiseTimeSplitIndices[user][month]:
          newRecord = self.tokenizeRecord(self.__data[index])
          if newRecord != -1:
            forum = newRecord[3]
            tokenizedRecords[user][month][forum].append(newRecord[1]) ## Only postBody being given!
    return tokenizedRecords
  
  
  def getPost2Month(self):
    post2Month = {}
    for user in self.__userWiseTimeSplitIndices.iterkeys():
      for month in self.__userWiseTimeSplitIndices[user].iterkeys():
        for index in self.__userWiseTimeSplitIndices[user][month]:
          postId = self.__data[index][0]
          post2Month[postId] = month
    return copy.deepcopy(post2Month)
  
  def getDoc2Post(self):
    doc2Post = {}
    for index in range(len(self.__data)):
      doc2Post[index+1] = self.__data[index][0]
    return copy.deepcopy(doc2Post)
    
  def getPost2User(self):
    post2User = {}
    for user in self.__userWiseIndices.iterkeys():
      for index in self.__userWiseIndices[user]:
        postId = self.__data[index][0]
        post2User[postId] = user
    return copy.deepcopy(post2User)
    
  def getPostingFreq(self):
    self.postingFreq = dd(int)
    for user in self.__userWiseIndices.iterkeys():
      self.postingFreq[len(self.__userWiseIndices[user])-len(self.__userWiseIndices[user])%10] += 1
    return copy.deepcopy(self.postingFreq)
  
  def getCumulativePostingFreq(self):
    sys.stderr.write("Total Users:"+str(len(self.__userWiseIndices))+"\n")    
    self.postingFreq = dd(int)
    for user in self.__userWiseIndices.iterkeys():
      userPosts = len(self.__userWiseIndices[user])-len(self.__userWiseIndices[user])%10
      for num in range(0,userPosts+1,10):
        self.postingFreq[num] += 1
    return copy.deepcopy(self.postingFreq)
  
  def getCutoffPostingFreq(self):
    totalPosts = 0
    cdfFreqPosting = dd(int)
    for user in self.__userWiseIndices.iterkeys():
      userPosts = len(self.__userWiseIndices[user])-len(self.__userWiseIndices[user])%10
      totalPosts += userPosts
      for num in range(0,userPosts+1,10):
        cdfFreqPosting[num] += userPosts
    for num in cdfFreqPosting.iterkeys():
      cdfFreqPosting[num] = round(cdfFreqPosting[num]*100.0/float(totalPosts),2)
    sys.stderr.write("Total Users:"+str(len(self.__userWiseIndices))+"\n")    
    sys.stderr.write("Total Posts:"+str(totalPosts)+"\n")
    return copy.deepcopy(cdfFreqPosting)
  
  def getMonthwisePostingFrequency(self):
    timeWisePostedUsers = dd(int)
    for time in self.__timeWiseUserSplitIndices.iterkeys():
      timeWisePostedUsers[time] = len(self.__timeWiseUserSplitIndices[time])
    return copy.deepcopy(timeWisePostedUsers)
  
  def getMonthwiseBinnedPostingFrequency(self):
    timeWisePostedUsers = dd(int)
    for time in self.__timeWiseUserSplitIndices.iterkeys():
      userWiseIndices = self.__timeWiseUserSplitIndices[time]
      postingFreq = dd(int)
      for user in userWiseIndices.iterkeys():
        userPosts = len(self.__userWiseIndices[user])
        for num in range(0,userPosts+1):
          postingFreq[num] += 1
      timeWisePostedUsers[time] = copy.deepcopy(postingFreq)
    return copy.deepcopy(timeWisePostedUsers)
  
  def getBasicTable(self):
    table = []
    for user in self.__userWiseTimeSplitIndices.iterkeys():
      userSubtable = []
      for month in self.__userWiseTimeSplitIndices[user].iterkeys():
        try:
          activeForum = self.activeForums[user]
          if activeForum == 'NULL':
            continue
          if int(month) >100:
            continue
          content = (user, month, len(self.__userWiseTimeSplitIndices[user][month]), self.activeForums[user])
          userSubtable.append(content)
        except:
          pass
      if len(userSubtable) >= 3:
        table.extend(userSubtable)
    return table
  
  def totalPostsByUsers(self):
    total = 0
    for user in self.__userWiseIndices.iterkeys():
      total += len(self.__userWiseIndices[user])
    return total
  
  def getTopPosterCoverage(self):
    totalPosts = self.totalPostsByUsers()
    postsTillTopN = 0
    
    
  def __loadUsersJoins(self, usersData):
    dataFile = open(usersData)
    for line in dataFile:
      line = line.strip().split('\t')
      self.__userJoins[line[0]] = line[1] ## Correct the indices
    sys.stderr.write("Loaded " + str(len(self.__userJoins)) + " users' joins\n")

  def loadActiveForums(self, activeForums):
    for line in csv.reader(open(activeForums)):
      try:
        self.activeForums[line[0]] = line[1]
        self.activeUsersInForums[line[1]].add(line[0])
      except:
        pass
  
  def __validUserId(self, userId):
    try:
      userId = int(userId)
      assert userId >= 1 and userId <= 45037
      return True
    except:
      return False

  def __splitUserWise(self):
    tempDD = dd(list)
    for index in range(len(self.__data)):
      try:
        user = self.__data[index][5]
      except:
        continue
      if not self.__validUserId(user):
        continue
      tempDD[user].append(index)
    for user in tempDD.iterkeys():
      self.__userWiseIndices[user] = copy.deepcopy(tempDD[user])
    del tempDD

  def __userWiseTimeSplit(self):
    for user in self.__userWiseIndices.iterkeys():
      self.__userWiseTimeSplitIndices[user] = self.divideBasedOnMonths(self.__userWiseIndices[user])
  
  def __timeWiseUserSplit(self):
    for user in self.__userWiseIndices.iterkeys():
      timeDividedUserData = self.divideBasedOnMonths(self.__userWiseIndices[user])
      for time in timeDividedUserData.iterkeys():
        self.__timeWiseUserSplitIndices[time][user] = timeDividedUserData[time]
    return copy.deepcopy(self.__timeWiseUserSplitIndices)
  
  def __commWiseTimeSplit(self):
    for comm in self.__commWiseIndices.iterkeys():
      self.__commWiseTimeSplitIndices[comm] = self.divideBasedOnMonths(self.__commWiseIndices[comm])
  
  def __justRead(self, dataFile):
    dataFile = open(dataFile)
    dataFile.readline()
    csvReader = csv.reader(dataFile, quotechar='"', escapechar="\\")
    for record in csvReader:
      #self.__data.append(tuple(record[1:]))
      self.__data.append(tuple(record))
  
  def __read(self, dataFile):
    dataFile = open(dataFile)
    dataFile.readline()
    csvReader = csv.reader(dataFile, quotechar='"', escapechar="\\")
    index = 0
    tempDD = dd(list)
    for record in csvReader:
      try:
        succ = self.__updateVocab(record)
        if succ:
          self.__data.append(tuple(record))
          tempDD[record[3]].append(index)
          tempDD['AllTalk'].append(index)
          self.__users.add(record[5])
        index += 1
      except:
        pass
    for key, value in tempDD.iteritems():
      if key.find("Talk") >= 0:
        self.__commWiseIndices[key] = value
    sys.stderr.write("Read " + str(index) + " records\n")
    sys.stderr.write("Word types " + str(len(self.__vocab)) + "\n")
    sys.stderr.write("Users: " + str(len(self.__users)) + "\n")
    
  def _tokenize(self, text):
    text = text.strip()
    text = re.sub('[\s\n]+', ' ', text)
    return self._tok.tokenize(text)
  
  def freqVector(self, tokens):
    tempFreqVector = dd(int)
    for token in tokens:
      tempFreqVector[token] += 1
    return tempFreqVector
  
  def __updateVocab(self, record):
    if len(record)!=7:
      return
    comm = record[3]
    if comm.find('Talk') < 0:
      return 0
    text = record[1]
    if text.find("http") >= 0 or text.find("<blockquote>") >= 0:
      return 0
    tokenDict = self.freqVector(self._tokenize(text))
    for word, freq in tokenDict.iteritems():
      self.__vocab[word] += freq
      self.__communutyWiseVocab[comm][word] += freq
      self.__vocabDocCount[word] += 1 
    return 1
    ##print self.__vocab
  
  def preprocessVocab(self, stopWords):
    self.__backGround = {}
    totalVocab = self.__vocab.keys()
    for word in totalVocab:
      freq = self.__vocab[word]
      if freq >= 5 and self.__vocabDocCount[word] >= 50 and word not in stopWords:
        self.__backGround[word] = freq
      else:
        del self.__vocab[word]
    for comm in self.__communutyWiseVocab.iterkeys():
      commVocab = self.__communutyWiseVocab[comm].keys()
      for word in commVocab:
        if word in self.__vocab:
          continue
        del self.__communutyWiseVocab[comm][word]
    sys.stderr.write("Filtered Word types " + str(len(self.__backGround)) + "\n")

  def getAllUsers(self):
    return copy.deepcopy(self.__users)

  def userStats(self, outFile):
    outFile = open(outFile,'w')
    for user in self.__userWiseIndices.iterkeys():
      userDataIndices = self.__userWiseIndices[user]
      timeDividedUserIndices = self.divideBasedOnMonths(userDataIndices)
      outFile.write('\t'.join(map(lambda x:str(x), [user, len(timeDividedUserIndices)]))+'\n')
    outFile.close()

  def getUserDataIndices(self, user):
    userDataIndices = []
    for index in range(len(self.__data)):
      userDataIndices.append(index)
    return copy.deepcopy(userDataIndices)
  
  def divideBasedOnMonths(self, data):
    timeDividedIndices = dd(list)
    for index in data:
      timeDiff  = -1
      try:
        timeDiff = self.__timeDiff(index)
      except:
        continue
      if timeDiff >= 0:
        timeDividedIndices[timeDiff].append(index)
      #else:
      #  print timeDiff
    return copy.deepcopy(timeDividedIndices)
    
  def __timeDiff(self, recordIndex):
    #try:
      #print recordIndex
      record = self.__data[recordIndex]
      postTime = str(record[4])
      user = str(record[5])
      userJoin = self.__userJoins[user]
      return self.timeHandler.diffMonths(postTime, userJoin)
    #except:
    #  return -1
  
  def makeDist(self, data):
    totalWords = 0
    dist = dd(lambda:1)
    for text in data: ## I just expect an array of texts, not the entire records
      tokenDict = self.freqVector(self._tokenize(text))
      for word, freq in tokenDict.iteritems():
        if word in self.__vocab:
          dist[word] += freq
          totalWords += freq
    for word in self.__vocab:
      dist[word] += 0
    totalWords += len(self.__vocab)
    for word in self.__vocab:
      dist[word] /= float(totalWords)
      ##dist[word] = round(-1*self.myLog(dist[word]),2) ## Log transformation!!
    #assert self.isValid(dist)
    return dist

  def isValid(self, dist):
    sumProb = 0
    for x in dist.iterkeys():
      sumProb += dist[x]
    print sumProb
    return True

  def sampleUsers(self):
    US = userSampling(self.__userWiseTimeSplitIndices)
    self.sampledUsers = US.finalizeUsers()
    self.__userWiseTimeSplitIndices = copy.deepcopy(US.userWiseTimeSplitIndices)
    return copy.deepcopy(self.sampledUsers)

  def getUserMonths(self, user):
    months = copy.deepcopy(self.__userWiseTimeSplitIndices[user].keys())
    for i in range(1,4):
      try:
        months.remove(i)
      except:
        pass
    for i in range(25,31):
      try:
        months.remove(i)
      except:
        pass
    return months

  def getUserDataForDivergence(self, user, month):
    return [copy.deepcopy(self.__data[index][1]) for index in self.__userWiseTimeSplitIndices[user][month]]

  def getUserInitialData(self, user):
    data = []
    for month in range(1,4):
      try:
        for index in self.__userWiseTimeSplitIndices[user][month]:
          data.append(self.__data[index][1])
      except:
        pass
    return data

  def getUserMaturedData(self, user):
    data = []
    for month in range(25,31):
      try:
        for index in self.__userWiseTimeSplitIndices[user][month]:
          data.append(self.__data[index][1])
      except:
        pass
    return data

  def getActiveForum(self, userNum):
    return self.activeForums[userNum]

  def getForumInitialData(self, comm):
    #assert comm in self.__commWiseIndices
    data = []
    #for user in self.__users:
    for user in self.activeUsersInForums[comm]:
      for month in range(1,4):
        try:
          for index in self.__userWiseTimeSplitIndices[user][month]:
            data.append(self.__data[index][1])
        except:
          pass
    return data

  def getForumMaturedData(self, comm):
    #assert comm in self.__commWiseIndices
    data = []
    #for user in self.__users:
    for user in self.activeUsersInForums[comm]:
      for month in range(25,31):
        try:
          for index in self.__userWiseTimeSplitIndices[user][month]:
            data.append(self.__data[index][1])
        except:
          pass
    return data
  
if __name__ == '__main__':
  dataFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/Regression/longtermUsersPosts.csv"
  userJoins = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/Regression/userJoins"
  activeForums = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/Regression/usersActiveForums"
  
  
  
