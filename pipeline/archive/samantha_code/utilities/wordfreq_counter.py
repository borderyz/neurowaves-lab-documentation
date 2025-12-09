import re
import string
import operator
from time import gmtime, strftime

print(strftime("%H:%M:%S", gmtime()))
frequency = { }

#first, in terminal run sed 's/[[:punct:]]//g' FILENAME.txt > nopunct_FILENAME.txt
#sed 's/[[:punct:]]//g' twittercorp_11may22txt > nopunct_twittercorp_11may22.txt
f = open("wordcount_nopunct_twittercorp_11may22.txt", "w")
document_text = open('nopunct_twittercorp_11may22.txt', 'r', encoding="utf8", errors='ignore')
text_string = document_text.read().lower()
#print(text_string)
match_pattern = re.findall(r'\S+', text_string)
#print(match_pattern)

if len(match_pattern) == 0:
    print("nothing")
else:
    for word in match_pattern:
        count = frequency.get(word,0)
        frequency[word] = count + 1


for key, value in sorted(frequency.items(), key=operator.itemgetter(1)):
    f.write('{} {}\n'.format(key, value))

f.close()

print(strftime("%H:%M:%S", gmtime()))
