from collections import defaultdict as dd
import csv

class TableGenerator:
  def __init__(self):
    self.posts = []
    self.userwise = dd(list) # Store Indices!
    self.userStart = dd(lambda:5000)
    self.maxDay = -1
    self.userWeekwise = dd(lambda:dd(list))
    self.ccScopeUsers = set()
    self.affiliation = dd(str)
    
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
      self.affiliation[user] = line[6]
    postsFile.close()
  
  def makeWeekwise(self):
    for user in self.ccScopeUsers:
      for postIndex in self.userwise[user]:
        #print self.userStart[user]
        self.userWeekwise[user][(int(self.posts[postIndex][8]) - self.userStart[user]) / 7].append(postIndex)
      #break
    
  def sanityCheck(self):
    print "Posts:", len(self.posts)
    print "Users:", len(self.userwise)
    print "MaxDay:", self.maxDay
    print "ccScopeUsers:", len(self.ccScopeUsers)
    print "Weekwise:", len(self.userWeekwise)
  
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
      return round((avg * 100.0) / numPosts,2)
    else:
      return -1
  
  def makeTable(self, tableFile):
    possibleRows = 0
    nonZeroRows = 0
    tableFile = open(tableFile,'w')
    for user in self.ccScopeUsers:
      for week in self.userWeekwise[user]:
        possibleRows += 1
        ccAvg = self.ccPostAvg(self.userWeekwise[user][week])
        if ccAvg != -1:
          nonZeroRows += 1
          #print user, week, self.affiliation[user], ccAvg
          tableFile.write('\t'.join(map(lambda x:str(x), [user, week, self.affiliation[user], ccAvg]))+'\n')
    tableFile.close()
    print possibleRows, nonZeroRows
    
if __name__ == '__main__':
  TG = TableGenerator()
  postsFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/postsWithScores.csv"
  ccTable = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/ccTable.tsv"
  TG.loadPosts(postsFile)
  TG.makeWeekwise()
  TG.makeTable(ccTable)
  #TG.sanityCheck()
