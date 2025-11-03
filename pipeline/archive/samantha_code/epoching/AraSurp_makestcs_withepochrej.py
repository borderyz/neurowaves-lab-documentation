import pyface.qt
import mne
#from eelbrain import * #do this as import eelbrain and then import pandas as well
import eelbrain
import pandas as pd
import glob #there
import matplotlib.pyplot as plt
import numpy as np
import os #there
from mne.preprocessing import ICA
import pickle


#raw1 = mne.io.read_raw_fif('AraSurp/meg/R0358/Y0358_AraSurp-NR-raw.fif',preload=True)
#raw2 = mne.io.read_raw_fif('AraSurp/meg/R0358/Y0358_AraSurp-NR-raw.fif',preload=True)
#raws = [raw1,raw2]
#raw = concatenate_raws(raws)
#raw.save('AraSurp/meg/R0358/Y0358_AraSurp-NR-raw.fif',overwrite=True)

def make_epoch_stcs(epochs, snr = 2.0, method='dSPM', morph=True, save_to_disk = True):                           
	"""Apply inverse operator to epochs to get source estimates of each item"""
	lambda2 = 1.0 / snr ** 2.0
	inverse = inv
	eps = mne.minimum_norm.apply_inverse_epochs(epochs=epochs,inverse_operator=inverse,lambda2=lambda2,method = method)
	if morph == True:
		eps_morphed = []
		counter = 1
		morph_status = 'morphed'
	# create morph map
	# get vertices to morph to (we'll take the fsaverage vertices)
		subject_to = 'fsaverage'
		fs = mne.read_source_spaces(subjects_dir + '%s/bem/%s-ico-4-src.fif' % (subject_to, subject_to))
		#vertices_to = [fs[0]['vertno'], fs[1]['vertno']]
		vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir='AraSurp/mri/')
		subject_from = subj
	
		for stc_from in eps:
			print "Morphing source estimate for epoch %d" %counter
			# use the morph function
			morph_mat = mne.compute_morph_matrix(subject_from, subject_to, stc_from.vertices, vertices_to=vertices_to, subjects_dir=subjects_dir)
			stc = mne.morph_data_precomputed(subject_from, subject_to, stc_from, vertices_to, morph_mat)
			eps_morphed.append(stc)
			counter += 1
			eps = eps_morphed
	if save_to_disk:
		pass
		#with open(op.join(stc_cont, '%s_stc_epochs.pickled' %subject), 'w') as fileout:
			#pickle.dump(eps, fileout)
	return eps

#cd ../../media/nellab/My Passport/AraSurp.py.workspace/AraSurp_eel

os.environ["SUBJECTS_DIR"] = 'AraSurp/mri'

event_id = dict(Hroot_Hlin_VIII=64, Lroot_Hlin_VIII=34, Hroot_Llin_VIII=41, Lroot_Llin_VIII=21, Hroot_Hlin_VII=71, Hroot_Llin_VII=25, Lroot_Hlin_VII=18, Lroot_Llin_VII=37, Hroot_Hlin_I=7, Lroot_Hlin_I=6, Hroot_Llin_I=5, Lroot_Llin_I=11)
condition_format = 'rootsurp_linearsurp_binyan'

#########making ICA
subjects = ['R0355']
for s in subjects:
	subject = s
	ica = ICA(n_components=0.95,method='fastica',random_state=42,max_iter=750)
	#reject = dict(mag=2e-12)
	raw = mne.io.read_raw_fif('AraSurp/meg/%s/%s_AraSurp-NR-raw.fif' %(subject,subject),preload=True)
	raw.filter(l_freq=0.1,h_freq=40,method='iir')
	ica.fit(raw,reject = dict(mag=2e-12))
	#ica.fit(raw)
        ica.plot_sources(raw)
        raw_input('Press enter to continue')    
	raw=ica.apply(raw,exclude=ica.exclude)
	raw.save('AraSurp/meg/%s/%s_AraSurp-raw.fif' %(subject,subject),overwrite=True)
	del raw,ica



##########read in data and trigger shift events##########
subjects_dir = 'AraSurp/mri/'
#subjects = ['R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0333','R0345','R0346','R0348']
#,'R0322','R0323','R0325','R0327'
subjects = ['R0157','R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0353','R0358','R0359'] #_75_epochdrop_acc

subjects = ['R0357'] 
#subjects = ['R0322']
for subj in subjects:
	
	
	raw = mne.io.read_raw_fif('AraSurp/meg/%s/%s_AraSurp-raw.fif' %(subj,subj),preload=True)
	events = mne.find_events(raw,min_duration=0.002)
	events_ = events
	####remove the below chunk for non-trigger shift
	#trigger shift all plus 200
	'''
	#
	events_[:,0] = events_[:,0] + 200
	#trigger shift viii and vii words an additional 200
	events_[events_[:, 2] == 64, 0] +=200
	events_[events_[:, 2] == 34, 0] +=200
	events_[events_[:, 2] == 41, 0] +=200
	events_[events_[:, 2] == 21, 0] +=200
	events_[events_[:, 2] == 71, 0] +=200
	events_[events_[:, 2] == 25, 0] +=200
	events_[events_[:, 2] == 18, 0] +=200
	events_[events_[:, 2] == 37, 0] +=200
	events = events_
	#
	#####remove the above chunk for non-trigger shift
	

##########make epochs##########

	reject = dict(mag=4e-12)
	#epochs = mne.Epochs(raw,events,event_id,tmin=-0.5,tmax=.6,baseline=(-0.5,-0.4),reject=reject)
	epochs = mne.Epochs(raw,events,event_id,tmin=-0.1,tmax=1.0,baseline=(-0.1,0.0),reject=reject)
	epochs.drop_bad()

##########make rejections with gui
	eelbrain.gui.select_epochs(epochs,mark=['MEG 087','MEG 130'])
	raw_input('NOTE: Save as MEG/%s/%s_rejfile.pickled. \nPress enter when you are done rejecting epochs in the GUI...'%(subj,subj))
	bad_channels = raw_input('\nMarking bad channels:\nWrite bad channels separated by COMMA (e.g. MEG 017, MEG 022)\nIf no bad channels, press enter\n>')
	if bad_channels == '':
		del bad_channels
	else:
		bad_channels = bad_channels.split(', ')
		epochs.drop_channels(bad_channels)
		del bad_channels
	rejfile = eelbrain.load.unpickle('AraSurp/meg/%s/%s-rejfile.pickled' %(subj,subj))
	rejs = rejfile['accept'].x
	epochs_rej = epochs[rejs]
	epochs_rej.save('AraSurp/meg/%s/%s-epo.fif' %(subj,subj))
	del raw
	'''
	
	epochs = mne.read_epochs('AraSurp/meg/%s/%s-epo.fif' %(subj,subj)) #uncomment this to read in
	print subj
	print epochs



##########make evoked averages
	
	factors = condition_format.split('_')

	fts = {f: {} for f in factors}
	for cond in event_id.keys():
		cond_split = cond.split('_')
		for i, l in enumerate(cond_split):
			fts[factors[i]].setdefault(l, [])
			fts[factors[i]][l].append(event_id[cond])

	factors = factors
	factorial_trigger_scheme = fts
	inverted_triggers = {trig: cond for cond, trig in event_id.iteritems()}
	inverted_triggers_levels = {trig: cond.split('_') for trig, cond in inverted_triggers.iteritems()}

	evokeds = []
	conds = []

	for i, key in enumerate(event_id):
            #if key in ds_events['condition'].unique():
		print "Making evoked for %s." %key
		#evokeds.append(epochs[key].average())
		evokeds.append(epochs[key])
		conds.append(key)

	'''
	for factor in factorial_trigger_scheme.keys():
		for level in factorial_trigger_scheme[factor].keys():
			print "Making evoked for %s" %level
			ep = epochs[np.in1d(epochs.events[:,2], factorial_trigger_scheme[factor][level])]
			#av = ep.average()
			#av.comment = level
			#evokeds.append(av)
			evokeds.append(ep)
			conds.append(level)
	#'''

##########make info

	###info = epochs.info #
	###pickle.dump(info,open('AraSurp/meg/%s/%s-info' %(subj,subj),'wb')) #
	info = eelbrain.load.unpickle('AraSurp/meg/%s/%s-info' %(subj,subj)) #uncomment this to read in

##########make covariance matrix

	###cov = mne.compute_covariance(epochs,tmax=0.0,method= 'empirical') #
	#cov = mne.compute_covariance(epochs,tmin=-0.5,tmax=-0.4,method='empirical')
	###pickle.dump(cov,open('AraSurp/meg/%s/%s-cov' %(subj,subj),'wb')) #
	cov = eelbrain.load.unpickle('AraSurp/meg/%s/%s-cov' %(subj,subj)) #uncomment this to read in

##########get source space

	###src = mne.setup_source_space(subject=subj,spacing='ico4',subjects_dir='AraSurp/mri',overwrite=True)
 	src = mne.read_source_spaces('AraSurp/mri/%s/bem/%s-ico-4-src.fif' %(subj,subj)) #uncomment this to read in

##########make forward solution

	#trans = mne.read_trans('AraSurp/meg/%s/%s-trans.fif' %(subj,subj)) 
	#bem = glob.glob('AraSurp/mri/%s/bem/*-bem-sol.fif' %subj)[0]
	###fwd = mne.make_forward_solution(info, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	###fwd = mne.convert_forward_solution(fwd,force_fixed=True)
	###mne.write_forward_solution('AraSurp/meg/%s/%s-fwd.fif'  %(subj,subj),fwd,overwrite=True) 
	
	fwd = mne.read_forward_solution('AraSurp/meg/%s/%s-fwd.fif'  %(subj,subj)) #uncomment this to read in

##########make inverse solution
	###inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, loose=0,fixed=True)
	###pickle.dump(inv,open('AraSurp/meg/%s/%s-epochs-inv' %(subj,subj),'wb'))
	inv = eelbrain.load.unpickle('AraSurp/meg/%s/%s-epochs-inv' %(subj,subj))
	###lambda2 = 1.0 / 3.0 ** 2

###########make morph map
	#'''	
	subject_to = 'fsaverage'
	fs = mne.read_source_spaces(subjects_dir + '%s/bem/%s-ico-4-src.fif' % (subject_to, subject_to))
	vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir='AraSurp/mri/')
	subject_from = subj
	#########morph_map = mne.mne_make_morph_map(subject_from, subject_to, subjects_dir=subjects_dir)
	#'''

###########write stcs
	'''
	evcount = 0
	for evoked in evokeds:
		if evcount == 0:
			print "first evoked of this particpiant, making morph map"
			stc_from = mne.minimum_norm.apply_inverse(evoked,inv,lambda2=lambda2,verbose=False,method='dSPM')
			morph_mat = mne.compute_morph_matrix(subject_from, subject_to, stc_from.vertices, vertices_to=vertices_to, subjects_dir=subjects_dir)
			#stc_avg = mne.morph_data(subject_from, subject_to, stc_from, 5, smooth=5)  
			stc_avg = mne.morph_data_precomputed(subject_from, subject_to, stc_from, vertices_to, morph_mat)
			stc_avg.save('AraSurp/stc_notriggershift/%s_%s' %(subj,conds[evcount]))
			print "wrote evoked " + evoked.comment
			evcount = evcount + 1
		else:
			print "morph map exists, continuing to write stc..."
			stc_from = mne.minimum_norm.apply_inverse(evoked,inv,lambda2=lambda2,verbose=False,method='dSPM')
			stc_avg = mne.morph_data_precomputed(subject_from, subject_to, stc_from, vertices_to, morph_mat)
			stc_avg.save('AraSurp/stc_notriggershift/%s_%s' %(subj,conds[evcount]))
			print "wrote evoked " + evoked.comment
			evcount = evcount + 1
	'''
	#filenames = ['Hroot_Hlin_VII','Lroot_Llin_I','Lroot_Llin_VII','Hroot_Hlin_I','Hroot_Hlin_VIII','Hroot_Llin_VII','Hroot_Llin_VIII','Lroot_Llin_VIII','Lroot_Hlin_VII','Lroot_Hlin_I','Lroot_Hlin_VIII','Hroot_Llin_I','I','VII','VIII','Lroot','Hroot','Llin','Hlin']

	filenames = ['Hroot_Hlin_VII','Lroot_Llin_I','Lroot_Llin_VII','Hroot_Hlin_I','Hroot_Hlin_VIII','Hroot_Llin_VII','Hroot_Llin_VIII','Lroot_Llin_VIII','Lroot_Hlin_VII','Lroot_Hlin_I','Lroot_Hlin_VIII','Hroot_Llin_I']

###########write epoch stcs
	i = 0
	for evoked in evokeds:
		eps = make_epoch_stcs(evoked)
		a = 1
		for ep in eps:
			ep.save('AraSurp/stc_epochs/%s_%s_%s' %(subj,filenames[i],a))
			a = a+1
		i = i+1	
	
###########clean up space
	#del epochs, trans, bem, fwd, inv, evokeds, cov, src
	del epochs, fwd, inv, evoked, cov, src
