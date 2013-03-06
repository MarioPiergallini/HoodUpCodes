#!/usr/bin/python
from collections import defaultdict as dd
import csv, random, re, copy, codecs, math

class SubsitutionCoder:
  def __init__(self):
    self.posts = []
    self.userwiseThreads = dd(set)
    self.userwisePosts = dd(set) # Stores indices
    self.userStart = dd(lambda:5000)
    self.maxDay = -1
    self.userWeekwisePosts = dd(lambda:dd(list))
    self.userWeekwiseAccusations = dd(lambda:dd(set))
    self.fakeUsers = set() # Stores the postId of the previous fake annotation we did
    self.fakeUsersPosts = {}
    self.postIdMap = {}
    self.nonFakeUsers = set()
    self.twitterLexicon = set()
    self.pkWords = set(["napkin", "pumpkin", "pk", "upkeep"])
    self.kcWords = set(["kc", "backcast", "backcloth", "blackcock", "blackcurrant", "bookcase", "cockchafer", "dickcissel", "kekchi", "kinkcough",
                        "lockchester", "markcourt", "neckcloth", "packcloth", "sackcloth"])
    self.addPlurals(self.pkWords)
    self.pkWords.add("pk's")
    self.ccWords = set()
    self.ckWords = set()
    self.loadLexiconForCC()
    self.loadLexiconForCK()
    self.loadTwitterLexicon("")
    self.addPlurals(self.twitterLexicon)
    self.features = set(["cc", "ck", "bk", "pk", "hk", "oe", "3", "5", "6", "8", "x", 'nword', 'hood', 'bCaret', 'cCaret', 'pCaret', 'hCaret'])
    self.activeForums = {}
    
    self.wordsNotConsideredLater = dd(int)
    self.wordsConsidered = dd(lambda:dd(int))
    self.consideredWordsCount = 0
  
  def createActiveForums(self):
    userPostedForums = dd(lambda:dd(int))
    for post in self.posts:
      user = post[1]
      forum = post[6].split()[0]
      userPostedForums[user][forum] += 1
    for user in userPostedForums.iterkeys():
      actForum = ""
      maxPosts = 0
      for forum, numPosts  in userPostedForums[user].iteritems():
        if numPosts > maxPosts:
          maxPosts = numPosts
          actForum = forum
      self.activeForums[user] = actForum
  
  def loadLexiconForCC(self):
    lexFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    self.ccWords = set()
    for line in open(lexFile):
      line = line.strip().lower()
      if line.find("cc") >= 0:
        self.ccWords.add(line)
  
  def loadLexiconForCK(self):
    lexFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    self.ckWords = set()
    for line in open(lexFile):
      line = line.strip().lower()
      if line.find("ck") >= 0:
        self.ckWords.add(line)
    
  def addPlurals(self, words):
    words2 = copy.deepcopy(words)
    for word in words2:
      words.add(word + "s")
      words.add(word + "z")
      words.add(word + "'s")
      words.add(word + "'z")
  
  def loadTwitterLexicon(self, lexiconFile):
    lexiconFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    for line in open(lexiconFile):
      line = line.strip()#.split('\t')
      self.twitterLexicon.add(line)
      #self.twitterLexicon[line[0]] = int(line[1])
  
  def filterTwitterLexicon(self):
    dummy = 1
  
  def sampleNonFakeUsers(self):
    count = 0
    while count < 100:
      user = random.sample(self.userwisePosts.keys(), 1)[0]
      while user in self.fakeUsers or user in self.nonFakeUsers:
        user = random.sample(self.userwisePosts.keys(), 1)[0]
      self.nonFakeUsers.add(user)
      count += 1
    return 0
  
  def betterSamplingNonFake(self):
    numPosts = self.numPostsByFakeUsers()
    #print numPosts
    mean = self.mean(numPosts)
    #print "Mean:", mean
    stdDev = self.stdDev(numPosts)
    #print "stdDev:", stdDev
    rangePostNums = mean - 0.5 * stdDev, mean + 0.5 * stdDev
    #print "Min,Max range:", rangePostNums
    possibleUsers = filter(lambda x:x not in self.fakeUsers and len(self.userwisePosts[x]) > rangePostNums[0] and len(self.userwisePosts[x]) < rangePostNums[1], self.userwisePosts.keys())
    self.nonFakeUsers = set(random.sample(possibleUsers, 100))
    #print "nonFakes:", self.nonFakeUsers
  
  def stdDev(self, numbers):
    mean = sum(numbers) * 1.0 / len(numbers)
    var = 0
    for num in numbers:
      var += (num - mean) ** 2
    var = var * 1.0 / len(numbers)
    return math.sqrt(var)
  
  def mean(self, numbers):
    return sum(numbers) * 1.0 / len(numbers)
  
  def numPostsByFakeUsers(self):
    numPosts = []
    for user in self.fakeUsers:
      numPosts.append(len(self.userwisePosts[user]))
    return numPosts
    
  def loadData(self, dataFile):
    dataFile = codecs.open(dataFile, encoding='utf8')
    dataFile.readline()
    reader = csv.reader(dataFile, quotechar='"', escapechar="\\")
    postIndex = 0
    for line in reader:
      self.posts.append(line)
      user = line[1]
      self.userwisePosts[user].add(postIndex)
      if int(line[8]) > self.maxDay:
        self.maxDay = int(line[8])
      if self.userStart[user] > int(line[8]):
        self.userStart[user] = int(line[8])
      postIndex += 1

  def makeWeekwise(self):
    for user in self.userwisePosts.iterkeys():
      for postIndex in self.userwisePosts[user]:
        self.userWeekwisePosts[user][(int(self.posts[postIndex][8]) - self.userStart[user]) / 7].append(postIndex)
      
  def loadFakeUsers(self, fakeAnnotation):
    fakeAnnotation = csv.reader(open(fakeAnnotation))
    for line in fakeAnnotation:
      try:
        dummy = int(line[1])
        dummy = int(line[2])
      except:
        continue
      self.fakeUsers[line[1]] = int(line[2])

  def loadFakeAnnotation(self, fakeAnnotation, remainingUsers):
    fakeAnnotation = open(fakeAnnotation)
    fakeAnnotation.readline()
    fakeAnnotation = csv.reader(fakeAnnotation)
    for line in fakeAnnotation:
      user = line[1]
      if user in remainingUsers:
        continue
      self.fakeUsers.add(user)
      userPosts = set()
      posts = self.parsePosts(line[2])
      userPosts = userPosts | posts
      posts = self.parsePosts(line[3])
      userPosts = userPosts | posts
      if len(userPosts) > 0:
        self.fakeUsersPosts[user] = userPosts
  
  def filterUsers(self):
    allUsers = self.userwisePosts.keys()
    for user in allUsers:
      #if user not in self.fakeUsers and user not in self.nonFakeUsers:
      if len(self.userWeekwisePosts[user]) < 5:
        del self.userwisePosts[user]
        del self.userWeekwisePosts[user]
  
  def sanityCheck(self):
    print "Posts:", len(self.posts)
    print "Fake users:", len(self.fakeUsers)
    print "Users from posts DS:", len(self.userwisePosts)
    print "MaxDay:", self.maxDay
    print "Weekwise:", len(self.userWeekwisePosts)
    print "Fake users:", len(self.fakeUsers)
    print "Non-Fake users:", len(self.nonFakeUsers)
    print "Users from Accusation map:", len(self.userWeekwiseAccusations)
    print "postIdMap:", len(self.postIdMap)
    print "Twitter Lexicon:", len(self.twitterLexicon)
    
  def parsePosts(self, postsField):
    posts = set()
    postsField = postsField.strip()
    if postsField.find(",") >= 0:
      for post in postsField.split(","):
        post = post.strip()
        if post != '':
          posts.add(post)
    else:
      if postsField != '':
        posts.add(postsField)
    return posts

  def buildPostIdMap(self):
    for postIndex in range(len(self.posts)):
      postId = self.posts[postIndex][2]
      self.postIdMap[postId] = postIndex

  def makeAccusationsWeekwise(self):
    for user in self.fakeUsers:
      if user not in self.fakeUsersPosts:
        continue
      for postId in self.fakeUsersPosts[user]:
        globalDay = int(self.posts[self.postIdMap[postId]][8])
        userWeek = (globalDay - self.userStart[user]) / 7
        self.userWeekwiseAccusations[user][userWeek].add(postId)

  def printPostingBehavior(self, logFile):
    logFile = open(logFile, 'w')
    #label = 'user\tuserType\tActiveForum\tweek\tnumPosts\tnumAccusations'
    label = 'user\tActiveForum\tweek\tnumPosts\tnumAccusations'
    for feat in self.features:
      label += '\t' + feat + 'Count'
      label += '\t' + feat
      label += '\t' + feat + 'Percent'
      label += '\t' + feat + 'RawPercent'
    label += '\tSubstitutionScore\tSubstitutionComplexity'
    logFile.write(label + '\n')
    for user in self.userWeekwisePosts.iterkeys():
      for week in self.userWeekwisePosts[user].iterkeys():
        ##userType = "Fake"
        ##if user not in self.fakeUsers:
        ##  userType = "Random"
        #toPrint = [user, userType, self.activeForums[user], str(week), str(len(self.userWeekwisePosts[user][week])), str(len(self.userWeekwiseAccusations[user][week]))]
        toPrint = [user, self.activeForums[user], str(week), str(len(self.userWeekwisePosts[user][week])), str(len(self.userWeekwiseAccusations[user][week]))]
        hits, scopes, numWordScopes, simpleGlobal, complexityGlobal = self.calculateFeatures(self.userWeekwisePosts[user][week])
        for feat in self.features:
          toPrint.append(str(hits[feat + 'Count']))
          toPrint.append(str(scopes[feat]))
          try:
              toPrint.append(str(round(hits[feat + 'Count'] * 100.0 / scopes[feat], 2)))    
          except:
              toPrint.append(str(""))
          try:
              toPrint.append(str(round(hits[feat + 'Count'] * 100.0 / numWordScopes[feat], 4)))  
          except:
              toPrint.append(str(""))
    
        toPrint.append(simpleGlobal)
        toPrint.append(complexityGlobal)
        logFile.write('\t'.join(toPrint) + '\n')
    logFile.close()
  
  def calculateFeatures(self, posts):
    Hits = dd(int)
    Scopes = dd(int)
    numWordsScope = dd(int)
    for post in posts:
      numWords = len(self.posts[post][4].split())
      postHits, postScopes = self.scorePostWordIndexing(self.posts[post][4])
      simpleGlobal = self.globalScoreSimple(postHits, postScopes)
      complexityGloabal = self.globalScoreComplexity(postHits, postScopes)
      #postHits = dict(map(lambda x:(x[0], len(x[1])), postHits.items()))
      #postScopes = dict(map(lambda x:(x[0], len(x[1])), postScopes.items()))
      for feat in postScopes.iterkeys():
        Scopes[feat] += len(postScopes[feat])
        Hits[feat + 'Count'] += len(postHits[feat + 'Count'])
        numWordsScope[feat] += numWords
    return Hits, Scopes, numWordsScope, simpleGlobal, complexityGloabal
  
  def preProcess(self, word):
    word = word.replace("$", "s")
    word = word.replace("00", "oo")
    word = re.sub(r'([a-z])0([a-z])', r'\1o\2', word)
    word = re.sub("i+", "i", word)
    return word
  
  def containsDigit(self, word):
    for char in word:
      if ord(char) >= ord('0') and ord(char) <= ord('9'):
        return False
      return True
  
  def notInterested(self, word):
    try:
      dummy = int(word)
      return True
    except:
      pass
    if len(word) <= 1:
      return True
    try:
      if word[:3] == '___' and word[-3:] == '___':
        return True
    except:
      pass
    if word.find("x") < 0 and word.find("ii") < 0 and word.find("^") < 0 and word.find("bk") < 0 and word.find("pk") < 0 \
    and word.find("hk") < 0 and word.find("cc") < 0 and word.find("ck") < 0 and not self.containsDigit(word):
      return True
    return False
  
  def updateScope(self, word, scopeDict, wordIndex):
    if word.find("c") >= 0:
      scopeDict['cCaret'].add(wordIndex)
    if word.find("b") >= 0:
      scopeDict['bk'].add(wordIndex)
      scopeDict['bCaret'].add(wordIndex)
    if word.find("p") >= 0:
      scopeDict['pk'].add(wordIndex)
      scopeDict['pCaret'].add(wordIndex)
    if word.find("h") >= 0:
      scopeDict['hk'].add(wordIndex)
      scopeDict['hCaret'].add(wordIndex)
    if word.find("e") >= 0:
      scopeDict['3'].add(wordIndex)
    if word.find("b") >= 0:
      scopeDict['6'].add(wordIndex)
    if word.find("s") >= 0:
      scopeDict['5'].add(wordIndex)
    if word.find("b") >= 0:
      scopeDict['8'].add(wordIndex)
    if word.find("o") >= 0:
      scopeDict['x'].add(wordIndex)
      scopeDict['oe'].add(wordIndex)
  
  def updateCCScope(self, word, scopeDict, wordIndex):
    if word.find("ck") >= 0 and word in self.twitterLexicon:
      scopeDict['cc'].add(wordIndex)
  
  def updateCKScope(self, word, scopeDict, wordIndex):
    if word.find("cck") < 0 and ((word.find("ck") >= 0 and word not in self.twitterLexicon) or (word.find("c") >= 0 and word.find("ck") < 0 and word in self.twitterLexicon)):
      scopeDict['ck'].add(wordIndex)
  
  def xSub(self, word, counts, scopeDict, wordIndex):
    xIndices = []
    listWord = []
    xFlag = 0
    if word.find('xx') >= 0:
      word = word.replace('xx', 'oo')
      counts['xCount'].add(wordIndex)
      xFlag = 1
    for index in range(len(word)):
      char = word[index]
      listWord.append(char)
      if char == 'x':
        xIndices.append(index)
    for xIndex in xIndices:
      if xIndex == 0:
        listWord[xIndex] = 'o'
        xFlag = 1
        continue
      if listWord[xIndex - 1] not in set(["a", "e", "i", "o", "u"]):
        listWord[xIndex] = 'o'
        xFlag = 1
    if xFlag:
      counts['xCount'].add(wordIndex)
      scopeDict['x'].add(wordIndex)
    word = ''.join(listWord)
    
    return word
  
  def hoodDoubleSub(self, word, counts, wordIndex):
    prevWord = word
    word = re.sub(r'gr[0-9][0-9]v([a-z]+)', r'groov\1', word)
    word = re.sub(r'h[0-9][0-9]d([sz]*)', r'hood\1', word)
    word = re.sub(r'h[0-9][0-9]v([a-z]+)', r'hoov\1', word)
    word = re.sub(r'bl[0-9][0-9]d([sz]+?)', r'blood\1', word)
    if prevWord != word:
      counts['hoodCount'].add(wordIndex)
    return word
  
  def nwordDoubleSub(self, word, counts, wordIndex):
    prevWord = word
    word = re.sub(r'ni[0-9][0-9]a([sz]?)', r'nigga\1', word)
    if prevWord != word:
      counts['nwordCount'].add(wordIndex)
    return word
  
  def updateHoodScope(self, word, scopeDict, wordIndex):
    if re.match(r'hood([sz]+)?', word) != None:
      scopeDict['hood'].add(wordIndex)
    elif re.match(r'hoov[a-z]+', word) != None:
      scopeDict['hood'].add(wordIndex)
    elif re.match(r'blood([sz]+)?', word) != None:
      scopeDict['hood'].add(wordIndex)
    elif re.match(r'groov[a-z]+', word) != None:
      scopeDict['hood'].add(wordIndex)
  
  def updateNwordScope(self, word, scopeDict, wordIndex):
    if re.match(r'nigga([sz]?)', word):
      scopeDict['nword'].add(wordIndex)

  def updateCaretFeats(self, word, counts, scopeDict, wordIndex):
    if word.find("b^") >= 0:
      counts['bCaretCount'].add(wordIndex)
    if word.find("c^") >= 0:
      counts['cCaretCount'].add(wordIndex)
    if word.find("h^") >= 0:
      counts['hCaretCount'].add(wordIndex)
    if word.find("p^") >= 0:
      counts['pCaretCount'].add(wordIndex)
    word = word.replace("^", "")
    return word
  
  def scorePostWordIndexing(self, post):
    counts = dd(set)
    scopeDict = dd(set)
    for index in range(len(post.split())):
      word = post.split()[index]
      actualWord = word
      self.updateScope(word, scopeDict, index) ## Updating the scope before skipping the words
      self.updateCCScope(word, scopeDict, index)
      if word in self.twitterLexicon or self.notInterested(word):
        self.updateCKScope(word, scopeDict, index)
        #print "filtered:", word
        continue
      considered = 0
      #print "un-filtered:", word
      word = self.preProcess(word)
      # ^
      if word.find("^") >= 0:
        word = self.updateCaretFeats(word, counts, scopeDict, index)
        considered = 1
      ## replacing cck with ck
      word = word.replace("cck", "ck")
      word = word.replace("ckk", "ck")
      # bk, pk, hk
      if word.find("bk") >= 0:
        word = word.replace("bk", "b")
        counts['bkCount'].add(index)
        considered = 1
        self.wordsConsidered['bk'][actualWord] += 1
      if word.find("hk") >= 0:
        word = word.replace("hk", "h")
        counts['hkCount'].add(index)
        considered = 1
        self.wordsConsidered['hk'][actualWord] += 1
      if word.find("pk") >= 0 and word not in self.pkWords:
        word = word.replace("pk", "p")
        counts['pkCount'].add(index)
        considered = 1
        self.wordsConsidered['pk'][actualWord] += 1
      # oe
      if word.find(u'\xf8') >= 0:
        word = word.replace(u'\xf8', 'o')
        counts['oeCount'].add(index)
        scopeDict['oe'].add(index)
        considered = 1
        self.wordsConsidered['oe'][actualWord] += 1
      ## Double Digits!
      word = self.hoodDoubleSub(word, counts, index)
      word = self.nwordDoubleSub(word, counts, index)
      ## Single Digits
      if word.find("5") >= 0:
        word = word.replace('5', 's')
        scopeDict['5'].add(index)
        counts['5Count'].add(index)
        self.wordsConsidered['5s'][actualWord] += 1
        considered = 1
      if word.find("3") >= 0:
        word = word.replace('3', 'e')
        counts['3Count'].add(index)
        scopeDict['3'].add(index)
        considered = 1
        self.wordsConsidered['3e'][actualWord] += 1
      if word.find("6") >= 0:
        word = word.replace('6', 'b') # g or b?
        counts['6Count'].add(index)
        scopeDict['6'].add(index)
        considered = 1
        self.wordsConsidered['6b'][actualWord] += 1
      if word.find("8") >= 0:
        word = word.replace('8', 'b')
        scopeDict['8'].add(index)
        counts['8Count'].add(index)
        considered = 1
        self.wordsConsidered['8b'][actualWord] += 1
      # x!
      if word.find('x') >= 0:
        word = self.xSub(word, counts, scopeDict, index)
        self.wordsConsidered['x'][actualWord] += 1
        considered = 1
      #print "word after subsitutions:", word
      # Updating cc scope again!
      self.updateCCScope(word, scopeDict, index)
      self.updateCKScope(word, scopeDict, index)
      self.updateHoodScope(word, scopeDict, index)
      self.updateNwordScope(word, scopeDict, index)
      # cc, ck and kc
      if word.find("ckk") >= 0:
        scopeDict['cc'].add(index)
      if word.find("cck") >= 0:
        scopeDict['cc'].add(index)
        pass
      elif word.find("cc") >= 0 and re.match("n[ui]cca+[sz]?", word) == None and word not in self.ccWords:
        counts['ccCount'].add(index)
        scopeDict['cc'].add(index)
        self.wordsConsidered['cc'][actualWord] += 1
        considered = 1
      elif word.find("ck") >= 0 and re.match("n[ui]cka+[sz]?", word) == None and word not in self.ckWords:
        counts['ckCount'].add(index)
        self.wordsConsidered['ck'][actualWord] += 1
        considered = 1
      if word.find("kc") >= 0 and word not in self.kcWords:
        counts['ccCount'].add(index)
        scopeDict['cc'].add(index)
        considered = 1
        self.wordsConsidered['cc'][actualWord] += 1
      if considered == 0:
        self.wordsNotConsideredLater[actualWord] += 1
      else:
        self.consideredWordsCount += 1
    
    #print scopeDict
    #print counts
    #print post
    #print dict(map(lambda x:(x[0], len(x[1])), counts.items())), dict(map(lambda x:(x[0], len(x[1])), scopeDict.items()))
    #print counts, scopeDict
    #print "Complexity Global Feat:", self.globalScoreComplexity(counts, scopeDict)
    #print "Simple Global Feat:", self.globalScoreSimple(counts, scopeDict)
    return counts, scopeDict

  def scorePost(self, post):
    caretCount = 0
    counts = {'ccCount':0, 'ckCount':0, 'pkCount':0, 'hkCount':0, 'bkCount':0, 'oeCount':0, 'xCount':0, '5Count':0, '3Count':0, '6Count':0, '8Count':0, 'nwordCount':0, 'hoodCount':0}
    scopeDict = {"cc":0, "ck":0, "bk":0, "pk":0, "hk":0, "oe":0, "3":0, "5":0, "6":0, "8":0, "x":0, 'nword':0, 'hood':0}
    for word in post.split():
      self.updateScope(word, scopeDict) ## Updating the scope before skipping the words
      self.updateCCScope(word, scopeDict)
      if word in self.twitterLexicon or self.notInterested(word):
        self.updateCKScope(word, scopeDict)
        #print "filtered:", word
        continue
      #print "un-filtered:", word
      word = self.preProcess(word)
      # ^
      if word.find("^") >= 0:
        word = word.replace("^", "")
        caretCount += 1
      # bk, pk, hk
      if word.find("bk") >= 0:
        word = word.replace("bk", "b")
        counts['bkCount'] += 1
      if word.find("hk") >= 0:
        word = word.replace("hk", "h")
        counts['hkCount'] += 1
      if word.find("pk") >= 0 and word not in self.pkWords:
        word = word.replace("pk", "p")
        counts['pkCount'] += 1
      # oe
      if word.find(u'\xf8') >= 0:
        word = word.replace(u'\xf8', 'o')
        counts['oeCount'] += 1
        scopeDict['oe'] += 1
      ## Double Digits!
      word = self.hoodDoubleSub(word, counts)
      word = self.nwordDoubleSub(word, counts)
      ## Single Digits
      if word.find("5") >= 0:
        word = word.replace('5', 's')
        scopeDict['5'] += 1
        counts['5Count'] += 1
      if word.find("3") >= 0:
        word = word.replace('3', 'e')
        counts['3Count'] += 1
        scopeDict['3'] += 1
      if word.find("6") >= 0:
        word = word.replace('6', 'b') # g or b?
        counts['6Count'] += 1
        scopeDict['6'] += 1
      if word.find("8") >= 0:
        word = word.replace('8', 'b')
        scopeDict['8'] += 1
        counts['8Count'] += 1
      # x!
      if word.find('x') >= 0:
        word = self.xSub(word, counts, scopeDict)
      #print "word after subsitutions:", word
      # Updating cc scope again!
      self.updateCCScope(word, scopeDict)
      self.updateCKScope(word, scopeDict)
      self.updateHoodScope(word, scopeDict)
      self.updateNwordScope(word, scopeDict)
      # cc, ck and kc
      if word.find("ckk") >= 0:
        scopeDict['cc'] += 1
      if word.find("cck") >= 0:
        scopeDict['cc'] += 1
        pass
      elif word.find("cc") >= 0 and re.match("n[ui]cca+[sz]?", word) == None and word not in self.ccWords:
        counts['ccCount'] += 1
        scopeDict['cc'] += 1
      elif word.find("ck") >= 0 and re.match("n[ui]cka+[sz]?", word) == None and word not in self.ckWords:
        counts['ckCount'] += 1
      if word.find("kc") >= 0 and word not in self.kcWords:
        counts['ccCount'] += 1
        scopeDict['cc'] += 1
    
    #print scopeDict
    #print counts
    #print post
    return counts, scopeDict

  def globalScoreComplexity(self, counts, scopeDict):
    scopeIndices = set()
    for feat in scopeDict.iterkeys():
      for index in scopeDict[feat]:
        scopeIndices.add(index)
    count = 0
    for feat in counts.iterkeys():
      count += len(counts[feat])
    if len(scopeIndices) > 0:
      return str(round(count * 100.0 / len(scopeIndices), 2))
    return ""
  
  def globalScoreSimple(self, counts, scopeDict):
    scope = 0
    for feat in scopeDict.iterkeys():
      scope += len(scopeDict[feat])
    count = 0
    for feat in counts.iterkeys():
      count += len(counts[feat])
    if scope > 0:
      return str(round(count * 100.0 / scope, 2))
    return ""
    
  def runScoring(self):
    consDir = "/usr0/home/pgadde/Work/Ethnic/Hoodup/RuleBasedScoring/considered/"
    notConsFile = open("/usr0/home/pgadde/Work/Ethnic/Hoodup/RuleBasedScoring/wordsNotConsidered.tsv", 'w', 1)
    
    for user in self.userWeekwisePosts.iterkeys():
      for week in self.userWeekwisePosts[user].iterkeys():
        for postIndex in self.userWeekwisePosts[user][week]:
          self.scorePostWordIndexing(self.posts[postIndex][4])

    for sub in self.wordsConsidered.iterkeys():
      consFile = open(consDir + sub, 'w')
      consFile.write('-------' * 2 + '\n')
      consFile.write(sub + '\n')
      consFile.write('-------' * 2 + '\n')
      for word, count in self.wordsConsidered[sub].iteritems():
        consFile.write(word + '\t' + str(count) + '\n')
    consFile.close()
    for word, count in self.wordsNotConsideredLater.iteritems():
      notConsFile.write(word + '\t' + str(count) + '\n')
    notConsFile.close()

if __name__ == '__main__':
  data = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/FromChive/posts.csv"
  fakeAnnotation = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/Users_Pointed_Out_As_Fake.csv"
  accuTimeline = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/accusationsFeatsTimelineAllUsers.tsv"
  F = SubsitutionCoder()
  F.loadData(data)
  F.createActiveForums()
  F.makeWeekwise()
  F.loadFakeAnnotation(fakeAnnotation, set([]))
  F.buildPostIdMap()
  #F.sampleNonFakeUsers()
  F.betterSamplingNonFake()
  F.filterUsers()
  ##F.makeAccusationsWeekwise()
  F.sanityCheck()
  ##F.printPostingBehavior(accuTimeline)
  F.runScoring()
  
  #while 1:
  #  post = raw_input("Text:")
  #  if post != "exit":
  #    F.scorePostWordIndexing(post)
  #  else:
  #    break
