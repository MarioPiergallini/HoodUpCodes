
from collections import defaultdict as dd

class AccusationStats:
  def __init__(self):
    self.users = dd(set)
    self.post2Accu = {}
  
  def loadAccusations(self, accuFile):
    accuFile = open(accuFile)
    for line in accuFile:
      line = line.strip().split('\t')
      self.users[line[0]].add(line[1])
      self.post2Accu[line[1]] = line[2]
    print "Num users:", len(self.users)
      
  def gangAccuStats(self):
    diffGangs = 0
    noneCount = 0
    gangCounts = dd(int)
    for user in self.users.iterkeys():
      userAccusations = set()
      for post in self.users[user]:
        userAccusations.add(self.post2Accu[post])
      try:
        userAccusations.remove("none")
      except:
        pass
      if len(userAccusations) > 1:
        print user, userAccusations
        diffGangs += 1
      elif len(userAccusations) == 0:
        noneCount += 1
      else:
        for accu in userAccusations:
          gangCounts[accu] += 1
      
    print "diff gangs:", diffGangs
    print "Gang Counts:", gangCounts
    print "None Count:", noneCount

if __name__ == '__main__':
  gangAccusations = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/gangAccusations.tsv"
  A = AccusationStats()
  A.loadAccusations(gangAccusations)
  A.gangAccuStats()
  
