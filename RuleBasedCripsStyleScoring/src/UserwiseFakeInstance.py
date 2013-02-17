from collections import defaultdict as dd
import csv, re
from happyfuntokenizing import Tokenizer

class FakeMatcher:
  def __init__(self):
    self.posts = []
    self.userwiseThreads = dd(set)
    self.userwisePosts = dd(set) # Stores indices
    self.threads = dd(list)
    self.userNames = {}
    self.fakeRE = re.compile("\\b(you |u |u're |you're |u'r |you'r |your |ur |username )(are |r |re |ar |is |be )(a )(fake|faking|faker|netbanger|net banger|fakeass|net-banger|fake-ass)\\b")
    self.noRealRE = re.compile("\\b(you |u |u're |you're |u'r |you'r |your |ur |username )(aren't |ain't |arent |aint |isn't |isnt |are not |is not |not )(no )?real\\b")
    self.tok = Tokenizer()
    self.badChars = set(['$', ')', '(', '+', '*', '-', '.', '<', '?', '>', '[', ']', '^', '|'])
    self.fakeUsers = {} # Stores the postId of the previous fake annotation we did
    
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
      self.userwiseThreads[user].add(thread)  
      self.userwisePosts[user].add(postIndex)
      postIndex += 1
  
  def loadFakeUsers(self, fakeAnnotation):
    fakeAnnotation = csv.reader(open(fakeAnnotation))
    for line in fakeAnnotation:
      try:
        dummy = int(line[1])
        dummy = int(line[2])
      except:
        continue
      self.fakeUsers[line[1]] = int(line[2])
  
  def filterUsers(self):
    allUsers = self.userwisePosts.keys()
    for user in allUsers:
      if user not in self.fakeUsers.iterkeys():
        del self.userwisePosts[user]
        del self.userwiseThreads[user]
        del self.userNames[user]
  
  def hasFake(self, postId):
    postText = self.posts[postId][4]
    return (self.fakeRE.search(postText) != None) or (self.noRealRE.search(postText) != None)
  
  def printFakeUsers(self, fakersDir):
    for user in self.fakeUsers:
      fakePostIds = []
      for thread in self.userwiseThreads[user]:
        for postIndex in self.threads[thread]:
          if self.hasFake(postIndex):
            fakePostIds.append(postIndex)
      fakePostIds = sorted(fakePostIds, cmp=lambda x, y:int(self.posts[x][2]) - int(self.posts[y][2]))
      #print user, self.posts[fakePostIds[0]][2], self.fakeUsers[user]
      if len(fakePostIds) > 0 and self.posts[fakePostIds[0]][2] != str(self.fakeUsers[user]):
        #self.printPosts(user, fakePostIds)
        dummy = 1
      else:
        print user
  
  def printPosts(self, user, fakePostIds):
    fakersFile = open(fakersDir + user, 'w', 1)
    for postIndex in fakePostIds:
      postId = self.posts[postIndex][2]
      postBody = self.posts[postIndex][4]
      fakersFile.write(postId + '\t' + postBody + '\n')
    fakersFile.close()
  
  def sanityCheck(self):
    print "Posts:", len(self.posts)
    print "Users:", len(self.userwiseThreads)
    print "Fake users:", len(self.fakeUsers)
    for user in self.fakeUsers:
      if user not in self.userwiseThreads.iterkeys():
        print user
    
if __name__ == '__main__':
  data = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/FromChive/posts.csv"
  fakeAnnotation = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/Users_Pointed_Out_As_Fake.csv"
  fakersDir = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/FakeUserFiles/"
  F = FakeMatcher()
  F.loadData(data)
  F.loadFakeUsers(fakeAnnotation)
  F.filterUsers()
  F.sanityCheck()
  F.printFakeUsers(fakersDir)
  
