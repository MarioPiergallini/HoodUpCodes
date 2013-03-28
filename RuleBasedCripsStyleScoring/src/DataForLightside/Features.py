import re, copy
from collections import defaultdict as dd

class RuleBasedFeatures:
  def __init__(self):
    self.twitterLexicon = set()
    self.pkWords = set(["napkin", "pumpkin", "pk", "upkeep"])
    self.kcWords = set(["kc", "backcast", "backcloth", "blackcock", "blackcurrant", "bookcase", "cockchafer", "dickcissel", "kekchi", "kinkcough",
                        "lockchester", "markcourt", "neckcloth", "packcloth", "sackcloth"])
    self.bkWords = set(["bk", "abk", "ebk", "bks", "abks", "ebks", "bkz", "abkz", "ebkz"])
    self.addPlurals(self.pkWords)
    self.pkWords.add("pk's")
    self.ccWords = set()
    self.ckWords = set()
    self.loadLexiconForCC()
    self.loadLexiconForCK()
    self.loadTwitterLexicon("")
    self.addAAESuffEnds(self.twitterLexicon)
    self.addXtreme(self.twitterLexicon)
    self.addPlurals(self.twitterLexicon)
    
    self.wordsNotConsideredLater = dd(int)
    self.wordsConsidered = dd(lambda:dd(int))
    self.consideredWordsCount = 0
  
  def loadLexiconForCC(self):
    lexFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    self.ccWords = set()
    for line in open(lexFile):
      line = line.strip().lower()
      if line.find("cc") >= 0:
        self.ccWords.add(line)
  
  def loadLexiconForCK(self):
    lexFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    self.ckWords = set()
    for line in open(lexFile):
      line = line.strip().lower()
      if line.find("ck") >= 0:
        self.ckWords.add(line)
    
  def addPlurals(self, words):
    words2 = copy.deepcopy(words)
    for word in words2:
      words.add(word + "s")
      words.add(word + "z")
      words.add(word + "'s")
      words.add(word + "'z")
  
  def addXtreme(self, words):
    words2 = copy.deepcopy(words)
    for word in words2:
      if re.match("ex", word):
        words.add(word[1:])
  
  def addAAESuffEnds(self, words):
    words2 = copy.deepcopy(words)
    for word in words2:
      if word[-2:] == 'er':
        words.add(word[:-2] + 'a')
      if word[-3:] == 'ing':
        words.add(word[:-1])
      words.add(word + "s")
      words.add(word + "z")
      words.add(word + "'s")
      words.add(word + "'z")
  
  def loadTwitterLexicon(self, lexiconFile):
    lexiconFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/RuleBasedStyleScoring/aquaintAZ"
    for line in open(lexiconFile):
      line = line.strip()#.split('\t')
      self.twitterLexicon.add(line)
      #self.twitterLexicon[line[0]] = int(line[1])
  
  def filterTwitterLexicon(self):
    words = copy.deepcopy(self.twitterLexicon)
    for word in words:
      if word.find("-") > 0:
        dashSplit = word.split('-')
        for part in dashSplit:
          self.twitterLexicon.add(part)
    
  def preProcess(self, word):
    word = word.replace("$", "s")
    word = word.replace("00", "oo")
    word = re.sub(r'([a-z])0([a-z])', r'\1o\2', word)
    word = re.sub("i+", "i", word)
    word = re.sub(r"([\w])\1\1+", r'\1\1', word)
    return word
  
  def containsDigit(self, word):
    for char in word:
      if ord(char) >= ord('0') and ord(char) <= ord('9'):
        return False
      return True
  
  def containsLetter(self, word):
    for char in word:
      if ord(char) >= 97 and ord(char) < 123:
        return True
    return False
  
  def notInterested(self, word):
    try:
      dummy = int(word)
      return True
    except:
      pass
    if len(word) >= 20:
      return True
    if len(word) <= 1:
      return True
    try:
      if word[:3] == '___' and word[-3:] == '___':
        return True
    except:
      pass
    if word.find("x") < 0 and word.find("ii") < 0 and word.find("^") < 0 and word.find("bk") < 0 and word.find("pk") < 0 \
    and word.find("hk") < 0 and word.find("cc") < 0 and word.find("ck") < 0 and not self.containsDigit(word):
      return True
    if word.find("=") >= 0:
      return True
    if word.find('@') >= 0 :
      return True
    if not self.containsLetter(word):
      return True
    if re.match(".*[0-9]{4}.*", word):
      return True
    if re.match("([0-9]+)?x([0-9]+)?('s)?$", word):
      return True
    return False
  
  def updateScope(self, word, scopeDict, wordIndex):
    if word.find("c") >= 0:
      scopeDict['cCaret'].add(wordIndex)
    if word.find("b") >= 0:
      scopeDict['bk'].add(wordIndex)
      scopeDict['bCaret'].add(wordIndex)
    if word.find("p") >= 0:
      scopeDict['pk'].add(wordIndex)
      scopeDict['pCaret'].add(wordIndex)
    if word.find("h") >= 0:
      scopeDict['hk'].add(wordIndex)
      scopeDict['hCaret'].add(wordIndex)
    if word.find("e") >= 0:
      scopeDict['3'].add(wordIndex)
    if word.find("b") >= 0:
      scopeDict['6'].add(wordIndex)
    if word.find("s") >= 0:
      scopeDict['5'].add(wordIndex)
    ### Not counting 8 feature ###
    #if word.find("b") >= 0:
    #  scopeDict['8'].add(wordIndex)
    if word.find("o") >= 0:
      scopeDict['x'].add(wordIndex)
      scopeDict['oe'].add(wordIndex)
  
  def updateCCScope(self, word, scopeDict, wordIndex):
    if word.find("ck") >= 0 and word in self.twitterLexicon:
      scopeDict['cc'].add(wordIndex)
  
  def updateCKScope(self, word, scopeDict, wordIndex):
    if word.find("cck") < 0 and ((word.find("ck") >= 0 and word not in self.twitterLexicon) or (word.find("c") >= 0 and word.find("ck") < 0 and word in self.twitterLexicon)):
      scopeDict['ck'].add(wordIndex)
  
  def xSub(self, word, counts, scopeDict, wordIndex):
    
    if word in self.twitterLexicon:
      return word, 0
    
    if word.find('-') >= 0:
      splitWord = word.split('-') 
      w1xSub, w1xFlag = self.xSub(splitWord[0], counts, scopeDict, wordIndex)
      w2xSub, w2xFlag = self.xSub(splitWord[1], counts, scopeDict, wordIndex)
      return w1xSub + '-' + w2xSub, w1xFlag | w2xFlag 
    
    xIndices = []
    listWord = []
    xFlag = 0
    if word.find('xx') >= 0:
      word = word.replace('xx', 'oo')
      counts['xCount'].add(wordIndex)
      xFlag = 1
    for index in range(len(word)):
      char = word[index]
      listWord.append(char)
      if char == 'x':
        xIndices.append(index)
    for xIndex in xIndices:
      if xIndex == 0:
        listWord[xIndex] = 'o'
        xFlag = 1
        continue
      if listWord[xIndex - 1] not in set(["a", "e", "i", "o", "u"]):
        listWord[xIndex] = 'o'
        xFlag = 1
    if xFlag:
      counts['xCount'].add(wordIndex)
      scopeDict['x'].add(wordIndex)
    word = ''.join(listWord)
    return word, xFlag
  
  def hoodDoubleSub(self, word, counts, wordIndex):
    prevWord = word
    word = re.sub(r'gr[0-9][0-9][0-9]?v([a-z]+)', r'groov\1', word)
    word = re.sub(r'h[0-9][0-9][0-9]?d([sz]*)', r'hood\1', word)
    word = re.sub(r'h[0-9][0-9][0-9]?v([a-z]+)', r'hoov\1', word)
    word = re.sub(r'bl[0-9][0-9][0-9]?d([sz]+?)', r'blood\1', word)
    if prevWord != word:
      counts['hoodCount'].add(wordIndex)
      self.wordsConsidered['hood'][prevWord] += 1
    return word
  
  def nwordDoubleSub(self, word, counts, wordIndex):
    prevWord = word
    word = re.sub(r'n[iu][0-9][0-9][0-9]?a([sz]?)', r'nigga\1', word)
    if prevWord != word:
      counts['nwordCount'].add(wordIndex)
      self.wordsConsidered['nword'][prevWord] += 1
    return word
  
  def updateHoodScope(self, word, scopeDict, wordIndex):
    if re.match(r'hood([sz]+)?', word) != None:
      scopeDict['hood'].add(wordIndex)
    elif re.match(r'hoov[a-z]+', word) != None:
      scopeDict['hood'].add(wordIndex)
    elif re.match(r'blood([sz]+)?', word) != None:
      scopeDict['hood'].add(wordIndex)
    elif re.match(r'groov[a-z]+', word) != None:
      scopeDict['hood'].add(wordIndex)
  
  def updateNwordScope(self, word, scopeDict, wordIndex):
    if re.match(r'nigga([sz]?)', word):
      scopeDict['nword'].add(wordIndex)

  def updateCaretFeats(self, word, counts, scopeDict, wordIndex):
    if word.find("b^") >= 0:
      counts['bCaretCount'].add(wordIndex)
    if word.find("c^") >= 0:
      counts['cCaretCount'].add(wordIndex)
    if word.find("h^") >= 0:
      counts['hCaretCount'].add(wordIndex)
    if word.find("p^") >= 0:
      counts['pCaretCount'].add(wordIndex)
    word = word.replace("^", "")
    return word
  
  def scorePostWordIndexing(self, post):
    counts = dd(set)
    scopeDict = dd(set)
    #score the words
    for index in range(len(post.split())):
      word = post.split()[index]
      actualWord = word
      self.updateScope(word, scopeDict, index) ## Updating the scope before skipping the words
      self.updateCCScope(word, scopeDict, index)
      if word in self.twitterLexicon or self.notInterested(word):
        self.updateCKScope(word, scopeDict, index)
        #print "filtered:", word
        continue
      considered = 0
      #print "un-filtered:", word
      word = self.preProcess(word)
      # ^
      if word.find("^") >= 0:
        word = self.updateCaretFeats(word, counts, scopeDict, index)
        considered = 1
      ## replacing cck with ck
      word = word.replace("cck", "ck")
      word = word.replace("ckk", "ck")
      # bk, pk, hk
      
      if word.find("bk") >= 0 and word not in self.bkWords:
        word = word.replace("bk", "b")
        counts['bkCount'].add(index)
        considered = 1
        self.wordsConsidered['bk'][actualWord] += 1
      if word.find("hk") >= 0:
        word = word.replace("hk", "h")
        counts['hkCount'].add(index)
        considered = 1
        self.wordsConsidered['hk'][actualWord] += 1
      if word.find("pk") >= 0 and word not in self.pkWords:
        word = word.replace("pk", "p")
        counts['pkCount'].add(index)
        considered = 1
        self.wordsConsidered['pk'][actualWord] += 1
      # oe
      if word.find(u'\xf8') >= 0:
        word = word.replace(u'\xf8', 'o')
        counts['oeCount'].add(index)
        scopeDict['oe'].add(index)
        considered = 1
        self.wordsConsidered['oe'][actualWord] += 1
      ## Double Digits!
      word = self.hoodDoubleSub(word, counts, index)
      word = self.nwordDoubleSub(word, counts, index)
      ## Single Digits
      if re.match("(.*[a-z]5?5([^0-9].*)?|(.*[^0-9])?55?[a-z].*)$", word):
        word = word.replace('5', 's')
        scopeDict['5'].add(index)
        counts['5Count'].add(index)
        self.wordsConsidered['5s'][actualWord] += 1
        considered = 1
      if re.match("(.*[a-z]3?3([^0-9].*)?|(.*[^0-9])?33?[a-z].*)$", word):
        word = word.replace('3', 'e')
        counts['3Count'].add(index)
        scopeDict['3'].add(index)
        considered = 1
        self.wordsConsidered['3e'][actualWord] += 1
      if re.match("(.*[aeiou][rlm]?6?6([^0-9].*)?|(.*[^0-9])?66?[rl]?[aeiouy].*)$", word):
        word = word.replace('6', 'b') # g or b?
        counts['6Count'].add(index)
        scopeDict['6'].add(index)
        scopeDict['bCaret'].add(index)
        scopeDict['bk'].add(index)
        ##scopeDict['8'].add(index)
        considered = 1
        self.wordsConsidered['6b'][actualWord] += 1
      
      ### Not counting 8 feature ###  
      '''if re.match("(.*[aeiou][rlm]?8?8([^0-9].*)?|(.*[^0-9])?88?[rl]?[aeiouy].*)$", word):
        word = word.replace('8', 'b')
        scopeDict['8'].add(index)
        scopeDict['bCaret'].add(index)
        scopeDict['bk'].add(index)
        scopeDict['6'].add(index)
        counts['8Count'].add(index)
        considered = 1
        self.wordsConsidered['8b'][actualWord] += 1'''
        
      # x!
      if word.find('x') >= 0:
        word, xFlag = self.xSub(word, counts, scopeDict, index)
        if xFlag:
          self.wordsConsidered['x'][actualWord] += 1
          considered = 1
      #print "word after subsitutions:", word
      # Updating cc scope again!
      self.updateCCScope(word, scopeDict, index)
      self.updateCKScope(word, scopeDict, index)
      self.updateHoodScope(word, scopeDict, index)
      self.updateNwordScope(word, scopeDict, index)
      # cc, ck and kc
      if word.find("ckk") >= 0:
        scopeDict['cc'].add(index)
      if word.find("cck") >= 0: ## Why linked with cc
        scopeDict['cc'].add(index)
        pass
      elif word.find("cc") >= 0 and re.match("n[ui]cca+[sz]?", word) == None and word not in self.ccWords:
        counts['ccCount'].add(index)
        scopeDict['cc'].add(index)
        self.wordsConsidered['cc'][actualWord] += 1
        considered = 1
      elif self.isCK(word):
        counts['ckCount'].add(index)
        self.wordsConsidered['ck'][actualWord] += 1
        considered = 1
      if word.find("kc") >= 0 and word not in self.kcWords:
        counts['ccCount'].add(index)
        scopeDict['cc'].add(index)
        considered = 1
        self.wordsConsidered['cc'][actualWord] += 1
      if considered == 0:
        self.wordsNotConsideredLater[actualWord] += 1
      else:
        self.consideredWordsCount += 1
    
    #print scopeDict
    #print counts
    #print post
    #print dict(map(lambda x:(x[0], len(x[1])), counts.items())), dict(map(lambda x:(x[0], len(x[1])), scopeDict.items()))
    #print counts, scopeDict
    #print "Complexity Global Feat:", self.globalScoreComplexity(counts, scopeDict)
    #print "Simple Global Feat:", self.globalScoreSimple(counts, scopeDict)
    return counts, scopeDict
  
  def isCK(self, word):
    
    if word.find("-") >= 0:
      splitWord = word.split('-')
      return self.isCK(splitWord[0]) | self.isCK(splitWord[1])
    
    if word.find("ck") < 0:
      return False
    ckIndex = word.index("ck")
    firstWord = word[:ckIndex + 2]
    secondWord = word[ckIndex + 2:]
    
    if re.match("n[uix]cka+[sz]?", word) or word in self.ckWords or re.match("m[oua][ftherauodzv]{0,4}f[aiou][ckg]+([aenoiusr][a-z]*)?", word) or re.match("f[eiou\*]{0,1}[ckg]*ck[ckg]*([aenoius][a-z]*)?", word):
      return False
     
    if len(firstWord) >= 4 and (firstWord in self.ckWords or re.match("m[oua][ftherauodzv]{0,4}f[aiou][ckg]+([aenoiusr][a-z]*)?", firstWord) or re.match("f[eiou\*]{0,1}[ckg]*ck[ckg]*([aenoius][a-z]*)?", firstWord)):
      if secondWord.find("ck") < 0:
        return False
    
    if secondWord.find("ck") >= 0 and re.match("n[uix]cka+[sz]?", secondWord) == None and word not in self.ckWords and not re.match("m[oua][ftherauodzv]{0,4}f[aiou][ckg]+([aenoiusr][a-z]*)?", secondWord) and not re.match("f[eiou\*]{0,1}[ckg]*ck[ckg]*([aenoius][a-z]*)?", secondWord):
      return True
    
    #return False
    return True
