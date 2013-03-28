from collections import defaultdict as dd
import codecs, csv

class DataReader:
  def __init__(self):
    self.posts = []
    self.userwisePosts = dd(set) # Stores indices
    
  def loadData(self, dataFile):
    dataFile = codecs.open(dataFile, encoding='utf8')
    dataFile.readline()
    reader = csv.reader(dataFile, quotechar='"', escapechar="\\")
    postIndex = 0
    for line in reader:
      self.posts.append(line)
      user = line[1]
      self.userwisePosts[user].add(postIndex)
      postIndex += 1
  
  def filterUsers(self):
    allUsers = self.userwisePosts.keys()
    for user in allUsers:
      #if user not in self.fakeUsers and user not in self.nonFakeUsers:
      if len(self.userwisePosts[user]) < 5:
        del self.userwisePosts[user]