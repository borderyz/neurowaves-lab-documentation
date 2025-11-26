from collections import OrderedDict
#buck2ipa = {"wu":"wu","w":"u:","'":"ʔ",">":"ʔ","<":"ʔ","&":"ʔ","|":"ʔa","`":"a:","{":"","A":"aː","p":"a","v":"θ","j":"dʒ", "H":"ħ","*":"ð","$":"ʃ", "S":"sˤ", "D":"dˤ", "T":"tˤ", "Z":"ðˤ", "E":"ʕ","Y":"a:", "o":"","g":"ɣ", "}":"ʔ"}

buck2ipa = OrderedDict([("wu","wu"),("w","u:"),("'","ʔ"),(">","ʔ"),("<","ʔ"),("&","ʔ"),("|","ʔa"),("`","a:"),("{",""),("A","aː"),("p","a"),("v","θ"),("j","dʒ"),("H","ħ"),("*","ð"),("$","ʃ"), ("S","sˤ"), ("D","dˤ"), ("T","tˤ"), ("Z","ðˤ"), ("E","ʕ"),("Y","a:"), ("o",""),("g","ɣ"), ("}","ʔ")])

#"~":"ّ"
#"w":"و", "y":"ي"
#wu wa wi
#yu ya yi
#w~u w~a w~i
#y~u y~a y~i
# "F":"ً", "N":"ٌ", "K":"ٍ"

#three stages (or a fancy regex) but not necessarily in this order, i need to figure out the order
#glides and long vowels
#single letters
#shadda?

#do i just want to replace ~ with : and add a length feature? is that the right way to have geminates?

#i need to also add a dot after each phoneme

def transString(string):
    '''Given a Buckwalter string, transliterate into IPA
    غ is marked as velar ɣ
    > and < are transcibed as ʔ with no vowel
    Currently removes final word case marking as well'''

    for k, v in buck2ipa.items():
        string = string.replace(k, v)


    return string

test = "wukw<"
print(transString(test))
