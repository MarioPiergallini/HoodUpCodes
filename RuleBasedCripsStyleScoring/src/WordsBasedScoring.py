import copy, csv
import MySQLdb as M

class CripsWords:
  def __init__(self):
    self.fillWords()
    self.loadLexiconForCC()
  
  def fillWords(self):
    self.pkWords = set(["pumpkin", "pumpkins", "bumpkin", "bumpkins", "bupkis", "capkin", "capkins", "hapkido", "hopkins", "kempkin",
                        "kempkins", "klipkous", "klipkouses", "lempke", "limpkin", "limpkins", "lumpkin", "lumpkins", "mapkin", "mapkins",
                        "napkin", "napkins", "pipkin", "pipkins", "Nimpkish", "Nipkow", "pipkin", "pipkins", "pipkinet", "pipkinets",
                        "pipkrake", "pipkrakes", "rumpkin", "rumpkins", "shapka", "shapkas", "shopkeep", "shopkeeps", "shopkeeper",
                        "shopkeepers", "shopkeeping", "topknot", "topknots", "upkeep", "upkeeping", "upkeeps"])
    self.hkWords = set(["achkan", "ashkenazim", "ashkenazi", "babushka", "britchka", "droshky", "dutchkin", "hotchkiss", "kishke",
                        "lashkar", "matryoshka", "mitchkin", "munchkin", "mutchkin", "narrischkeit", "peshkash", "puschkinia", "rathke",
                        "rubashka", "sharashka", "suchkin", "tchotchke", "yiddishkeit"])
    self.addPlurals(self.hkWords)
    self.bkWords = set(["abkari", "abkhaz", "abkhazian", "babka", "cobkey", "knobkerrie", "lambkill", "lambkin", "lebkuchen", "libken",
                        "nabk", "sabkha", "subkind", "subkingdom", "thumbkin"])
    self.addPlurals(self.bkWords)
    self.kcWords = set(["backcast", "backcloth", "blackcock", "blackcurrant", "bookcase", "cockchafer", "dickcissel", "kekchi", "kinkcough",
                        "lockchester", "markcourt", "neckcloth", "packcloth", "sackcloth"])
    self.addPlurals(self.kcWords)
    
  def loadLexiconForCC(self):
    lexFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    self.ccWords = set()
    for line in open(lexFile):
      line = line.strip().lower()
      if line.find("cc") >= 0:
        self.ccWords.add(line)
    
  def addPlurals(self, words):
    words2 = copy.deepcopy(words)
    for word in words2:
      words.add(word + "s")
  
  def ccScore(self, post):
    ccHits = 0
    ccScope = 0
    for word in post:
      if word.find("cc") >= 0 and word not in self.ccWords:
          ccScope += 1
          ccHits += 1
      if word.find("kc") >= 0 and word not in self.kcWords:
          ccScope += 1
          ccHits += 1
      if word.find("ck") >= 0:
        ccScope += 1
    if ccScope == 0:
      return -1, -1
    else:
      return ccHits, ccScope 
  
  def pkScore(self, post):
    pkHits = 0
    pkScope = 0
    for word in post:
      if word.find("pk") >= 0 and word not in self.pkWords:
        pkHits += 1
        pkScope += 1
      elif word.find("p") >= 0:
        pkScope += 1
    if pkScope == 0:
      return -1, -1
    else:
      return pkHits, pkScope
  
  def bkScore(self, post):
    bkHits = 0
    bkScope = 0
    for word in post:
      if word.find("bk") >= 0 and word not in self.bkWords:
        bkHits += 1
        bkScope += 1
      elif word.find("b") >= 0:
        bkScope += 1
    if bkScope == 0:
      return -1, -1
    else:
      return bkHits, bkScope
  
  def hkScore(self, post):
    hkHits = 0
    hkScope = 0
    for word in post:
      if word.find("hk") >= 0 and word not in self.hkWords:
        hkHits += 1
        hkScope += 1
      elif word.find("h") >= 0:
        hkScope += 1
    if hkScope == 0:
      return -1, -1
    else:
      return hkHits, hkScope
  
  def scorePost(self, post):
    postBody = copy.deepcopy(post)
    postBody = postBody.split()
    scores = []
    scores.extend(self.ccScore(postBody))
    scores.extend(self.bkScore(postBody))
    scores.extend(self.hkScore(postBody))
    scores.extend(self.pkScore(postBody))
    return scores
  
  def addScores(self, postsFile):
    self.posts = []
    postsFile = open(postsFile)
    postsFile.readline()
    reader = csv.reader(postsFile, quotechar='"', escapechar="\\")
    for post in reader:
      scores = map(lambda x:str(x), self.scorePost(post[4]))
      post = post[:7] + post[9:10] + scores + post[12:]
      self.posts.append(post)
  
  def makeATable(self):
    conn = M.connect('localhost', 'phani', 'phani', 'hoodup')
    cursor = conn.cursor()
    cursor.execute("""create table PostwiseRuleBasedCripsScores(userName VARCHAR(100), userId INT, userMonth INT, ActiveAndPostedForums VARCHAR(50),
      postBody VARCHAR(10000), postId INT, threadId INT, LDAScore DOUBLE, cc DOUBLE, ccScope DOUBLE, bk DOUBLE, bkScope DOUBLE, hk DOUBLE, hkScope DOUBLE,
      pk DOUBLE, pkScope DOUBLE, HoodupLink VARCHAR(100))""")
    status = 0
    for post in self.posts:
      if len(post)!=17:
        continue
      cursor.execute("""insert into PostwiseRuleBasedCripsScores values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", tuple(post))
      status += 1
      if status%10000 == 0:
        print status
    conn.close()
      
if __name__ == '__main__':
  C = CripsWords()
  ldaScoresFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/postsWithLDAScores.csv"
  C.addScores(ldaScoresFile)
  C.makeATable()
