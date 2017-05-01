import xlrd
import nltk
from nltk.corpus import stopwords
import random
from sklearn.svm import SVC
from sklearn import tree
from sets import Set

def get_accuracy(genL, actualL):
    count = 0
    for i in range(len(genL)):
        if genL[i]==actualL[i]: count += 1
    return count/float(len(genL))

def get_frequency(p, plist):
    count = 0
    for temp in plist:
        if p==temp: count+=1
    return count

def num_words(p):
    return len(p.split())

def get_features(phrase, list_phrases):
    temp = []
    temp.append(get_frequency(phrase,list_phrases))
    temp.append(num_words(phrase))
    #TODO: refer to paper
    #TODO: use stemming
    return temp

dat = xlrd.open_workbook('data.xlsx').sheet_by_name('Main dataset')

#remove stop words
data = []
test = []
train = []
max = 0
for rownum in range(1,dat.nrows):
    keywords = dat.cell(rownum, 15).value.split(',')
    for i in keywords:
        k = i.split(' ')
        l = len(k)
        if l>max:
            max = l
    r = random.randint(1,10)
    if r > 8:
        test.append(rownum)
    else:
        train.append(rownum)
    #for k in keywords:
    #    k = k.split()
    #    for i in k:
    #        if i in stopwords.words('english'): print i
print "Maximum lengh of keywords: ", max-1

test_data = {}
test_data['features'] = []
test_data['labels'] = []
train_data = {}
train_data['features'] = []
train_data['labels'] = []
num_keywords = 0
cal_keywords = 0
test_keywords = 0
train_keywords = 0
test_neg = 0
train_neg = 0
for rownum in range(1,dat.nrows):
    list_phrases = []
    phrases_set = Set([])
    abstract = unicode(dat.cell(rownum,9).value)
    title = str(dat.cell(rownum,2).value)
    tokens = nltk.word_tokenize((title+". "+abstract))
    keywords = dat.cell(rownum, 15).value.lower().split(",")
    num_keywords += len(keywords)
    for k in keywords: k = k.strip()
    #check what all stopwords are present in keywords: of, and, with, to, in, on
    stop = stopwords.words('english')
    stop.append(".")
    stop.append("!")
    stop.append("?")
    stop.append(",")
    stop.remove("of")
    stop.remove("and")
    stop.remove("with")
    stop.remove("to")
    stop.remove("in")
    stop.remove("on")
    #get all combinations of 1,2,3,4... word pairs without punctuation and stop words
    for l in range(0,max-1):
        for i in range(len(tokens)-l):
            temp = []
            ignore = False
            temp_phrase = ''
            for j in range(0,l):
                if tokens[j+i] not in temp: temp.append(tokens[j+i])
            #print temp
            for t in temp:
                if t in stop: ignore = True
            if ignore==False:
                for t in temp:
                    temp_phrase+=(t+' ')
                list_phrases.append(temp_phrase.lower().strip())
    while '' in list_phrases: list_phrases.remove('')
    #print list_phrases
    #handle capitalization, remove extra spaces and remove the extra 'u'
    #get attributes of all of them
    #mark them as 0 or 1
    labels = []
    added = []
    for phrase in list_phrases:
        phrases_set.add(phrase)
    for phrase in phrases_set:
        if phrase in keywords:
            labels.append(1)
            if rownum in test: test_keywords += 1
            else: train_keywords += 1
            added.append("1")
            cal_keywords+=1
        else:
            r = random.randint(1,10)
            if r < 2: 
                labels.append(0) #reduce number of false samples to make SVM faster
                added.append("1")
                if rownum in test: test_neg += 1
                else: train_neg += 1
            else:
                added.append("0")
    features = []
    it = 0
    for phrase in phrases_set:
        if added[it]=="1": features.append(get_features(phrase, list_phrases))
        it+=1
        #if phrase in keywords: print phrase, get_features(phrase, list_phrases)
        #print phrase, features
    #append to test and train sets
    if rownum in train:
        train_data['features']+=(features)
        train_data['labels']+=(labels)
    else:
        test_data['features']+=(features)
        test_data['labels']+=(labels)
#print train_data
#print test_data

print num_keywords
print cal_keywords
print "Train positives ", train_keywords, "Train negatives ", train_neg
print "Test positives ", test_keywords, "Test negatives ", test_neg

#Decision Tree
print "Start Decision Tree:"
clf = tree.DecisionTreeClassifier()
trainF = train_data['features']
trainL = train_data['labels']
clf = clf.fit(trainF, trainL)
testF = test_data['features']
testL = clf.predict(testF)
#print testL
from IPython.display import Image  
import pydotplus
dot_data = tree.export_graphviz(clf, out_file=None, 
                         feature_names=["Frequency","Length"],  
                         class_names=["0","1"],  
                         filled=True, rounded=True,  
                         special_characters=True)  
graph = pydotplus.graph_from_dot_data(dot_data)  
graph.write_pdf("dt.pdf") 
print "Accuracy: ", get_accuracy(testL, test_data['labels'])

#SVM
print "Start SVM:"
clf = SVC()
clf = clf.fit(trainF,trainL)
testL = clf.predict(testF)
#print testL
print "Accuracy: ", get_accuracy(testL, test_data['labels'])
