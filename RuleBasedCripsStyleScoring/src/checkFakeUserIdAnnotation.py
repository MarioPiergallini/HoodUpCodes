import csv

class FakeAnnotationSanityChecker:
  def __init__(self):
    self.fakeUserData = []
    self.usernameMap = {}
    self.mapFromPosts = {}
    
  def loadFakeAnnotation(self, annotationFile):
    annotationFile = open(annotationFile)
    annotationFile.readline()
    annotationFile = csv.reader(annotationFile)
    for line in annotationFile:
      self.fakeUserData.append(line)
  
  def constructUsernameMap(self):
    for line in self.fakeUserData:
      userName = line[0]
      userId = line[1]
      self.usernameMap[userName] = userId
  
  def loadMapFromPostsData(self, postsFile):
    postsFile = open(postsFile)
    postsFile.readline()
    reader = csv.reader(postsFile, quotechar='"', escapechar="\\")
    for line in reader:
      userName = line[0]
      userId = line[1]
      self.mapFromPosts[userName] = userId
  
  def sanityCheck(self):
    for userName in self.usernameMap.iterkeys():
      if userName not in self.mapFromPosts:
        print "User ", userName, self.usernameMap[userName], " not in posts data!"
      if self.usernameMap[userName] != self.mapFromPosts[userName]:
        print "User Id mismatch:", userName, " From Annotation:", self.usernameMap[userName] , "From posts:" , self.mapFromPosts[userName]

if __name__ == '__main__':
  postsFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/FromChive/posts.csv"
  fakeAnnotation = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/Users_Pointed_Out_As_Fake.csv"
  F = FakeAnnotationSanityChecker()
  F.loadFakeAnnotation(fakeAnnotation)
  F.loadMapFromPostsData(postsFile)
  F.constructUsernameMap()
  F.sanityCheck()
