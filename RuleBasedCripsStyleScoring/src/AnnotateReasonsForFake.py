import csv, codecs, textwrap

class ReasonAnnotationHelper:
  def __init__(self):
    self.posts = []
    self.postIdMap = {}
    self.fakeUsers = {}
    self.userNames = {}
  
  def loadFakeAnnotation(self, fakeAnnotation):
    fakeAnnotation = open(fakeAnnotation)
    fakeAnnotation.readline()
    fakeAnnotation = csv.reader(fakeAnnotation)
    for line in fakeAnnotation:
      user = line[1]
      userPosts = set()
      posts = self.parsePosts(line[2])
      userPosts = userPosts | posts
      posts = self.parsePosts(line[3])
      userPosts = userPosts | posts
      if len(userPosts) > 0:
        self.fakeUsers[user] = userPosts
  
  def parsePosts(self, postsField):
    posts = set()
    postsField = postsField.strip()
    if postsField.find(",") >= 0:
      for post in postsField.split(","):
        post = post.strip()
        if post != '':
          posts.add(post)
    else:
      if postsField != '':
        posts.add(postsField)
    return posts
  
  def buildPostIdMap(self):
    for postIndex in range(len(self.posts)):
      postId = self.posts[postIndex][2]
      self.postIdMap[postId] = postIndex
      
  def loadData(self, dataFile):
    dataFile = codecs.open(dataFile, encoding='utf8')
    dataFile.readline()
    reader = csv.reader(dataFile, quotechar='"', escapechar="\\")
    postIndex = 0
    for line in reader:
      user = line[1]
      userName = line[0]
      self.userNames[user] = userName
      self.posts.append(line)
      postIndex += 1
  
  def helpAnnotate(self, annotationFile):
    annotationFile = open(annotationFile, 'w', 1)
    for user in self.fakeUsers.iterkeys():
      #print '---------' * 5
      #print user, self.userNames[user]
      #print '---------' * 5
      for post in self.fakeUsers[user]:
        print '---------' * 5
        print user, post, self.userNames[user]
        print '---------' * 5
        print textwrap.fill(self.posts[self.postIdMap[post]][4], 200)
        print '---------' * 5
        annotation = ''
        #while annotation not in ["style", "norm", "other", "no"]:
        while annotation not in ["crip", "blood", "king", "hoover", "other", "none", "multi"]:
          annotation = raw_input("Enter the annotation: ")
        annotationFile.write(user + '\t' + post + '\t' + annotation + '\n')
        print "Annotation Stored"
      
    annotationFile.close()
      
if __name__ == '__main__':
  data = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/FromChive/posts.csv"
  fakeAnnotation = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/Users_Pointed_Out_As_Fake.csv"
  reasonAnnotation = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/Fake/Annotation/gangAccusations.tsv"
  R = ReasonAnnotationHelper()
  R.loadData(data)
  R.buildPostIdMap()
  R.loadFakeAnnotation(fakeAnnotation)
  R.helpAnnotate(reasonAnnotation)
  
  
