import csv
from collections import defaultdict as dd
class Discontinuity:
  
  def __init__(self):
    self.posts = []
    self.userWise = dd(list)
    self.userCC = dd(int)
    self.userCCAvg = {}
    self.maxDay = -1
    
  def userConsistency(self, user):
    if self.userCCAvg[user] >= 25 and self.userCCAvg[user] < 75:
      return '0'
    else:
      return '1' 
    
  def loadPosts(self, postsFile):
    postsFile = open(postsFile)
    postsFile.readline()
    reader = csv.reader(postsFile, quotechar='"', escapechar="\\")
    index = 0
    for line in reader:
      self.posts.append(line)
      user = line[1]
      self.userWise[user].append(index)
      self.userCC[user] += int(line[11])
      index += 1
      if int(line[8]) > self.maxDay:
        self.maxDay = int(line[8])
    postsFile.close()
    
  def sortPostsBasedOnTime(self):
    users = self.userWise.keys()
    for user in users:
      self.userWise[user] = sorted(self.userWise[user], cmp=lambda x, y:self.day(x) - self.day(y))
      if len(self.userWise[user]) == 1:
        del self.userWise[user]
      #if 2180 - self.day(self.userWise[user][0]) <= 180 or len(self.userWise[user]) == 1:
      #  del self.userWise[user]
      #elif self.userCC[user] == 0:
      #  del self.userWise[user]
    print "Remaining Users:", len(self.userWise)
  
  def loadCCAvg(self, consistencyTable):
    consistencyTable = open(consistencyTable)
    consistencyTable.readline()
    reader = csv.reader(consistencyTable, quotechar='"', escapechar="\\")
    for line in reader:
      self.userCCAvg[line[1]] = float(line[3])
  
  def day(self, index):
    return int(self.posts[index][8])
  
  def getDiscountinuity(self):
    for user in self.userWise:
      diffs = [self.day(self.userWise[user][i]) - self.day(self.userWise[user][i - 1]) for i in range(1, len(self.userWise[user]))]
      lastGap = map(lambda x:self.maxDay - self.day(x), self.userWise[user])[-1]
      maxGap = max(diffs)
      print maxGap
      #if lastGap > maxGap:
      #  print user + "\t0\t" + self.userConsistency(user)
      #else:
      #  print user + "\t1\t" + self.userConsistency(user)

if __name__ == '__main__':
  D = Discontinuity()
  postsFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/postsWithScores.csv"
  ccConsistencyTable = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/ccUserSubRate.csv"
  D.loadPosts(postsFile)
  D.sortPostsBasedOnTime()
  D.loadCCAvg(ccConsistencyTable)
  D.getDiscountinuity()
  
  
