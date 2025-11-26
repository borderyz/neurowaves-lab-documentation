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
from surfer import Brain

from mne.minimum_norm import apply_inverse_epochs, read_inverse_operator
from mne.minimum_norm import apply_inverse

'''
class TagInfRed(eelbrain.MneExperiment):
	path_version = 1 #can be 1 or 0 depending on folder organization
    	trigger_shift = 0.028 #to be added if delay with photodiode
	sessions='TagInfRed' #name in file before R000..
	defaults = {'experiment': 'TagInfRed', #name of your exp
		#'raw': '0-40', #raw data is selected for 0-40Hz. IF FILTERED DURING ICA: 'raw':'raw'
		'raw':'raw',
		'rej': 'man', #manual rejection of epochs
		'epoch': 'epoch',
		'inv': 'fixed-3-dSPM'} #analysis with free dipole orientation. #the number indicates expected signal to noise ratio: 3 for ttest (and anova) and 2 for regression	
	epoch_default = {'tmin':-0.2, 'tmax': .5, 'baseline': (-0.1,0.0)}
	groups = {'all':('R001','R002','R006','R007','R008','R010','R011','R012','R014','R015','R016','R017','R020','R023','R021','R022','R024','R025','R026','R028','R029','R030','R203')}	
	#tmin=-0.5,tmax=1.5,baseline=(-0.4,,-0.2) #'decim': 5, 
	variables = {'condition' : {(35) : 'reduplicate', (30): 'pseudo_transp', (25): 'pseudo_nontransp', (45): 'morph_simple', (40): 'morph_complex', (15) : 'phonemic_in', (20): 'infix_in', (10): 'morph_complex', (5): 'morph_simple'}}
	epochs={'epoch':{},
		'cov': {'base': 'epoch', 'tmin': -0.1, 'tmax': 0.0}
	} #this needs to be here: defines the parameters of the covariance matrix
	parcs = {
'lefthemi_full' : 'fsaverage_parc','' : 'fsaverage_parc','Fusiform': {'kind':'combination','base':'aparc','labels': {'Fusiform':'fusiform'}},'sup-temp': {'kind':'combination','base':'aparc','labels': {'sup-temp':'superiortemporal'}},'mid-temp': {'kind':'combination','base':'aparc','labels': {'mid-temp':'middletemporal'}},'orb-front':{'kind':'combination','base':'aparc','labels':{'orbitofrontal':'lateralorbitofrontal+medialorbitofrontal'}},'occ-lobe':'fsaverage_parc','tark_noise1_binary':'fsaverage_parc','tark_stringType_binary2':'fsaverage_parc'
}
	tests = {'my_anova': {'kind': 'anova', 'x': 'condition * subject'},'my_ttest': {'kind': 'ttest_rel', 'model': 'condition','c1': 'pseudo_nontransp', 'c0': 'pseudo_transp'}}

e = TagInfRed('TagInfRed')

	#'words':{'base': 'epoch','sel':" condition !='nonword'"}, 

e.make_report('my_anova', group='after_acc', parc='Fusiform', pmin=0.05, tstart=0.13, tstop=0.25, samples=10000, sns_baseline=True,epoch='words',include=0.05, redo=True)
'''
#def make_epoch_stcs(epochs, snr = 2.0, method='dSPM', morph=True, save_to_disk = True):                           
def make_epoch_stcs(epochs, nave, snr = 2.0, method='dSPM', morph=True):                           
	"""Apply inverse operator to epochs to get source estimates of each item"""
	lambda2 = 1.0 / snr ** 2.0
	#inverse = inv_3snr
	inverse = inv
	eps = mne.minimum_norm.apply_inverse_epochs(epochs=epochs,inverse_operator=inverse,lambda2=lambda2,method = method,nave=nave,verbose=True)
	if morph == True:
		eps_morphed = []
		counter = 1
		morph_status = 'morphed'
	# create morph map
	# get vertices to morph to (we'll take the fsaverage vertices)
		subject_to = 'fsaverage'
		###eelbrain 14fs = mne.read_source_spaces(subjects_dir + '%s/bem/%s-ico-4-src.fif' % (subject_to, subject_to))
		###eelbrain 14vertices_to = [fs[0]['vertno'], fs[1]['vertno']]
		###eelbrain 14vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir='TagInfRed/mri/')
		subject_from = subject
	
		for stc_from in eps:
			#print "Morphing source estimate for epoch %d" %counter
			# use the morph function
			morph = mne.compute_source_morph(stc_from, subject_from, subject_to, spacing=4, subjects_dir=subjects_dir)
			stc = morph.apply(stc_from)
			eps_morphed.append(stc)
				###eelbrain 14morph_mat = mne.compute_morph_matrix(subject_from, subject_to, stc_from.vertices, vertices_to=vertices_to, subjects_dir=subjects_dir)
				###stc = mne.morph_data_precomputed(subject_from, subject_to, stc_from, vertices_to, morph_mat)
				###eps_morphed.append(stc)
			counter += 1
			eps = eps_morphed
	return eps

subjects_dir = 'TagInfRed/mri/' 

event_id = dict(pseudo_nontransp=25,pseudo_transp=30,reduplicate=35,morph_complex_red=40,morph_simple_red=45,phonemic_in=15,infix_in=20,morph_complex_in=10,morph_simple_in=5,nonword=2)

subjects = ['R001','R002','R006','R007','R008','R010','R011','R012','R014','R015','R016','R017','R020','R023','R024','R025','R026','R028','R029','R030','R203']
#subjects = ['R002','R006','R007','R008','R010','R011','R012','R014','R015','R016','R017','R020','R022','R023','R024','R025','R026','R028','R029','R030','R203']
#subjects = ['R001','R002','R006','R008','R010','R011','R012','R014','R015','R016','R017','R022','R023','R024','R025','R026','R028','R029','R030','R203']
subjects = ['R022']

'''
for s in subjects:
	subject = s
	subject1 = subject
	rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s_oldbase_TagInfRed_raw_epoch-man.pickled' %subject)
	%store rejfile.as_table() >> 'TagInfRed/meg/R029/epoch selection/R029_rejections_oldbase.txt'
'''

#def morph_stcs_in_list(morph,stcs):
#	return morph.apply(stcs)	         

for s in subjects:
	subject = s
	subject1 = subject
	raw = mne.io.read_raw_fif('TagInfRed/meg/%s/%s_TagInfRed-raw.fif' %(subject,subject1),preload=True)

	events = mne.find_events(raw,min_duration=0.002)
	events_ = events
	events_[:,0] = events_[:,0] + 28 #includes 28ms photodiode delay

	reject = dict(mag=4e-12)
	#epochs = mne.Epochs(raw,events_,event_id,tmin=-0.2,tmax=.5,baseline=(-0.1,0),reject=reject) #pre-revisions
	#epochs = mne.Epochs(raw,events_,event_id,tmin=-0.5,tmax=.5,baseline=(-0.5,-0.4),reject=reject) #post-revisions
	epochs = mne.Epochs(raw,events_,event_id,tmin=-0.5,tmax=.5,baseline=((None,None)),reject=reject) #post post-revisions
	epochs.drop_bad()
	#%store epochs.drop_log >> 'TagInfRed/meg/R203/epoch selection/R203_droplog.txt'
	#eelbrain.gui.select_epochs(epochs)
	#input('NOTE: Save as meg/%s/%s_rejfile.pickled. \nPress enter when you are done rejecting epochs in the GUI...'%(subject,subject))
	'''	
	if os.path.isfile('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man_corrected.pickled'%subject):
		rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man_corrected.pickled' %subject)
	else:
		rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man.pickled' %subject)
	%store rejfile.as_table() >> 'TagInfRed/meg/R010/epoch selection/R010_rejections.txt'
	'''
	rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s_oldbase_TagInfRed_raw_epoch-man.pickled' %subject) #for 22
	#rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man_corrected.pickled' %subject)
	rejs = rejfile['accept'].x
	epochs_rej = epochs[rejs]
	epochs = epochs_rej
	'''	
	#rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man.pickled' %subject)
	####if standard rejfile is not sufficient due to automatic epoch rejection:
	#eelbrain.gui.select_epochs(epochs,mark=['MEG 087','MEG 130'])
	#raw_input('NOTE: Save as MEG/%s/%s_rejfile.pickled. \nPress enter when you are done rejecting epochs in the GUI...'%(subject,subject))
	if os.path.isfile('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man_corrected.pickled'%subject):
		rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man_corrected.pickled' %subject)
	else:
		rejfile = eelbrain.load.unpickle('TagInfRed/meg/%s/epoch selection/TagInfRed_raw_epoch-man.pickled' %subject)

		
	rejs = rejfile['accept'].x
	epochs_rej = epochs[rejs]
	epochs = epochs_rej
	print epochs
	'''
	

	#'''
	#make evokeds	
	ev_phonemic_in = epochs['phonemic_in']
	ev_infix_in = epochs['infix_in']


	ev_pseudo_nontransp = epochs['pseudo_nontransp']
	ev_pseudo_transp = epochs['pseudo_transp']
	ev_reduplicate = epochs['reduplicate']
	ev_morph_complex = epochs['morph_complex_in','morph_complex_red']
	ev_morph_simple = epochs['morph_simple_in','morph_simple_red']
	

	####make evoked averages!
	epochs.equalize_event_counts(event_id)
	#'''
	ev_phonemic_in_av = epochs['phonemic_in'].average()
	ev_infix_in_av = epochs['infix_in'].average()
	ev_pseudo_nontransp_av = epochs['pseudo_nontransp'].average()
	ev_pseudo_transp_av = epochs['pseudo_transp'].average()
	ev_reduplicate_av = epochs['reduplicate'].average()
	ev_morph_complex_av = epochs['morph_complex_in','morph_complex_red'].average()
	ev_morph_simple_av = epochs['morph_simple_in','morph_simple_red'].average()
	#'''

	subject1=subject
	trans = mne.read_trans('TagInfRed/meg/%s/%s-trans.fif' %(subject1,subject)) 
	bem = glob.glob('TagInfRed/mri/%s/bem/*-bem-sol.fif' %subject)[0]
	src = mne.read_source_spaces(subjects_dir + '/%s/bem/%s-ico-4-src.fif' %(subject,subject))

	#'''
	#########writing everything the first time
	######for indv trials
	#'''
	#cov = mne.compute_covariance(epochs,tmin=-0.1,tmax=0,method='empirical') #pre-revisions
	#cov = mne.compute_covariance(epochs,tmin=-0.5,tmax=-0.4,method='empirical') #post revisions
	cov = mne.compute_covariance(epochs,tmin=None,tmax=None,method='empirical') #post post revisions
	pickle.dump(cov,open('TagInfRed/meg/%s/%s-cov' %(subject,subject1),'wb'))
	info = epochs.info
	pickle.dump(info,open('TagInfRed/meg/%s/%s-info' %(subject,subject1),'wb'))
	src = mne.setup_source_space(subject=subject,spacing='ico4',subjects_dir='TagInfRed/mri')
	mne.write_source_spaces(subjects_dir + '/%s/bem/%s-ico-4-src.fif' %(subject,subject1),src,overwrite=True) 

	fwd = mne.make_forward_solution(info, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	fwd = mne.convert_forward_solution(fwd,force_fixed=True)
	mne.write_forward_solution('TagInfRed/meg/%s/%s-fwd.fif'  %(subject,subject1),fwd,overwrite=True) 
	#inv_3snr = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, loose=0,fixed=True)
	inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, loose=0,fixed=True)
	pickle.dump(inv,open('TagInfRed/meg/%s/%s-inv' %(subject,subject1),'wb'))
	
	######for evoked averages
	'''
	#cov_eq = mne.compute_covariance(epochs,tmin=-0.1,tmax=0,method='empirical') # pre-revisions
	#cov_eq = mne.compute_covariance(epochs,tmin=-0.5,tmax=-0.4,method='empirical') #post revisions
	cov_eq = mne.compute_covariance(epochs,tmin=None,tmax=None,method='empirical') #post post revisions
	pickle.dump(cov_eq,open('TagInfRed/meg/%s/%s-cov_eq' %(subject,subject1),'wb'))
	info_eq = epochs.info
	pickle.dump(info_eq,open('TagInfRed/meg/%s/%s-info_eq' %(subject,subject1),'wb'))
	src = mne.setup_source_space(subject=subject,spacing='ico4',subjects_dir='TagInfRed/mri')
	mne.write_source_spaces(subjects_dir + '/%s/bem/%s-ico-4-src.fif' %(subject,subject1),src,overwrite=True) 

	fwd_eq = mne.make_forward_solution(info_eq, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	fwd_eq = mne.convert_forward_solution(fwd_eq,force_fixed=True)
	mne.write_forward_solution('TagInfRed/meg/%s/%s-fwd_eq.fif'  %(subject,subject1),fwd_eq,overwrite=True) 
	inv_eq = mne.minimum_norm.make_inverse_operator(info_eq, fwd_eq, cov_eq, depth=None, loose=0,fixed=True)
	pickle.dump(inv_eq,open('TagInfRed/meg/%s/%s-inv_eq' %(subject,subject1),'wb'))


	'''
	####reading everything in after it's been written
	#src = mne.read_source_spaces(subjects_dir + '/%s/bem/%s-ico-4-src.fif' %(subject,subject))
	cov = eelbrain.load.unpickle('TagInfRed/meg/%s/%s-cov' %(subject,subject))
	#info_eq = eelbrain.load.unpickle('TagInfRed/meg/%s/%s-info_eq' %(subject,subject))
	#cov_eq = eelbrain.load.unpickle('TagInfRed/meg/%s/%s-cov_eq' %(subject,subject))
	info = eelbrain.load.unpickle('TagInfRed/meg/%s/%s-info' %(subject,subject))
	fwd = mne.read_forward_solution('TagInfRed/meg/%s/%s-fwd.fif'  %(subject,subject))
	fwd = mne.convert_forward_solution(fwd,force_fixed=True)
	inv = eelbrain.load.unpickle('TagInfRed/meg/%s/%s-inv' %(subject,subject))
	#fwd_eq = mne.read_forward_solution('TagInfRed/meg/%s/%s-fwd_eq.fif'  %(subject,subject))
	#fwd_eq = mne.convert_forward_solution(fwd_eq,force_fixed=True)
	#inv_eq = eelbrain.load.unpickle('TagInfRed/meg/%s/%s-inv_eq' %(subject,subject))
	#'''

	conditions = [ev_pseudo_nontransp, ev_pseudo_transp, ev_reduplicate,ev_morph_complex, ev_morph_simple,ev_phonemic_in,ev_infix_in]
	#conditions = [ev_pseudo_nontransp_av, ev_pseudo_transp_av, ev_reduplicate_av,ev_morph_complex_av, ev_morph_simple_av,ev_phonemic_in_av,ev_infix_in_av]

	filenames = ['pseudo_nontransp', 'pseudo_transp', 'reduplicate', 'morph_complex', 'morph_simple','phonemic_in','infix_in']
	i = 0

	############sanity check for seeing if evokeds and single trials produce the same value
	'''
	src = mne.read_source_spaces('TagInfRed/mri/fsaverage/bem/fsaverage-ico-4-src.fif')
	lambda2 = 1.0 / 3.0 ** 2
	parc = mne.read_labels_from_annot('fsaverage','tark_stringType_binary2',subjects_dir='TagInfRed/mri',hemi='lh')
	label = [i for i in parc if i.name.startswith('tark_stringType_binary2-lh')][0]
	#parc = mne.read_labels_from_annot('%s' %subject,parc='PALS_B12_Brodmann',subjects_dir=subjects_dir,hemi='lh')
	#label = [i for i in parc if i.name.startswith('Brodmann.42')][0]
	inverse_operator = eelbrain.load.unpickle('TagInfRed/meg/%s/%s-inv_3snr' %(subject,subject))
	evoked = epochs['morph_simple_in'].average()
	stcs = apply_inverse_epochs(epochs['morph_simple_in'], inverse_operator, lambda2, "dSPM",nave=epochs['morph_simple_in'].average().nave,verbose=True)
	subject_from = subject
	src_from = mne.read_source_spaces('TagInfRed/mri/%s/bem/%s-ico-4-src.fif' %(subject,subject))
	subject_to = 'fsaverage'
	#morph = mne.compute_source_morph(src_from, subject_from, subject_to, spacing=4, subjects_dir=subjects_dir)
	

	#stcs_morphed = morph_stcs_in_list(morph,stcs)
	
	stcs_morphed = []
	counter = 0
	for stc in stcs: 
		morph = mne.compute_source_morph(stc, subject_from, subject_to, spacing=4, subjects_dir=subjects_dir,verbose=True)
		stc_morphed = morph.apply(stc)	
		stcs_morphed.append(stc_morphed)
		counter = counter+1
		print(counter)
	
	stcs = stcs_morphed
	#mean_stc = sum(stcs_morphed) / len(stcs_morphed)
	mean_stc = sum(stcs) / len(stcs)
	mean_stc = mean_stc.in_label(label)
	flip = mne.label_sign_flip(label, inverse_operator['src'])
	label_mean = np.mean(mean_stc.data, axis=0)
	label_mean_flip = np.mean(flip[:, np.newaxis] * mean_stc.data, axis=0)

	evoked = epochs['morph_simple_in'].average()
	stc_evoked = apply_inverse(evoked, inverse_operator, lambda2, "dSPM",verbose=True)
	morph = mne.compute_source_morph(stc_evoked, subject_from, subject_to, spacing=4, subjects_dir=subjects_dir, verbose=True)
	stc_morphed = morph.apply(stc_evoked)
	stc_evoked_label = stc_morphed.in_label(label)
	#stc_evoked_label = stc_evoked.in_label(label)
	label_mean_evoked = np.mean(stc_evoked_label.data, axis=0)

	times = 1e3 * stcs[0].times  # times in ms

	plt.figure()
	h0 = plt.plot(times, mean_stc.data.T, 'k')
	h1, = plt.plot(times, label_mean, 'r', linewidth=3)
	h2, = plt.plot(times, label_mean_flip, 'g', linewidth=3)
	plt.legend((h0[0], h1, h2), ('all dipoles in label', 'mean',
                             'mean with sign flip'))
	plt.xlabel('time (ms)')
	plt.ylabel('dSPM value')
	plt.show()

	###
	plt.figure()
	for k, stc_trial in enumerate(stcs):
		plt.plot(times, np.mean(stc_trial.data, axis=0).T, 'k--',label='Single Trials' if k == 0 else '_nolegend_',alpha=0.5)

	# Single trial inverse then average.. making linewidth large to not be masked
	plt.plot(times, label_mean_flip, 'b', linewidth=6,label='dSPM first, then average')

	# Evoked and then inverse
	plt.plot(times, label_mean_evoked, 'r', linewidth=2,label='Average first, then dSPM')

	plt.xlabel('time (ms)')
	plt.ylabel('dSPM value')
	plt.legend()
	plt.show()
	'''

	for cond in conditions:
		#'''
		###for epoch stcs
		if filenames[i] == 'morph_simple':
			mynave = ev_morph_simple_av.nave
		elif filenames[i] == 'morph_complex':
			mynave = ev_morph_complex_av.nave
		else:		
			myepochs = epochs[filenames[i]].average()
			mynave = myepochs.nave
		eps = make_epoch_stcs(cond,mynave)
		a = 1
		for ep in eps:
			ep.save('TagInfRed/stc/%s%s%s' %(subject,filenames[i],a))
			a = a+1
		i = i+1
		
		###for average stcs
		'''
		lambda2 = 1.0 / 3.0 ** 2
		#lambda2 = 1.0 / 2.0 ** 2.0
		my_stc = mne.minimum_norm.apply_inverse(cond,inv_eq,lambda2=lambda2,verbose=False,method='dSPM')
		if i == 0:
			subject_from = subject
			subject_to = 'fsaverage'
			morph = mne.compute_source_morph(my_stc, subject_from, subject_to, spacing=4, subjects_dir=subjects_dir)
			#stc = mne.morph_data_precomputed(subject_from, subject_to, stc_from, vertices_to, morph_mat)
			stc_morphed = morph.apply(my_stc)
			stc_morphed.save('TagInfRed/average_stc_equalized_counts/%s%s' %(subject,filenames[i]))
		else:
			stc_morphed = morph.apply(my_stc)
			stc_morphed.save('TagInfRed/average_stc_equalized_counts/%s%s' %(subject,filenames[i]))
		i = i+1	
		###my_stc.save('TagInfRed/stc/%s%s' %(subject,filenames[i]))
		#'''


######make ICA
subjects = ['R022']
for s in subjects:
	subject = s
	subject1 = subject
	ica = ICA(n_components=0.95,method='fastica',random_state=42,max_iter=15000)
	#ica = ICA(n_components=0.95,method='fastica',random_state=42)
	raw = mne.io.read_raw_fif('TagInfRed/meg/%s/%s_TagInfRed-raw.fif' %(subject,subject1),preload=True)
	raw.filter(l_freq=0.1,h_freq=40,method='iir')
	#ica.fit(raw,reject = dict(mag=4e-12))
	ica.fit(raw)
	ica.plot_sources(raw)
        raw_input('Press enter to continue')   #python 2
	#input('Press enter to continue')  #python 3   
	raw=ica.apply(raw,exclude=ica.exclude)
	raw.save('TagInfRed/meg/%s/%s-ica2-raw.fif' %(subject,subject1), overwrite=True)
	del raw,ica 

#############Read in to DS##############################
#subjects = ['R001','R002','R006','R007','R008','R010','R011','R012','R014','R015','R016','R017','R020','R023','R024','R025','R026','R028','R029','R030','R203']
subjects_with_22 = ['R001','R002','R006','R007','R008','R010','R011','R012','R014','R015','R016','R017','R020','R022','R023','R024','R025','R026','R028','R029','R030','R203']
subjects_lmer = ['R001','R002','R006','R008','R010','R011','R012','R014','R015','R016','R017','R022','R023','R024','R025','R026','R028','R029','R030','R203']
subjects_lmer_no_22 = ['R001','R002','R006','R008','R010','R011','R012','R014','R015','R016','R017','R023','R024','R025','R026','R028','R029','R030','R203']
subjects_lmer_rebaseline = ['R001','R002','R006','R007','R008','R010','R011','R014','R015','R016','R017','R020','R022','R023','R024','R025','R028','R029','R030','R203']

subjects = subjects_lmer_rebaseline
my_stc_names = ['infix_in', 'morph_complex', 'morph_simple', 'phonemic_in', 'pseudo_nontransp', 'pseudo_transp', 'reduplicate']
stcs,subject,cond = [],[],[]
for sbj in subjects:
	#stc_path = 'TagInfRed/average_stc_equalized_counts/%s' %sbj
	stc_path = 'average_stc_equalized_counts_master/average_stc_equalized_counts/%s' %sbj
	for i in my_stc_names:
		stc = mne.read_source_estimate(stc_path + i + '-lh.stc')
		#####################################################################stc = mne.read_source_estimate(stc_path + i + '-rh.stc')
		stcs.append(stc)
		cond.append(str.split(i,'%s' %sbj)[0]) 
		subject.append(sbj)
		del stc
		print ("done!")



ds = eelbrain.Dataset()
#ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='TagInfRed/mri',method='dSPM',fixed=True,parc='aparc')
ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='mri',method='dSPM',fixed=True,parc='aparc')
ds['Condition'] = eelbrain.Factor(cond)
ds['Subject'] = eelbrain.Factor(subject,random=True)

'''
tstart = .0
tstop = .3
newtime = ds['stc']
mytime = newtime.sub(time=(tstart,tstop))
ds['stc']=mytime
'''

src = ds['stc']
#src.source.set_parc('tark_stringType_binary2') #eelbrain 14
src = eelbrain.set_parc(src,parc='tark_stringType_binary2') #eelbrain 30
#src = eelbrain.set_parc(src,parc='tark_stringType_binary2_attempt_to_do_other_hemi') #eelbrain 30
#src.source.set_parc('tark_stringType_binary2_attempt_to_do_other_hemi')
src_region = src.sub(source='tark_stringType_binary2-lh')
#src_region = src.sub(source='tark_stringType_binary2-rh')
ds['stc']=src_region


#######generate chart of time course activity averaged by condition
timecourse = ds['stc'].mean('source')
#timecourse = src_region.mean('source')
activation = eelbrain.plot.UTSStat(timecourse,'Condition',match='Subject',ds=ds,xlim=(-0.15,.3),legend='upper right', title='Tark type 2 - left hemisphere (no baseline correct') #% is the

eelbrain.plot.UTSStat(timecourse,'Condition',match='Subject',ds=ds,xlim=(-0.05,.3),legend='upper right', title='Tark type 2 - left hemisphere (no baseline correct') #% is the


test = eelbrain.plot.UTS(timecourse,'Condition',ds=ds,xlim=(0.00,.3),legend='upper right', title='Tark type 2 - left hemisphere')


#the following doesn't work
fs_src = mne.read_source_spaces('TagInfRed/mri/fsaverage/bem/fsaverage-ico-4-src.fif')
parc = mne.read_labels_from_annot('fsaverage','tark_stringType_binary2',subjects_dir='TagInfRed/mri',hemi='lh')
label = [i for i in parc if i.name.startswith('tark_stringType_binary2-lh')][0]
act = mne.extract_label_time_course(stcs,label,src=fs_src,mode='mean')


plt.plot(timecourse.time,timecourse[0],color='red')
plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('VFWA Averaged Source Activity - n=20')
#plt.axvline(tstart,color='lightgrey',alpha=2)
plt.pyplot.xlim(xmin=0)
#plt.savefig('vwfa_all_together.png')
plt.clf()
