from collections import defaultdict as dd
import csv

class LocalDisc:
  def __init__(self):
    self.posts = []
    self.userwise = dd(list) # Store Indices!
    self.userCCAvg = {}
    self.userCC = dd(int)
    self.userDisc = {}
    self.userStart = dd(lambda:5000)
    self.maxDay = -1
    self.userWeekwise = dd(lambda:dd(list))
    self.ccScopeUsers = set()
    self.ccUsers = set()
    self.affiliation = dd(str)
    self.userConsis = {}
    
  def loadPosts(self, postsFile):
    postsFile = open(postsFile)
    postsFile.readline()
    reader = csv.reader(postsFile, quotechar='"', escapechar="\\")
    index = 0
    for line in reader:
      self.posts.append(line)
      user = line[1]
      self.userwise[user].append(index)
      index += 1
      if int(line[8]) > self.maxDay:
        self.maxDay = int(line[8])
      if self.userStart[user] > int(line[8]):
        self.userStart[user] = int(line[8])
      if int(line[12]) > 0:
        self.ccScopeUsers.add(user)
      if int(line[11]) > 0:
        self.ccUsers.add(user)
      self.userCC[user] += int(line[11])
      self.affiliation[user] = line[6]
    postsFile.close()
    
  def makeWeekwise(self):
    for user in self.userwise.keys():
      for postIndex in self.userwise[user]:
        #print self.userStart[user]
        self.userWeekwise[user][(int(self.posts[postIndex][8]) - self.userStart[user]) / 7].append(postIndex)
      #break
  
  def sortPostsBasedOnTime(self):
    users = self.userwise.keys()
    for user in users:
      self.userwise[user] = sorted(self.userwise[user], cmp=lambda x, y:self.day(x) - self.day(y))
      if self.maxDay - self.day(self.userwise[user][0]) <= 180 or len(self.userwise[user]) == 1:
        del self.userwise[user]
      elif self.userCC[user] == 0:
        del self.userwise[user]
    print "Remaining Users:", len(self.userwise)
    
  def day(self, index):
    return int(self.posts[index][8])
  
  def prepareDiscountinuity(self):
    for user in self.userwise:
      diffs = [self.day(self.userwise[user][i]) - self.day(self.userwise[user][i - 1]) for i in range(1, len(self.userwise[user]))]
      lastGap = map(lambda x:self.maxDay - self.day(x), self.userwise[user])[-1]
      maxGap = max(diffs)
      if lastGap > maxGap:
        self.userDisc[user] = 1
      else:
        self.userDisc[user] = 0
  
  def ccPostAvg(self, postIndices):
    avg = 0
    numPosts = 0
    for postIndex in postIndices:
      cc = int(self.posts[postIndex][11])
      ccScope = int(self.posts[postIndex][12])
      if ccScope != 0:
        avg += (cc * 1.0) / ccScope
        numPosts += 1
    if numPosts != 0:
      return round((avg * 100.0) / numPosts, 2)
    else:
      return -1
  
  def calculateConsistency(self):
    for user in self.userwise.keys():
      if len(self.userWeekwise[user]) < 2:
        continue
      prevWeekAvg = 0
      changed = 0
      numDiffs = 0
      start = 1
      diff = 0
      for week in self.userWeekwise[user].iterkeys():
        ccAvg = self.ccPostAvg(self.userWeekwise[user][week])
        if ccAvg != -1:
          diff += abs(ccAvg-prevWeekAvg)
          prevWeekAvg = ccAvg
          if not start:
            changed = 1
          start = 0
          numDiffs += 1
      if not changed:
        continue
      self.userConsis[user] = (diff*1.0)/numDiffs
    
  def sanityCheck(self):
    print "Posts:", len(self.posts)
    print "Users:", len(self.userwise)
    print "MaxDay:", self.maxDay
    print "ccUsers:", len(self.ccUsers)
    print "Weekwise:", len(self.userWeekwise)
    
  def printConsisDisc(self, tableFile):
    tableFile = open(tableFile,'w')
    for user in self.userConsis.iterkeys():
      print user, self.userConsis[user], self.userDisc[user]
      tableFile.write('\t'.join(map(lambda x:str(x),[user,self.userConsis[user], self.userDisc[user]]))+'\n')
    tableFile.close()

if __name__ == '__main__':
  D = LocalDisc()
  postsFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/postsWithScores.csv"
  tableFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/localConsis.tsv"
  D.loadPosts(postsFile)
  D.sortPostsBasedOnTime()
  D.makeWeekwise()
  D.prepareDiscountinuity()
  D.calculateConsistency()
  D.printConsisDisc(tableFile)
  D.sanityCheck()
  
