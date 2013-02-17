from collections import defaultdict as dd
import csv, re
from happyfuntokenizing import Tokenizer

class FakeMatcher:
  def __init__(self):
    self.posts = []
    self.userwiseThreads = dd(lambda:dd(lambda:-1))
    self.userwisePosts = dd(set) # Stores indices
    self.userLastPost = dd(lambda:-1)
    self.threads = dd(list)
    self.userStart = dd(lambda:5000)
    self.userNames = {}
    self.fakeRE = re.compile("\\b(you |u |u're |you're |u'r |you'r |your |ur |username )(are |r |re |ar |is |be )(a )(fake|faking|faker|netbanger|net banger|fakeass|net-banger|fake-ass)\\b")
    self.noRealRE = re.compile("\\b(you |u |u're |you're |u'r |you'r |your |ur |username )(aren't |ain't |arent |aint |isn't |isnt |are not |is not |not )(no )?real\\b")
    self.tok = Tokenizer()
    self.badChars = set(['$', ')', '(', '+', '*', '-', '.', '<', '?', '>', '[', ']', '^', '|'])
    
  def loadData(self, dataFile):
    dataFile = open(dataFile)
    dataFile.readline()
    reader = csv.reader(dataFile, quotechar='"', escapechar="\\")
    postIndex = 0
    for line in reader:
      self.posts.append(line)
      thread = line[3]
      user = line[1]
      username = line[0]
      self.userNames[user] = ' '.join(self.tok.tokenize(username))
      self.threads[thread].append(postIndex)
      if self.userwiseThreads[user][thread] < 0 or self.userwiseThreads[user][thread] > postIndex:  
        self.userwiseThreads[user][thread] = postIndex
      self.userwisePosts[user].add(postIndex)
      days = int(line[8])
      if self.userLastPost[user] < days:
        self.userLastPost[user] = days
      if self.userStart[user] > int(line[8]):
        self.userStart[user] = int(line[8])
      postIndex += 1
    self.sortThreads()
  
  def sortThreads(self):
    for thread in self.threads.iterkeys():
      self.threads[thread] = sorted(self.threads[thread], cmp=lambda x, y:x - y)
  
  def filterUsers(self):
    allUsers = self.userwisePosts.keys()
    for user in allUsers:
      if len(self.userwisePosts[user]) < 20 or len(self.userwisePosts[user]) > 150 or (self.userStart[user] - self.userLastPost[user]) > 120:
        del self.userwisePosts[user]
        del self.userwiseThreads[user]
        del self.userNames[user]
  
  def hasFake(self, postId):
    postText = self.posts[postId][4]
    #if postText.find(" you a fake ")>=0:
    #  print postText
    return (self.fakeRE.search(postText) != None) or (self.noRealRE.search(postText) != None)
  
  def printFakePosts(self, logFile):
    logFile = open(logFile, 'w')
    index = 0
    for post in self.posts:
      if self.hasFake(index):
        logFile.write('\t'.join(post[:5]) + '\n')
      index += 1 
  
  def printFakeUsers(self, fakersFile):
    fakersFile = open(fakersFile, 'w', 1)
    for user in self.userwiseThreads.iterkeys():
      fakePostCount = 0
      fakePostIds = set()
      for thread in self.userwiseThreads[user].iterkeys():
        userFirstPost = self.userwiseThreads[user][thread]
        postIndex = self.threads[thread].index(userFirstPost) + 1
        while postIndex < len(self.threads[thread]):
          postId = self.threads[thread][postIndex]
          if self.hasFake(postId):
            #print 'here'
            fakePostCount += 1
            fakePostIds.add(postId)
          postIndex += 1
      if fakePostCount > 5:
        fakersFile.write(user + '\t' + ' '.join(map(lambda x:str(x), list(fakePostIds))) + '\n')
    fakersFile.close()
  
  def makeRECompatible(self, userName):
    for char in self.badChars:
      if char != '\\':
        userName = userName.replace(char, "\\" + char)
    return userName
  
  def bigRESearch(self, logFile):
    logFile = open(logFile, 'w', 1)
    bigUserName = "\\b("
    for userName in self.userNames.itervalues():
      if userName in ["dat nigga", "bitch"]:
        continue
      if userName.strip() != "":
        if self.considerUserName(userName): 
          userName = self.makeRECompatible(userName)
          bigUserName += userName + " |"
    bigUserName = bigUserName[:-1] + ")"
    bigUserName += "(is )(a )?(fake|faking|faker|netbanger|net banger|fakeass|net-banger|fake-ass)"
    print len(bigUserName)
    print bigUserName
    P = re.compile(bigUserName)
    #sampleText = "i wanna see wat dat nigga about but i aint gonna fite him im on parole . but dat nigga fake so i dont even matter"
    #while 1:
    #  sampleText = raw_input("Enter the text: ")
    #  if sampleText == 'exit':
    #    break
    #  print "Full match:",P.search(sampleText).group(), " username match:",P.search(sampleText).group(1)
    for post in self.posts:
      text = post[4]
      if P.search(text) != None:
        logFile.write('\t'.join(post[:5]) + '\n')
    logFile.close()
  
  def printNonChars(self):
    nonChars = set()
    for userName in self.userNames.itervalues():
      userName = userName.lower()
      for char in userName:
        if ord(char) >= 32 and ord(char) <= 126 and (ord(char) < 97 or ord(char) > 122) and ord(char) not in range(48, 58):
          nonChars.add(char)
    print "Users:", len(self.userNames)
    print nonChars
  
  def contentToLookAt(self):
    uniqThreads = set()
    uniqPosts = set()
    for userId in self.userNames.iterkeys():
      for thread in self.userwiseThreads[userId]:
        uniqThreads.add(thread)
        for post in self.threads[thread]:
          uniqPosts.add(post)
    print "Users to look at:", len(self.userNames)
    print "Unique threads to look at:", len(uniqThreads)
    print "Unique posts to look at:", len(uniqPosts)
  
  def isAllLetters(self, userName):
    for char in userName:
      if ord(char) < 97 or ord(char) > 122:
        return False
    return True
  
  def considerUserName(self, userName):
    for char in userName:
      o = ord(char)
      if o < 32 or o > 126:
        return False
    return True
  
  def matchUserNamesInPosts(self, logFile):
    logFile = open(logFile, 'w', 1)
    for userId in self.userNames.iterkeys():
      userName = self.userNames[userId]
      if not self.isAllLetters(userName):
        continue
      for post in self.posts:
        if post[4].find(userName) >= 0:
          logFile.write(str(userId) + '\t' + userName + '\t' + post[4] + '\n')
    logFile.close()

if __name__ == '__main__':
  data = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/FromChive/posts.csv"
  #fakeUsers = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/fakeUsers.tsv"
  logFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/fakeAccusations.tsv" 
  F = FakeMatcher()
  F.loadData(data)
  F.filterUsers()
  F.printFakePosts(logFile)
  #F.contentToLookAt()
  #F.matchUserNamesInPosts(logFile)
  #F.printNonChars()
  #F.bigRESearch(logFile)
  #F.printFakeUsers(fakeUsers)
  #a = '$ome_/\\$$_ho|e'
  #print a 
  #print F.isAllLetters(a)
