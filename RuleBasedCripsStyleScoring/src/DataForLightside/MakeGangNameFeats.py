'''
Created on Apr 26, 2013

@author: Mario
'''

import csv, re
csv.field_size_limit(1000000000)

if __name__ == '__main__':
    #Read in original CSV
    postFile = "D:\\Documents\\Schoolwork\\CMU\\HoodUp\\COWFeaturesWithTextAndGangs_WithoutKH.txt"
    postFile = open(postFile)
    postFile.readline()
    postReader = csv.reader(postFile,delimiter=',', quotechar='\"', escapechar='\\')
    dic = {}
    #Loop through lines in CSV
    for row in postReader:
      #Skip empty rows
      if row == []:
        continue
      #if row[0] == "Username":
      #  continue
      #Get metadata from row
      posterId = row[0]
      numPosts = float(row[1])
      doc = row[-1]
      #Add data to dictionary of UserID:[Username,UserID,gang,#posts,docs]
      if posterId not in dic:
        #count number of positive/neutral or negative gang mentions and divide by numPosts
        #gk = 1.0*len(re.findall(r'\b(?:\w*gk\w+|\w+gk\w*)\b',doc))/numPosts
        crip = 1.0*len(re.findall(r'\b(?:crip|cripp?ing?|locc?(ette)?)[sz]?\b',doc))/numPosts
        crab = 1.0*len(re.findall(r'\b(?:ck|ckr(ab|ip))[sz5]?\b',doc))/numPosts
        blood = 1.0*len(re.findall(r'\b(?:bl(?:xx|u)d|blood[sz5]?|b[l1]\d\d\d?d|damu|piru|ubn)[sz5]?\b',doc))/numPosts
        slob = 1.0*len(re.findall(r'\b(bk|pk|bkl(?:oo|xx)d|pkiru|slobk?)[sz]?\b',doc))/numPosts
        hoova = 1.0*len(re.findall(r'\b((?:h|gr)(?:oo|xx|\d\d\d?)v(?:a|er?)|crim|hgc|hcg)[sz]?\b',doc))/numPosts
        snoova = 1.0*len(re.findall(r'\b(?:hk|(?:hk|sn)(?:oo|xx)v(?:a|er))[sz]?\b',doc))/numPosts
        gd = 1.0*len(re.findall(r'\b(?:[bi]gd|a?b?gdn|(?:black|insane|mania?c) ?gangst(?:a|er)|dis?c?iple)[sz]?\b',doc))/numPosts
        gdk = 1.0*len(re.findall(r'\b(?:gk|g?dk|nigk(?:a|uh))[sz]?\b',doc))/numPosts
        folk = 1.0*len(re.findall(r'\b(?:folkk?|folknation)[sz]?\b',doc))/numPosts
        people = 1.0*len(re.findall(r'\b(?:people|peoplenation)[sz5]?\b',doc))/numPosts
        nation = 1.0*len(re.findall(r'\b(?:(?:al)?mighty|nation)\b',doc))/numPosts
        king = 1.0*len(re.findall(r'\b(?:a?lkq?n?|king|queen)[sz5]?\b',doc))/numPosts
        stone = 1.0*len(re.findall(r'\b(?:[s5]tone|a?bp[s5]n?|black p\.?)[sz5]?\b',doc))/numPosts
        vice = 1.0*len(re.findall(r'\b(?:vicelord|vice|lord|a?[ac]?vln?)[sz5]?\b',doc))/numPosts
        trini = 1.0*len(re.findall(r'\b(?:(?:3|tri)ni(?:tario)?)[sz]?\b',doc))/numPosts
        #construct the new row
        newRow = [posterId,str(numPosts),row[2],row[3],row[4],row[5],row[6],row[8],row[9],row[10],row[11],row[14],row[15],row[16],row[17],str(crip),str(crab),str(blood),str(slob),str(hoova),str(snoova),str(gd),str(gdk),str(folk),str(people),str(nation),str(king),str(stone),str(vice),str(trini),row[18],doc.strip()]
        #Make a new UserID key
        #dic[posterId] = [posterId,str(numPosts),str(crip),str(crab),str(blood),str(slob),str(hoova),str(snoova),str(gd),str(gdk),str(folk),str(people),str(nation),str(king),str(stone),str(vice),str(trini),doc.strip()]
        dic[posterId] = newRow
    #Write output to file
    f = open("D:\\Documents\\Schoolwork\\CMU\\HoodUp\\newPostsGangnam.txt",'w')
    writer = csv.writer(f,delimiter=',', quotechar='\"', escapechar='\\')
    #prepare column header
    headerText = "UserID,NumPosts,ccFreq,ckFreq,bkFreq,pkFreq,hkFreq,"
    headerText = headerText + "3eFreq,5sFreq,6bFreq,xoFreq,"
    headerText = headerText + "bCaret,cCaret,pCaret,hCaret,"
    headerText = headerText + "CripFreq,CrabFreq,BloodFreq,SlobFreq,HoovaFreq,SnoovaFreq,GDFreq,GdkFreq,"
    headerText = headerText + "FolkFreq,PeopleFreq,NationFreq,KingFreq,StoneFreq,ViceFreq,TriniFreq,"
    headerText = headerText + "gang,text"
    header = headerText.split(",")
    writer.writerow(header)
    for posterId in dic:
      writer.writerow(dic[posterId])
    f.close()