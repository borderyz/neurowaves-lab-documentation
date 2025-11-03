#pip install langdetect

from langdetect import detect, detect_langs
import os

inDir = os.path.join(os.getcwd(),'/home/scw9/wray_workspace/tagalog_POStag/stanford-tagger-4.2.0/stanford-postagger-full-2020-11-17/workspace/9')

inFiles = os.listdir(inDir)

outfile_tag = open('/home/scw9/wray_workspace/tagalog_POStag/9_tag.txt','w')
outfile_other = open('/home/scw9/wray_workspace/tagalog_POStag/9_other.txt','w')

'''
for fname in inFiles[1:]:'/home/scw9/wray_workspace/tagalog_POStag/
    print('======', fname, '======')split text into sentences python nltk
    inpath = os.path.join(inDir,fname)
    with open(inpath,'rb') as inf:
      strip = inf.read().decode(errors='replace')
    strip_sents = strip.split('. ')
    for sent in strip_sents:
        try:
            lang_check = detect_langs(sent)
        except:
            lang_check = ['???:SKIP']
        print(lang_check,'\t',sent)
'''
for fname in inFiles[1:]:
    #print('======', fname, '======')
    inpath = os.path.join(inDir,fname)
    with open(inpath,'rb') as inf:
      strip = inf.read().decode(errors='replace')
    sent = strip
    try:
        lang_check = detect_langs(sent)
    except:
        lang_check = ['???:SKIP']
    top = str(lang_check[0])
    if "tl" in top:
        outfile_tag.write(str(fname + '\t' + top + '\n'))
    elif "?" in top:
        pass
        #print(top)
    else:
        outfile_other.write(str(fname + '\t' + top + '\n'))

    #for langs in lang_check:
    #    print langs
    #if "tl" in lang_check[0]:
    #    print "ok"
    #print(fname,'\t',lang_check)
    #print(lang_check)
