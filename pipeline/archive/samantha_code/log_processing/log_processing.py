import re

wrongcount = 0
total = 240 #Arasurp 589 TagSurp 407 Savant_Ara 120 Savant_Ara 2 240
totalreal = 120
#with open('tag_surp_logs/P040-TagSurp.log','r') as f:
#with open('AraSurp_mne/log_files/Y0359-AraSurp.log','r') as f:
with open('../../MEG_DATA/Y0440/Y0440-Savant_Ara.log','r') as f:
	for line in f:
		line = line.strip()
		count = len(re.findall('; (99|10)\t.+(miss|incorrect)',line))
		if count != 0:
			line = re.split('\W+', line)
			#line = line[1:4]
			print(line)
			wrongcount = wrongcount + count
accuracy = 100 - (100* (wrongcount / totalreal))
print("possible accuracy:")
print(accuracy)
accuracy = (100* (wrongcount / totalreal))
print("possible accuracy:")
print(accuracy)
