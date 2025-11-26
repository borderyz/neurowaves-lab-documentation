import os

#from main import subjects
subjects = ['Y0119','Y0208','Y0119','Y0312','Y0321','Y0368','Y0371','Y0367','Y0369','Y0373','Y0374','Y0378','Y0379','Y0381','Y0382','Y0387','Y0393','Y0395','Y0396']

for subj in subjects:


#### FIX THESE

	logFileName = os.path.join("/home/scw9/wray_workspace/Savant_Arabic/Logs/", subj + '-Savant_Ara.log')
	rejFileName = os.path.join("/home/scw9/wray_workspace/Savant_Arabic/new_ica/savant_main/meg", subj, subj + '_SavantAra-rejected_epochs.txt')

####

	rejFile = open(rejFileName, "r")

	rejectedEpochs = []

	for x in rejFile:
		if '[' in x:  # <- you'll need an 'if' statement to make sure that this is a full list
			x = x.split('[') # <- ['Epochs removed (first epoch = 0): ', '350, 430]')
			x = x[1] # <- '350, 430]'
			x = x[:-1] # <- '350, 430'
			x = x.split(',') # = ['350', ' 430']
		rejectedEpochs = x

	rejFile.close()

	z = []

	for epo in rejectedEpochs:
		z.append(epo.strip())

	rejectedEpochs = z

	logFile = open(logFileName, "r")

	newLogFileName = logFileName[:-4]
	newLogFileName += '_NEW.log'
	newLogFile = open(newLogFileName, 'w')
	print(subj)

	trialCounter = 0
	for z in logFile:
		if z.startswith("Picture\t") and ("hit" in z or "incorrect" in z or "miss" in z) and "practice;" not in z:
			if str(trialCounter) in rejectedEpochs:
				print('rejecting trial: ' + str(trialCounter))
				newZ = z[:-1] + '\t!REJECTED!\n'
				newLogFile.write(newZ)
			else:
				newLogFile.write(z)
			trialCounter += 1
		else:
			newLogFile.write(z)

	newLogFile.close()

	logFile.close()
