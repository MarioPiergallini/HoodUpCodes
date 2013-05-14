from DataReader import DataReader
from Features import RuleBasedFeatures
from collections import defaultdict as dd

class Printer:
  def __init__(self):
    self.DR = DataReader()
    self.Features = RuleBasedFeatures()
    self.feats = ["cc", "ck", "bk", "pk", "hk", "oe", "3", "5", "6", "x", 'nword', 'hood', 'bCaret', 'cCaret', 'pCaret', 'hCaret']
    self.gang = {}
    print 'in constructor'
  
  def loadData(self, postsFile):
    self.DR.loadData(postsFile)
    print 'data loaded'
  
  def calculateCountScopeFeatures(self, posts):
    Feats = {}
    consideredPosts = dd(int)
    for post in posts:
      postHits, postScopes = self.Features.scorePostWordIndexing(self.DR.posts[post][4])
      for feat in self.feats:
        if len(postScopes[feat]) > 0:
          Feats[feat] = Feats.get(feat,0) + len(postHits[feat + 'Count']) * 100.0 / len(postScopes[feat])
          consideredPosts[feat] += 1
    return dict(map(lambda x:(x[0], x[1] * 1.0 / consideredPosts[x[0]]), Feats.iteritems())) 
  
  def calculateCountFeatures(self, posts):
    Feats = dd(int)
    for post in posts:
      numWords = len(self.DR.posts[post][4].split())
      postHits, postScopes = self.Features.scorePostWordIndexing(self.DR.posts[post][4])
      for feat in self.feats:
        Feats[feat] += len(postHits[feat + 'Count']) * 100.0 / numWords
    return dict(map(lambda x:(x[0], x[1] * 1.0 / len(posts)), Feats.iteritems()))
  
  def calculateScopeFeatures(self, posts):
    Feats = dd(int)
    for post in posts:
      numWords = len(self.DR.posts[post][4].split())
      postHits, postScopes = self.Features.scorePostWordIndexing(self.DR.posts[post][4])
      for feat in self.feats:
        Feats[feat] += len(postScopes[feat]) * 100.0 / numWords
    return dict(map(lambda x:(x[0], x[1] * 1.0 / len(posts)), Feats.iteritems()))  
  
  def calculateFeatures(self, posts):
    Hits = dd(int)
    Scopes = dd(int)
    numWordsScope = dd(int)
    for post in posts:
      numWords = len(self.DR.posts[post][4].split())
      postHits, postScopes = self.Features.scorePostWordIndexing(self.DR.posts[post][4])
      #print postHits, postScopes
      for feat in self.feats:
        Scopes[feat] += len(postScopes[feat])
        Hits[feat + 'Count'] += len(postHits[feat + 'Count'])
        numWordsScope[feat] += numWords
    #print Hits, Scopes
    #simpleGlobal = self.globalScoreSimple(Hits, Scopes)
    #complexityGloabal = self.globalScoreComplexity(Hits, Scopes)  
    return Hits, Scopes, numWordsScope
  
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
  
  def printFeats(self, users, outFile):
    outFile = open(outFile, 'w', 1)
    outFile.write("user,NumPosts," + ','.join(self.feats) + ",Gang\n")
    for user in users:
      numPosts = len(self.DR.userwisePosts[user])
      Feats = self.calculateCountScopeFeatures(self.DR.userwisePosts[user])
      feats = []
      for feat in self.feats:
        try:
          feats.append(round(Feats[feat], 2))
        except ZeroDivisionError:
          feats.append('-1')
      outFile.write(user + ',' + str(numPosts) + ',' + ','.join(feats) + ',' + self.gang[user] + '\n')
      print '.',
    outFile.close()
  
  def loadGangAnnotation(self, gangAnnotation):
    for line in open(gangAnnotation):
      line = line.strip().split('\t')
      self.gang[line[0]] = line[1]
    print 'gangs loaded'
  
if __name__ == '__main__':
  posts = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/FromChive/posts.csv"
  gangAnnotation = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/BasicData/Affiliations/userGangs.tsv"
  dataFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Clustering/Data/style/Postwise/CountOverScopes.csv"
  users = set([l.strip().split('\t')[0] for l in open(gangAnnotation)])
  P = Printer()
  P.loadData(posts)
  P.loadGangAnnotation(gangAnnotation) 
  P.printFeats(users, dataFile)  
