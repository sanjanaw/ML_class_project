import xlrd
import rake
import operator
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

ps = PorterStemmer()
rake_obj = rake.Rake("SmartStoplist.txt",5,3,2)
dat = xlrd.open_workbook('data.xlsx').sheet_by_name('Main dataset')

i = 1
tot_count = 0
true_count = 0
for rownum in range(1,dat.nrows):
    abstract = unicode(dat.cell(rownum,9).value)
    title = str(dat.cell(rownum,2).value)
    keywords = dat.cell(rownum, 15).value
    if keywords!='':
        keywords = (keywords.lower().split(','))
        keywords = [str(t) for t in keywords]
        text = title+". "+abstract
        rake_keywords = rake_obj.run(text.lower())
        if rake_keywords:
            r = [t[0] for t in rake_keywords]
            k = keywords
            temp = []
            for w in k:
                word = ''
                w = word_tokenize(w)
                for w2 in w:
                    w2 = ps.stem(w2)
                    word += w2 + ' '
                temp.append(word)
            k = temp
            temp = []
            for w in r:
                word = ''
                w = word_tokenize(w)
                for w2 in w:
                    w2 = ps.stem(w2)
                    word += w2 + ' '
                temp.append(word)
            r = temp
            tot_count = tot_count + len(k)
#            for a in range(len(r)):
#                for b in range(len(k)):
#                    if r[a]!=k[b] and r[a] not in k[b] and k[b] not in r[a]:
#                        true_count = true_count + 1
            for w in r:
                for w2 in k:
                    if w in w2 or w2 in w: true_count = true_count + 1
print true_count
print tot_count
