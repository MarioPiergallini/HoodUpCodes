import copy, csv, re
import MySQLdb as M

class CripsWords:
  def __init__(self):
    self.fillWords()
    self.loadLexiconForCC()
  
  def fillWords(self):
    self.pkWords = set(["pk", "pumpkin", "bumpkin", "bupkis", "capkin", "hapkido", "hopkins", "kempkin",
                        "klipkous", "klipkouses", "lempke", "limpkin", "lumpkin", "mapkin",
                        "napkin", "pipkin", "Nimpkish", "Nipkow", "pipkin", "pipkinet",
                        "pipkrake", "rumpkin", "shapka", "shopkeep", "shopkeeper",
                        "shopkeeping", "topknot", "upkeep", "upkeeping", "tompkin", "thompkin"])
    self.addPlurals(self.pkWords)
    self.addPluralz(self.pkWords)
    self.hkWords = set(["hk", "achkan", "ashkenazim", "ashkenazi", "babushka", "britchka", "droshky", "dutchkin", "hotchkiss", "kishke",
                        "lashkar", "matryoshka", "mitchkin", "munchkin", "mutchkin", "narrischkeit", "peshkash", "puschkinia", "rathke",
                        "rubashka", "sharashka", "suchkin", "tchotchke", "yiddishkeit"])
    self.addPlurals(self.hkWords)
    self.addPluralz(self.hkWords)
    self.bkWords = set(["bk", "abkari", "abkhaz", "abkhazian", "babka", "cobkey", "knobkerrie", "lambkill", "lambkin", "lebkuchen", "libken",
                        "nabk", "sabkha", "subkind", "subkingdom", "thumbkin"])
    self.addPlurals(self.bkWords)
    self.addPluralz(self.bkWords)
    self.kcWords = set(["kc", "backcast", "backcloth", "blackcock", "blackcurrant", "bookcase", "cockchafer", "dickcissel", "kekchi", "kinkcough",
                        "lockchester", "markcourt", "neckcloth", "packcloth", "sackcloth"])
    self.addPlurals(self.kcWords)
    self.addPluralz(self.kcWords)
    
  def loadLexiconForCC(self):
    lexFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    self.ccWords = set()
    for line in open(lexFile):
      line = line.strip().lower()
      if line.find("cc") >= 0:
        self.ccWords.add(line)
    #self.ccWords.add("nicca")
    #self.ccWords.add("nucca")
    
  def addPlurals(self, words):
    words2 = copy.deepcopy(words)
    for word in words2:
      words.add(word + "s")
  
  def addPluralz(self, words):
    words2 = copy.deepcopy(words)
    for word in words2:
      words.add(word + "z")
  
  def ccScore(self, post):
    ccHits = 0
    ccScope = 0
    for word in post:
      if word.find("cc") >= 0 and re.match("n[ui]cca+[sz]?", word) != None and word not in self.ccWords:
          ccScope += 1
          ccHits += 1
      if word.find("kc") >= 0 and word not in self.kcWords:
          ccScope += 1
          ccHits += 1
      if word.find("ck") >= 0 and word != "ck":
        ccScope += 1
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
    return hkHits, hkScope
  
  def removeSmileys(self, post):
    newPost = []
    for word in post:
      if len(word) > 6 and word[:3] == '___' and word[-3:] == '___':
        continue
      else:
        newPost.append(word)
    return newPost
  
  def scorePost(self, post):
    postBody = copy.deepcopy(post)
    postBody = postBody.split()
    postBody = self.removeSmileys(postBody)
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
    status = 0
    for post in reader:
      scores = map(lambda x:str(x), self.scorePost(post[4]))
      post = post[:11] + scores + post[11:12]
      self.posts.append(post)
      status += 1
      if status % 10000 == 0:
        print status
  
  def makeATable(self):
    conn = M.connect('localhost', 'phani', 'phani', 'hoodup')
    cursor = conn.cursor()
    cursor.execute("""create table RuleBasedCripsScores(userName VARCHAR(100), userId INT, postId INT, threadId INT, postBody VARCHAR(10000), 
    postForum VARCHAR(50), activeForum VARCHAR(50), userRegDay INT, days INT, hours INT, minutes INT, cc DOUBLE, ccScope DOUBLE, bk DOUBLE, 
    bkScope DOUBLE, hk DOUBLE, hkScope DOUBLE, pk DOUBLE, pkScope DOUBLE, HoodupLink VARCHAR(100))""")
    status = 0
    for post in self.posts:
      if len(post) != 20:
        continue
      cursor.execute("""insert into RuleBasedCripsScores values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", tuple(post))
      status += 1
      if status % 10000 == 0:
        print status
    conn.close()
      
if __name__ == '__main__':
  C = CripsWords()
  ldaScoresFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/posts.csv"
  C.addScores(ldaScoresFile)
  C.makeATable()
