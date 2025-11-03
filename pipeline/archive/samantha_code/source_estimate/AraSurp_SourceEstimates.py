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

class AraSurp(eelbrain.MneExperiment):
	path_version = 1 #can be 1 or 0 depending on folder organization
    #trigger_shift = 0.03 #to be added if delay with photodiode
	sessions='AraSurp' #name in file before R000..
	defaults = {'experiment': 'AraSurp', #name of your exp
		#'raw': '0-40', #raw data is selected for 0-40Hz. IF FILTERED DURING ICA: 'raw':'raw'
		'raw':'raw',
		'rej': 'man', #manual rejection of epochs
		'epoch': 'epoch',
		'inv': 'fixed-2-dSPM'} #analysis with free dipole orientation. #the number indicates expected signal to noise ratio: 3 for ttest (and anova) and 2 for regression
	groups = {'good': ('Y0310','Y0312','Y0315','Y0316','Y0318','Y0319','Y0320','Y0321','Y0322','Y0323','Y0324','Y0325','Y0326','Y0327')}
	#groups = {'good':('Y0317')}	
	epoch_default = {'tmin':-0.5, 'tmax': 1.5, 'decim': 5, 'baseline': (-0.4,-0.2)}
	#tmin=-0.5,tmax=1.5,baseline=(-0.4,-0.2)
	#variables = {'myvariable' : {(64) : 'R_HH_VIII', (34): 'R_LH_VIII'}}
	epochs={'epoch':{},  #this needs to be here: selects all epochs
		'cov': {'base': 'epoch', 'tmin': -0.5, 'tmax': 1.5}
	} #this needs to be here: defines the parameters of the covariance matrix
	parcs={'Temp': {'kind': 'combination',
		'base': 'aparc', #chose if you want to use "aparc" or "PALS_B12_Brodmann"
		'labels': {'temp-lh':'middletemporal+superiortemporal'}
                        #define the hemisphere (after the '-') and then give the name tag (taken from base naming place)
	}
	tests = 
}
e = AraSurp('AraSurp')

e.make_rej()
#

event_id = dict(R_HH_VIII=64, R_LH_VIII=34, R_HL_VIII=41, R_LL_VIII=21, R_HH_VII=71, R_HL_VII=25, R_LH_VII=18, R_LL_VII=37,R_HH_I=7, R_LH_I=6, R_HL_I=5, R_LL_I=11)
#, N_LL_VIII=30, N_LH_VII=8, N_HH_VIII=16, N_LH_VIII=9, N_HL_VIII=10, , N_HH_VII=15, N_HL_VII=20,  N_LL_VII=4

#event_id_VIII = dict(R_HH_VIII=64, R_LH_VIII=34, R_HL_VIII=41, R_LL_VIII=21, N_HH_VIII=16, N_LH_VIII=9, N_HL_VIII=10, N_LL_VIII=30)

#event_id_VII = dict(R_HH_VII=71, R_HL_VII=25, R_LH_VII=18, R_LL_VII=37, N_HH_VII=15, N_HL_VII=20, N_LH_VII=8, N_LL_VII=4)

event_id_I = dict(R_HH_I=7, R_LH_I=6, R_HL_I=5, R_LL_I=11,N_LL_VII=76, N_HH_I=12, N_LH_I=14, N_HL_I=13, N_LL_I=76)
#event_id = dict(R_HH_VIII=64, R_LH_VIII=34, R_LL_VIII=21, R_HH_VII=71, R_HL_VII=25, R_LH_VII=78, R_LL_VII=37)


#subjects = ['Y0315','Y0320']
subjects = ['Y0328','Y0329']
#subjects = ['Y0318','Y0319','Y0320','Y0310','Y0315']
#do 321 separately, it chokes
ica = ICA(n_components=0.95,method='fastica',random_state=42)   
for s in subjects:
	subject = s
	subject1 = subject
	raw = mne.io.read_raw_fif('AraSurp/meg/%s/%s_AraSurp_NR-raw.fif' %(subject,subject1),preload=True)
	raw.filter(l_freq=0.1,h_freq=40,method='iir')
	ica.fit(raw)    
	raw=ica.apply(raw,exclude=ica.exclude)
	raw.save('AraSurp/meg/%s/%s-ica-raw.fif' %(subject,subject1))

subjects = ['Y0316','Y0322','Y023']
subject = 'Y0327'
subject1 = subject
raw = mne.io.read_raw_fif('AraSurp/meg/%s/%s_AraSurp-raw.fif' %(subject,subject1),preload=True)
#raw.info['bads'] = ['MEG 017', 'MEG 037', 'MEG 055', 'MEG 070', 'MEG 072', 'MEG 083', 'MEG 084', 'MEG 086', 'MEG 087', 'MEG 088', 'MEG 097', 'MEG 104', 'MEG 110', 'MEG 116', 'MEG 130', 'MEG 150', 'MEG 158', 'MEG 160', 'MEG 168']
#raw.interpolate_bads(reset_bads=False, verbose=False)
raw.filter(l_freq=0.1,h_freq=40,method='iir')

ica = ICA(n_components=0.95,method='fastica',random_state=42)   
ica.fit(raw)    
raw=ica.apply(raw,exclude=ica.exclude)


#subjects = ['Y0316','Y0322','Y0323']
event_id = dict(R_HH_VIII=64, R_LH_VIII=34, R_HL_VIII=41, R_LL_VIII=21, R_HH_VII=71, R_HL_VII=25, R_LH_VII=18, R_LL_VII=37)
subjects_dir = 'AraSurp/mri/'
subjects = ['Y0329']
for s in subjects:
	subject = s
	subject1 = subject
	raw = mne.io.read_raw_fif('AraSurp/meg/%s/%s-ica-raw.fif' %(subject,subject1),preload=True)
	events = mne.find_events(raw,min_duration=0.002)
	events_ = events
#events_[:,0] + 345
	events_[:,0] = events_[:,0] + 400 #includes 45/50 ms trigger to audio delay plus 370 ms start of audio to surprising phoneme

	#events_[5,2] = 41
	#events_[16,2] = 41
	#events_[21,2] = 41
	#events_[22,2] = 41
	#events_[31,2] = 41
	#events_[58,2] = 41
	#events_[62,2] = 41
	#events_[76,2] = 41
	#events_[114,2] = 41
	#events_[136,2] = 41
	#events_[177,2] = 41
	#events_[202,2] = 41
	#events_[221,2] = 41
	#events_[276,2] = 41
	#events_[297,2] = 41
	#events_[306,2] = 41
	#events_[337,2] = 41
	#events_[352,2] = 41

#event_id = dict(R_HH_VIII=64, R_LH_VIII=34, R_HL_VIII=41, R_LL_VIII=21, R_HH_VII=71, R_HL_VII=25, R_LH_VII=18, R_LL_VII=37)

	reject = dict(mag=4e-12)
	epochs = mne.Epochs(raw,events_,event_id,tmin=-0.5,tmax=.6,baseline=(-0.5,-0.4),reject=reject) #500 ms before event, and 1.5 seconds after?
	epochs.drop_bad()

#	ev_R_HH_VIII = epochs['R_HH_VIII'].average()
#	ev_R_LH_VIII = epochs['R_LH_VIII'].average()
#	ev_R_HL_VIII = epochs['R_HL_VIII'].average()
#	ev_R_LL_VIII = epochs['R_LL_VIII'].average()

	#ev_N_HH_VIII = epochs['N_HH_VIII'].average()
	#ev_N_LH_VIII = epochs['N_LH_VIII'].average()
	#ev_N_HL_VIII = epochs['N_HL_VIII'].average()
	#ev_N_LL_VIII = epochs['N_LL_VIII'].average()

#	epochs = mne.Epochs(raw,events_,event_id_VII,tmin=-0.5,tmax=1.5,baseline=(-0.45,-0.35),reject=reject) #500 ms before event, and 1.5 seconds after?
#	epochs.drop_bad()
#	ev_R_HH_VII = epochs['R_HH_VII'].average()
#	ev_R_LH_VII = epochs['R_LH_VII'].average()
#	ev_R_HL_VII = epochs['R_HL_VII'].average()
#	ev_R_LL_VII = epochs['R_LL_VII'].average()

	#ev_N_HH_VII = epochs['N_HH_VII'].average()
	#ev_N_LH_VII = epochs['N_LH_VII'].average()
	#ev_N_HL_VII = epochs['N_HL_VII'].average()
	#ev_N_LL_VII = epochs['N_LL_VII'].average()

	ev_R_HH_VIII = epochs['R_HH_VIII']
	ev_R_LH_VIII = epochs['R_LH_VIII']
	ev_R_HL_VIII = epochs['R_HL_VIII']
	ev_R_LL_VIII = epochs['R_LL_VIII']

	#ev_N_HH_VIII = epochs['N_HH_VIII'].average()
	#ev_N_LH_VIII = epochs['N_LH_VIII'].average()
	#ev_N_HL_VIII = epochs['N_HL_VIII'].average()
	#ev_N_LL_VIII = epochs['N_LL_VIII'].average()

#	epochs = mne.Epochs(raw,events_,event_id_VII,tmin=-0.5,tmax=1.5,baseline=(-0.4,-0.2),reject=reject) #500 ms before event, and 1.5 seconds after?
#	epochs.drop_bad()
	ev_R_HH_VII = epochs['R_HH_VII']
	ev_R_LH_VII = epochs['R_LH_VII']
	ev_R_HL_VII = epochs['R_HL_VII']
	ev_R_LL_VII = epochs['R_LL_VII']

	#ev_N_HH_VII = epochs['N_HH_VII'].average()
	#ev_N_LH_VII = epochs['N_LH_VII'].average()
	#ev_N_HL_VII = epochs['N_HL_VII'].average()
	#ev_N_LL_VII = epochs['N_LL_VII'].average()


	subject1=subject
	cov = mne.compute_covariance(epochs,tmin=-0.48,tmax=-0.38,method='empirical')
#mne.write_covariance('AraSurp/meg/%s/%s-cov.fif' %(subject,subject1),cov)
	pickle.dump(cov,open('AraSurp/meg/%s/%s-cov' %(subject,subject1),'wb'))


	info = epochs.info
	pickle.dump(info,open('AraSurp/meg/%s/%s-info' %(subject,subject1),'wb'))


	subject1 = subject
	trans = mne.read_trans('AraSurp/meg/%s/%s-trans.fif' %(subject1,subject)) 
	bem = glob.glob('AraSurp/mri/%s/bem/*-bem-sol.fif' %subject)[0]
#fname = 'AraSurp/meg/%s/%s-fwd.fif' %(subject,subject1)

	#subject_to = 'fsaverage'
	#fs = mne.read_source_spaces('AraSurp/mri' + '%s/bem/%s-ico-4-src.fif' % ('fsaverage', 'fsaverage'))
	#fsave_vertices = [s['vertno'] for s in src]
	#sample_vertices = [fs[0]['vertno'], fs[1]['vertno']]
	#morph_mat = mne.compute_morph_matrix(sbj, 'fsaverage', fsave_vertices, sample_vertices, subjects_dir)
	#src = mne.morph_data_precomputed(subject_from, fs, src_from, vertices_to, morph_mat)
	
	#vertices_to = [fs[0]['vertn'], fs[1]['vertno']]
	#vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir='AraSurp/mri/')
	#subject_from = subject
	# use the morph function
	#morph_mat = mne.compute_morph_matrix(subject_from, subject_to, stc_from.vertices, vertices_to=vertices_to, subjects_dir=subjects_dir)
	#src = mne.morph_data_precomputed(subject_from, subject_to, stc_from, vertices_to, morph_mat)

	src = mne.setup_source_space(subject=subject,spacing='ico4',subjects_dir='AraSurp/mri',overwrite=True)
	src_morph = mne.morph_source_spaces(src, subject_to='fsaverage', subjects_dir='AraSurp/mri')
	#mne.write_source_spaces('AraSurp/meg/%s/%s-src.fif' %(subject,subject1),src_morph,overwrite=True) 
	mne.write_source_spaces('AraSurp/meg/%s/%s-src.fif' %(subject,subject1),src_morph,overwrite=True) 
#mne.write_source_spaces('AraSurp/meg/%s/%s-src.fif' %(subject,subject1),src) 


	#fwd = mne.make_forward_solution(info, trans,src_morph,bem,meg=True,eeg=False,ignore_ref=True)
#fwd = mne.make_forward_solution(info, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	fwd = mne.make_forward_solution(info, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	fwd = mne.convert_forward_solution(fwd,force_fixed=True)
	mne.write_forward_solution('AraSurp/meg/%s/%s-fwd.fif'  %(subject,subject1),fwd,overwrite=True) 


# Inverse operator
	inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, loose=0,fixed=True)
	pickle.dump(inv,open('AraSurp/meg/%s/%s-epochs-inv' %(subject,subject1),'wb'))
	#lambda2 = 1.0 / 3.0 ** 2
	lambda2 = 1.0 / 2 ** 2


	
	inv = pickle.load(open('AraSurp/meg/%s/%s-epochs-inv' %(subject,subject1),"rb"))
	#conditions = [ev_R_HH_VIII, ev_R_LH_VIII, ev_R_HL_VIII, ev_R_LL_VIII,ev_R_HH_VII, ev_R_LH_VII, ev_R_HL_VII, ev_R_LL_VII,ev_N_HH_VIII, ev_N_LH_VIII, ev_N_HL_VIII, ev_N_LL_VIII,ev_N_HH_VII, ev_N_LH_VII, ev_N_HL_VII, ev_N_LL_VII]
	conditions = [ev_R_HH_VIII, ev_R_LH_VIII, ev_R_HL_VIII, ev_R_LL_VIII,ev_R_HH_VII, ev_R_LH_VII, ev_R_HL_VII, ev_R_LL_VII]
	#filenames = ['_R_HH_VIII', '_R_LH_VIII', '_R_HL_VIII', '_R_LL_VIII','_R_HH_VII', '_R_LH_VII', '_R_HL_VII', '_R_LL_VII','_N_HH_VIII', '_N_LH_VIII', '_N_HL_VIII', '_N_LL_VIII','_N_HH_VII', '_N_LH_VII', '_N_HL_VII', '_N_LL_VII']
	filenames = ['_R_HH_VIII', '_R_LH_VIII', '_R_HL_VIII', '_R_LL_VIII','_R_HH_VII', '_R_LH_VII', '_R_HL_VII', '_R_LL_VII']
	#vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir='AraSurp/mri/')
	i = 0	
	for cond in conditions:
		eps = make_epoch_stcs(cond)
		#my_stc = mne.minimum_norm.apply_inverse(cond,inv,lambda2=lambda2,verbose=False,method='dSPM')
		#my_stc = mne.minimum_norm.apply_inverse_epochs(cond,inv,lambda2=lambda2,verbose=False,method='dSPM')
		#morph_mat = mne.compute_morph_matrix(subject_from, subject_to,my_stc.vertices, vertices_to,subjects_dir='AraSurp/mri/')
		#stc_morphed = mne.morph_data_precomputed(subject_from=subject, subject_to='fsaverage',stc_from=my_stc, grade=vertices_to,morph_mat)
		#stc_morphed = mne.morph_data(subject_from=subject, subject_to='fsaverage',stc_from=my_stc, grade=vertices_to,subjects_dir='AraSurp/mri')
	#stc_morphed.save('AraSurp/stc/%s%s' %(subject,filename))
		a = 1
		for ep in eps:		
			ep.save('AraSurp/stc/%s%s%s' %(subject,filenames[i],a))
			a = a+1	
		i = i+1

def make_epoch_stcs(epochs, snr = 2.0, method='dSPM', morph=True, save_to_disk = False):                           
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
		subject_from = subject
	
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


#temporarily here
vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir='AraSurp/mri/') #fsaverage's source space
cond = ev_R_HH_VIII
my_stc = mne.minimum_norm.apply_inverse(cond,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_morphed = mne.morph_data(subject_from=subject, subject_to='fsaverage',stc_from=my_stc, grade=vertices_to,subjects_dir='AraSurp/mri/')
stc_morphed.save('AraSurp/stc/%s%s' %(subject,"ev_R_HH_VIII"))
cond = ev_R_LH_VIII
my_stc = mne.minimum_norm.apply_inverse(cond,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_morphed = mne.morph_data(subject_from=subject, subject_to='fsaverage',stc_from=my_stc, grade=vertices_to,subjects_dir='AraSurp/mri/')
stc_morphed.save('AraSurp/stc/%s%s' %(subject,"ev_R_LH_VIII"))

activation = eelbrain.plot.UTSStat(stc_morphed, sub=subject, legend='lower left')

'''
'''


#label = [i for i in parc if i.name.startswith('LOBE.TEMPORAL-lh')][0]
 #means his data looks like: subj_prime_task_soa.stc



#subjects = ['Y0321','Y0327']
#subjects = ['Y0310','Y0312','Y0316','Y0318','Y0319','Y0320','Y0321','Y0322','Y0323','Y0324','Y0325','Y0326','Y0327']
subjects_70_acc = ['R0157','R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0350','R0351','R0352','R0353','R0356','R0357']
subjects_70_epochdrop_acc = ['R0157','R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0351','R0352','R0353','R0357']
subjects_75_acc = ['R0157','R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0350','R0353','R0358','R0359']
subjects_75_epochdrop_acc = ['R0157','R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0353','R0358','R0359']
subjects_all = ['R0157','R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0350','R0351','R0352','R0353','R0333','R0334','R0347','R0355','R0324','R0356','R0357','R0358','R0359']

subjects_temp = ['R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0351','R0352','R0353','R0357','R0358','R0359']

subjects_gofish = ['R0157','R0215','R0318','R0319','R0320','R0321','R0322','R0323','R0327','R0329','R0345','R0346','R0348','R0349','R0353','R0358','R0359']

subjects = subjects_75_epochdrop_acc

my_stc_names = ['Hroot_Hlin_I-lh.stc','Hroot_Hlin_VIII-lh.stc','Hroot_Hlin_VII-lh.stc','Hroot_Llin_I-lh.stc','Hroot_Llin_VIII-lh.stc','Hroot_Llin_VII-lh.stc','Lroot_Hlin_I-lh.stc','Lroot_Hlin_VIII-lh.stc','Lroot_Hlin_VII-lh.stc','Lroot_Llin_I-lh.stc','Lroot_Llin_VIII-lh.stc','Lroot_Llin_VII-lh.stc']

my_stc_names = ['Hroot_Hlin_VIII-lh.stc','Hroot_Hlin_VII-lh.stc','Hroot_Llin_VIII-lh.stc','Hroot_Llin_VII-lh.stc','Lroot_Hlin_VIII-lh.stc','Lroot_Hlin_VII-lh.stc','Lroot_Llin_VIII-lh.stc','Lroot_Llin_VII-lh.stc']

my_stc_names = ['Hroot_Hlin_I-lh.stc','Hroot_Llin_I-lh.stc','Lroot_Hlin_I-lh.stc','Lroot_Llin_I-lh.stc']
#my_stc_names = ['Hroot_Hlin_I-lh.stc','Hroot_Llin_I-lh.stc','Lroot_Hlin_I-lh.stc','Lroot_Llin_I-lh.stc']

my_stc_names = ['Hroot_Hlin_I-lh.stc','Hroot_Llin_I-lh.stc','Lroot_Hlin_I-lh.stc','Lroot_Llin_I-lh.stc','Hroot_Hlin_VII-lh.stc','Hroot_Llin_VII-lh.stc','Lroot_Hlin_VII-lh.stc','Lroot_Llin_VII-lh.stc','Hroot_Hlin_VIII-lh.stc','Hroot_Llin_VIII-lh.stc','Lroot_Hlin_VIII-lh.stc','Lroot_Llin_VIII-lh.stc']

stcs_I, stcs_VII, stcs_VIII, rootsurp, linsurp, binyan, subject = [],[],[],[],[],[],[]

for sbj in subjects:
    #epochs = mne.read_epochs('AraSurp/meg/%s/%s-epo.fif' %(sbj,sbj)) #uncomment this to read in
    #print epochs
    stc_path = 'AraSurp/stc_notriggershift/%s_' %sbj 
    #labels = [i for i in os.listdir(stc_path) if i.endswith('-lh.stc')]
    for i in my_stc_names:
        stc = mne.read_source_estimate(stc_path + i)
	if str.split(i,'_')[2].strip("-lh.stc") == "I":
        	stcs_I.append(stc)
	elif str.split(i,'_')[2].strip("-lh.stc") == "VII":
		stcs_VII.append(stc)
	else:
		stcs_VIII.append(stc)
        rootsurp.append(str.split(i,'_')[0])
	#if i[2] == 'H':
	#	rootsurp.append('HighRoot')
	#elif i[2] == 'L':
	#	rootsurp.append('LowRoot')
	#if i[3] == 'H':
	#	linsurp.append('HighLinear')
	#elif i[3] == 'L':
	#	linsurp.append('LowLinear')
	#new = i[3]+"l"
        linsurp.append(str.split(i,'_')[1])
        binyan.append(str.split(i,'_')[2].strip("-lh.stc"))
        subject.append(sbj)
        del stc
	print "done!"


ds = eelbrain.Dataset()
#for subject in subjects:
#ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='AraSurp/mri',method='dSPM',fixed=True,parc='PALS_B12_Brodmann')
ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='AraSurp/mri',method='dSPM',fixed=True,parc='aparc')
#ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir,method='dSPM',fixed=True,parc='aparc')
ds['RootSurp'] = eelbrain.Factor(rootsurp)
ds['LinearSurp'] = eelbrain.Factor(linsurp)
ds['Binyan'] = eelbrain.Factor(binyan)
ds['Subject'] = eelbrain.Factor(subject,random=True)


src = ds['stc']
#src.source.set_parc('PALS_B12_Brodmann')
src.source.set_parc('AudCortex')
src_region = src.sub(source='transverse_and_superior-lh') #reducing the ds toc

src = ds['stc']
src.source.set_parc('AudCortex_broddman')
src_region = src.sub(source='brodmann_41_42-lh')
ds['stc']=src_region

src = ds['stc']
src.source.set_parc('AudCortex_broddman_with22')
src_region = src.sub(source='brodmann_41_42_22-lh')
ds['stc']=src_region


src = ds['stc']
src_region = src.sub(source='superiortemporal-lh')
ds['stc']=src_region

tstart = .39
tstop = .69
newtime = ds['stc']
mytime = newtime.sub(time=(tstart,tstop))
ds['stc']=mytime

timecourse = ds['stc'].mean('source')
#activation = eelbrain.plot.UTSStat(timecourse,'RootSurp % LinearSurp',xlim=(tstart,tstop),match='Subject',ds=ds,legend='upper right', title='STG - VIII - n=22 - C1 onset') #% is the
plt.plot(timecourse.time,timecourse[0],color='red')
plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('STG - I - n=22 - C3 onset')
plt.axvline(tstart,color='lightgrey',alpha=2)
#plt.xlim = tstart
plt.savefig('onset_m100_STG_I_n=22_C3.png')
plt.clf()


res = eelbrain.testnd.anova(ds['stc'], X='RootSurp*LinearSurp',ds=ds,match='Subject',pmin=0.05, tstart=0.1, tstop=0.15, samples=10000, mintime=0.01) #the .mea

stc_lowlinear = mne.read_source_estimate('AraSurp/stc/%s_Llin-lh.stc' %subj)
stc_highlinear = mne.read_source_estimate('AraSurp/stc/%s_Hlin-lh.stc' %subj)
tl_lowlinear = stc_lowlinear.extract_label_time_course(label,src=src,mode='mean')
tl_highlinear = stc_highlinear.extract_label_time_course(label,src=src,mode='mean')
print "plotting timecourse..."
plt.plot(src.time,timecourse[0],color='purple')
plt.plot(stc_lowlinear.times,tl_lowlinear[0],color='green',label='lowroot')
plt.axvline(0,color='lightgrey',alpha=2)
plt.xlim = tstart
plt.legend(loc=0)
plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Auditory Cortex - Linear Surprisal')
plt.savefig('AraSurp/%s_linear_surprisal.png' %subj)
plt.clf()

#res = eelbrain.testnd.anova(ds['stc'].mean('source'), X='Binyan*RootSurp*LinearSurp',ds=ds,match='Subject',pmin=0.05, tstart=0.03, tstop=1.0, samples=10000, mintime=0.01) #the .mean('source' here is because i'm doing an ROI test: i'm not looking for space

res = eelbrain.testnd.anova(ds['stc'].mean('source'), X='RootSurp*LinearSurp',ds=ds,sub=(ds['Binyan']=='I'),match='Subject',pmin=0.05, tstart=0.2, tstop=0.5, samples=10000, mintime=0.01) #the .mean('source' here is because i'm doing an ROI test: i'm not looking for space

res = eelbrain.testnd.anova(ds['stc'].mean('source'), X='RootSurp*LinearSurp',ds=ds,sub=(ds['Binyan']=='VII'),match='Subject',pmin=0.05, tstart=0.4, tstop=0.7, samples=10000, mintime=0.01) #the .mean('source' here is because i'm doing an ROI test: i'm not looking for space

res = eelbrain.testnd.anova(ds['stc'].mean('source'), X='RootSurp*LinearSurp',ds=ds,sub=(ds['Binyan']=='VIII'),match='Subject',pmin=0.05, tstart=0.4, tstop=0.7, samples=10000, mintime=0.01) #the .mean('source' here is because i'm doing an ROI test: i'm not looking for space


FIND ME

#res = eelbrain.testnd.anova(ds['stc'].mean('source') , X='RootSurp*LinearSurp*Binyan',ds=ds,match='Subject',pmin=0.05, tstart=0.00, tstop=0.4, samples=10000, mintime=0.01,minsource=10)

audcortex = [i for i in parc if (i.name == 'transversetemporal-lh' or i.name == 'superiortemporal-lh')]
audcortex = [audcortex[0] + audcortex[1]]
audcortex[0].name = 'transverse_and_superior'
mne.write_labels_to_annot(audcortex, subject='fsaverage',parc='AudCortex',subjects_dir=subjects_dir,overwrite=True)


left_hemi = [i for i in parc]
left_hemi=[left_hemi[0]+left_hemi[1]+left_hemi[2]+left_hemi[3]+left_hemi[4]+left_hemi[5]+left_hemi[6]]


parc = mne.read_labels_from_annot('fsaverage',parc='aparc',subjects_dir='AraSurp/mri',hemi='lh')
#parc = [i for i in parc if i.name.startswith('Brodmann.41-lh')]


parc = mne.read_labels_from_annot('fsaverage',parc='AudCortex_broddman',subjects_dir='AraSurp/mri',hemi='lh')
src = ds['stc']
src_region = src.sub(source='brodmann_41_42-lh')
ds['stc']=src_region
timecourse = src_region.mean('source')

###make a bar chart of a cluster

tstart = res.clusters[0]['tstart']
tstop = res.clusters[0]['tstop']
ds['average_source_activation'] = timecourse.mean(time=(tstart,tstop))
activation_barplot = eelbrain.plot.Barplot(ds['average_source_activation'],'RootSurp%LinearSurp',match='Subject',ds=ds, sub=(ds['Binyan']=='VIII'), title='Auditory Cortex - Root and Linear Surp cluster activity - Bin VIII') 


#parc = mne.read_labels_from_annot('fsaverage',parc='PALS_B12_Brodmann',subjects_dir='AraSurp/mri',hemi='lh')
#audcortex_bm = [i for i in parc if (i.name == 'Brodmann.42-lh' or i.name == 'Brodmann.41-lh' or i.name == 'Brodmann.22-lh')]
#audcortex_bm = [audcortex_bm[0] + audcortex_bm[1] + audcortex_bm[2]]
#audcortex_bm[0].name = 'brodmann_41_42_22'
#mne.write_labels_to_annot(audcortex_bm, subject='fsaverage',parc='AudCortex_broddman_with22',subjects_dir=subjects_dir,overwrite=True)

activation = eelbrain.plot.UTSStat(timecourse,'LinearSurp',match='Subject',ds=ds, sub=(ds['Binyan']=='I'),xlim=(0.0,.65),legend='lower left', title='Auditory Cortex - Linear Surp activity - Bin I') #% is the between model operator (not *)
activation.add_vspan(xmin=.16, xmax=.16,color='black', fill=False)                                                        
activation.add_vspan(xmin=.32, xmax=.349, color='lightgrey',zorder=-50)  
activation.add_vspan(xmin=.363, xmax=.4, color='lightgrey', zorder=-50)                                                                  
activation.save('AraSurp/cns_poster_binyanI_clusters_rootsurp.png')                                                           
activation.close()  

###grand average
from operator import add

tstart = .43
tstop = .57
stc_avg = reduce(add, stcs)
stc_avg /= len(stcs)
stc_avg.subject = 'fsaverage'
stc_avg.crop(tstart,tstop)
mydata = stc_avg.data1
myabsdata = np.absolute(mydata)
fmin = np.min(myabsdata)
fmax = np.max(myabsdata)
fmid = np.mean(myabsdata)
brain = stc_avg.plot(surface='inflated', hemi='split', subjects_dir='AraSurp/mri')

#colormap: fmin=-1.83e+00 fmid=0.00e+00 fmax=1.83e+00 transparent=0

brain = eelbrain.plot.brain.dspm(stc_avg_ndvar, fmin=fmid, fmax=fmax,surf='inflated')
stc_avg_ndvar = eelbrain.load.fiff.stc_ndvar(stc_avg,subject='fsaverage',src='ico-4',subjects_dir='AraSurp/mri',method='dSPM',fixed=True,parc='aparc')

brain.scale_data_colormap(fmin=-1.83e+00, fmid=fmid, fmax=1.83e+00, transparent=0)
brain.set_time(.5)


#eelbrain.plot.brain.cluster(ds['stc'].mean(time=(.3,.5))

#ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='AraSurp/mri/',method='dSPM',fixed=True,parc='aparc')

src = ds['stc']

subjects_dir='AraSurp/mri'
parc = mne.read_labels_from_annot('fsaverage',parc='aparc',subjects_dir=subjects_dir)
#parc = mne.read_labels_from_annot('fsaverage',parc='PALS_B12_Brodmann',subjects_dir=subjects_dir,hemi='lh')
#parc2 = [i for i in parc if i.name.startswith('Brodmann.42')]
left_hemi = [i for i in parc if i.name.endswith('lh')]
#left_hemi = [i for i in left_hemi1 if i not in parc2]
left_hemi=[left_hemi[0]+left_hemi[1]+left_hemi[2]+left_hemi[3]+left_hemi[4]+left_hemi[5]+left_hemi[6]]
left_hemi[0].name='left_hemi-lh'
mne.write_labels_to_annot(left_hemi, subject='fsaverage',parc='FullLeftHemisphere',subjects_dir=subjects_dir,overwrite=True)

ds['stc']=src #reset data to full space
#src.source.set_parc('FullLeftHemisphere') #dont do this man
src.source.set_parc('PALS_B12_Brodmann')
#src.source.set_parc('aparc')
#eelbrain.set_parc(src,'FullLeftHemisphere') #i said don't do this man
src_region = src.sub(source='lh') #reducing the ds to just the sources of interest. can also sub with time. DO THIS!!
ds['stc']=src_region

brain = eelbrain.plot.brain.cluster(src_region.mean('time'), subjects_dir=subjects_dir, surf='inflated')
brain.save_image('AraSurp/Left_hemisphere.png')
brain.close()


brain = eelbrain.plot.brain.brain(src, subjects_dir=subjects_dir, surf='inflated',cortex=(red))

brain = eelbrain.plot.brain.brain(src, subjects_dir=subjects_dir, surf='inflated',cortex=(red))



RootSurpLevels = ['L','H']
LinearSurpLevels = ['L','H']
#pmin = 0.05

for currentRS in RootSurpLevels:
#for currentLS in LinearSurpLevels:
        ds['stc']=src
        src.source.set_parc('AudCortex')
        src_region = src.sub(source='audcortex-lh')
        ds['stc']=src_region
        #res = eelbrain.testnd.ttest_ind('stc','Binyan',c0='VII',c1='VIII',ds=ds,sub=(ds['RootSurp']==currentRS) & (ds['LinearSurp']==currentLS),match='Subject',pmin=0.05,tstart=.076,tstop=0.097,samples=10000,mintime=0.001)
	res = eelbrain.testnd.ttest_ind(ds['stc'].mean('source'),'LinearSurp',c1='L',c0='H',ds=ds,sub=(ds['RootSurp']==currentLS),match='Subject',pmin=0.05,tstart=.055,tstop=0.07,samples=10000,mintime=0.001)
	#res = eelbrain.testnd.ttest_rel(ds['stc'].mean('source'),'RootSurp',ds=ds,sub=(ds['LinearSurp']==currentLS),match='Subject',pmin=0.05,tstart=0.129,tstop=0.141,samples=10000,mintime=0.001)
	print currentRS
	#print currentLS
	print res.clusters

    
#results for using related t-test:
#linear surp in every level for root surp
#Permutation test: 100%|███████| 8191/8191 [00:00<00:00, 10358.44 permutations/s]
#L
#id   tstart   tstop   duration   v         p          sig
#---------------------------------------------------------
#1    0.055    0.07    0.015      -42.225   0.010499   *  
#Permutation test: 100%|███████| 8191/8191 [00:00<00:00, 10302.74 permutations/s]
#H
#id   tstart   tstop   duration   v         p          sig
#---------------------------------------------------------
#1    0.055    0.07    0.015      -42.225   0.010499   *  

#root surp in every level for linear surp
#L
#id   tstart   tstop   duration   v   p   sig
#--------------------------------------------
#
#Permutation test: 100%|███████| 8191/8191 [00:00<00:00, 10193.26 permutations/s]
#H
#id   tstart   tstop   duration   v         p          sig
#---------------------------------------------------------
#1    0.056    0.07    0.014      -36.004   0.024905   *  

#linear surp for every level in root surp
#Permutation test: 100%|████████| 8191/8191 [00:00<00:00, 9898.73 permutations/s]
#L
#id   tstart   tstop   duration   v         p           sig
#----------------------------------------------------------
#1    0.076    0.099   0.023      -83.309   0.0041509   ** 
#Permutation test: 100%|████████| 8191/8191 [00:00<00:00, 9668.33 permutations/s]
#H
#id   tstart   tstop   duration   v         p           sig
#----------------------------------------------------------
#1    0.076    0.099   0.023      -83.309   0.0041509   ** 

#root surp in every level for linear surp
#L
#id   tstart   tstop   duration   v   p   sig
#--------------------------------------------
#
#Permutation test: 100%|███████| 8191/8191 [00:00<00:00, 10118.59 permutations/s]
#H
#id   tstart   tstop   duration   v         p           sig
#----------------------------------------------------------
#1    0.076    0.099   0.023      -80.208   0.0056159   ** 

#L
#id   tstart   tstop   duration   v        p           sig
#---------------------------------------------------------
#1    0.129    0.141   0.012      -38.42   0.0053717   ** 
#Permutation test: 100%|████████| 8191/8191 [00:00<00:00, 9959.27 permutations/s]
#H
#id   tstart   tstop   duration   v        p           sig
#---------------------------------------------------------
#1    0.129    0.141   0.012      -38.42   0.0053717   ** 

#L
#id   tstart   tstop   duration   v   p   sig
#--------------------------------------------
#Permutation test: 100%|███████| 8191/8191 [00:00<00:00, 10435.94 permutations/s]
#H
#id   tstart   tstop   duration   v         p          sig
#---------------------------------------------------------
#1    0.129    0.138   0.009      -21.518   0.039556   *  



#high linear surp? x any value for root surp?


#1    0.055    0.07    0.015      78.7626   0.0229   *     RootSurp x LinearSurp
#2    0.076    0.099   0.023      154.097   0.0075   **    RootSurp x LinearSurp
#3    0.129    0.141   0.012      53.9243   0.0399   *     RootSurp x LinearSurp



results = eelbrain.testnd.ttest_rel('stc', X='RootSurp', ds=ds,match='Subject', pmin=0.05, tstart=0.05, tstop=0.45, samples=1, mintime=0.01,minsource=10)

myresults = []
for sbj in subjects:
	oddoneout = 'Y0312'
	i = eelbrain.testnd.anova('stc', X='Binyan*RootSurp*LinearSurp',sub=(ds['Subject']!= oddoneout),ds=ds,match='Subject',pmin=0.05, tstart=0.05, tstop=0.5, samples=100, mintime=0.01, minsource=10)
	myresults.append(i)


with open("lmm_lookup_rootsurp.txt") as fin:
     rows = ( line.split('\t') for line in fin )
     rootsurpdict = { row[0]:row[1].strip('\n') for row in rows }
with open("lmm_lookup_linearsurp.txt") as fin:
     rows = ( line.split('\t') for line in fin )
     linearsurpdict = { row[0]:row[1].strip('\n') for row in rows }
with open("lmm_lookup_rootfreq.txt") as fin:
     rows = ( line.split('\t') for line in fin )
     rootfreqdict = { row[0]:row[1].strip('\n') for row in rows }
with open("lmm_lookup_wordfreq.txt") as fin:
     rows = ( line.split('\t') for line in fin )
     linearfreqdict = { row[0]:row[1].strip('\n') for row in rows }



# e orders
R_HH_VIII_order = ['HiRo_HiLin_VIII_2iftaEal','HiRo_HiLin_VIII_2irtaHal','HiRo_HiLin_VIII_2intaHab','HiRo_HiLin_VIII_2i0tamam','HiRo_HiLin_VIII_2iltaSaq','HiRo_HiLin_VIII_2intamaY','HiRo_HiLin_VIII_2iHtifaZ','HiRo_HiLin_VIII_2iHtajab','HiRo_HiLin_VIII_2i0ta
k','HiRo_HiLin_VIII_2ikta2ab','HiRo_HiLin_VIII_2intakas','HiRo_HiLin_VIII_2iftadaY','HiRo_HiLin_VIII_2ibtakar','HiRo_HiLin_VIII_2imtaEaD','HiRo_HiLin_VIII_2irtaTam','HiRo_HiLin_VIII_2ibtanaY','HiRo_HiLin_VIII_2iHta0am','HiRo_HiLin_VIII_2iktarav','HiRo_HiLin_VIII_2iEtazal','HiRo_HiLin_VIII_2iHtakar','HiRo_HiLin_VIII_2iqtabas','HiRo_HiLin_VIII_2intavar','HiRo_HiLin_VIII_2iktanaf','HiRo_HiLin_VIII_2i0tadad']
R_LH_VIII_order = ['LoRo_HiLin_VIII_2intawaY','LoRo_HiLin_VIII_2istalam','LoRo_HiLin_VIII_2irtawaY','LoRo_HiLin_VIII_2iltaHaq','LoRo_HiLin_VIII_2iftataH','LoRo_HiLin_VIII_2istamaE','LoRo_HiLin_VIII_2intasab','LoRo_HiLin_VIII_2iqtaSar','LoRo_HiLin_VIII_2ijtaraf','LoRo_HiLin_VIII_2intazaE','LoRo_HiLin_VIII_2irta0af','LoRo_HiLin_VIII_2iltamam','LoRo_HiLin_VIII_2ittaHad','LoRo_HiLin_VIII_2iltazam','LoRo_HiLin_VIII_2iEtaSar','LoRo_HiLin_VIII_2iHtasaY','LoRo_HiLin_VIII_2imtaraZ','LoRo_HiLin_VIII_2ittafaq','LoRo_HiLin_VIII_2ixtaTaf','LoRo_HiLin_VIII_2ibtada2','LoRo_HiLin_VIII_2ihtadaY','LoRo_HiLin_VIII_2ibtalaY','LoRo_HiLin_VIII_2iEtanaY','LoRo_HiLin_VIII_2iHtadad']
R_HL_VIII_order = ['HiRo_LoLin_VIII_2imtazaj','HiRo_LoLin_VIII_2iSTanaE','HiRo_LoLin_VIII_2istaHaq','HiRo_LoLin_VIII_2i0tahar','HiRo_LoLin_VIII_2irtasam','HiRo_LoLin_VIII_2ixtanaq','HiRo_LoLin_VIII_2iftaxar','HiRo_LoLin_VIII_2intaqaY','HiRo_LoLin_VIII_2iftaqad','HiRo_LoLin_VIII_2iEtaVar','HiRo_LoLin_VIII_2irtaxaS','HiRo_LoLin_VIII_2iHtafal','HiRo_LoLin_VIII_2izdaHam','HiRo_LoLin_VIII_2iktasaH','HiRo_LoLin_VIII_2intaqad','HiRo_LoLin_VIII_2ittaham','HiRo_LoLin_VIII_2ixtaraE','HiRo_LoLin_VIII_2intaqaS','HiRo_LoLin_VIII_2ikta0af','HiRo_LoLin_VIII_2irtamaY','HiRo_LoLin_VIII_2inta0al','HiRo_LoLin_VIII_2intabah','HiRo_LoLin_VIII_2iSTafaY','HiRo_LoLin_VIII_2iHtaDar']
R_LL_VIII_order = ['LoRo_LoLin_VIII_2irtafaE','LoRo_LoLin_VIII_2ihtazaz','LoRo_LoLin_VIII_2iZZalam','LoRo_LoLin_VIII_2i0taEal','LoRo_LoLin_VIII_2iltafaf','LoRo_LoLin_VIII_2iEtaqad','LoRo_LoLin_VIII_2ijtamaE','LoRo_LoLin_VIII_2intahaY','LoRo_LoLin_VIII_2ixtafat','LoRo_LoLin_VIII_2ibtaEad','LoRo_LoLin_VIII_2ixtabar','LoRo_LoLin_VIII_2iftakar','LoRo_LoLin_VIII_2iHtawaY','LoRo_LoLin_VIII_2intaZar','LoRo_LoLin_VIII_2iftarar','LoRo_LoLin_VIII_2iTTarad','LoRo_LoLin_VIII_2iHtaram','LoRo_LoLin_VIII_2iEtamad','LoRo_LoLin_VIII_2iqtaraH','LoRo_LoLin_VIII_2iHtimal','LoRo_LoLin_VIII_2izdarad','LoRo_LoLin_VIII_2intaZam','LoRo_LoLin_VIII_2iHtaqar','LoRo_LoLin_VIII_2irtabaT']
R_HH_VII_order = ['HiRo_HiLin_VII_2inxaSam','HiRo_HiLin_VII_2inHafar','HiRo_HiLin_VII_2infaqaS','HiRo_HiLin_VII_2indabag','HiRo_HiLin_VII_2inHaVaf','HiRo_HiLin_VII_2insaTal','HiRo_HiLin_VII_2inxaVal','HiRo_HiLin_VII_2infa00','HiRo_HiLin_VII_2insafar','HiRo_HiLin_VII_2indavar','HiRo_HiLin_VII_2infaqaE','HiRo_HiLin_VII_2infalaE','HiRo_HiLin_VII_2infaTar','HiRo_HiLin_VII_2inbaTaH','HiRo_HiLin_VII_2inkafa2','HiRo_HiLin_VII_AinsaqaY','HiRo_HiLin_VII_2inbatar','HiRo_HiLin_VII_2infalat','HiRo_HiLin_VII_2inqa0aE','HiRo_HiLin_VII_2inHaSar']
R_HL_VII_order = ['HiRo_LoLin_VII_2indaEas','HiRo_LoLin_VII_2inEakas','HiRo_LoLin_VII_2inqaTaE','HiRo_LoLin_VII_2in0aqq','HiRo_LoLin_VII_2inqasam','HiRo_LoLin_VII_2inEazal','HiRo_LoLin_VII_2inqabaD','HiRo_LoLin_VII_2in0all','HiRo_LoLin_VII_2inTafa2','HiRo_LoLin_VII_2inkasar','HiRo_LoLin_VII_2inxaraT','HiRo_LoLin_VII_2inxanaq','HiRo_LoLin_VII_2inqahar','HiRo_LoLin_VII_2inxadaE','HiRo_LoLin_VII_2inqaDD','HiRo_LoLin_VII_2indaha0','HiRo_LoLin_VII_2inkama0','HiRo_LoLin_VII_2indafaE','HiRo_LoLin_VII_2inmaHaY','HiRo_LoLin_VII_2inzalaq','HiRo_LoLin_VII_Ain0adah','HiRo_LoLin_VII_2infaEal','HiRo_LoLin_VII_2inbahar','HiRo_LoLin_VII_2in0add']
R_LH_VII_order = ['LoRo_HiLin_VII_Ainsakat','LoRo_HiLin_VII_2inhazam','LoRo_HiLin_VII_AinqaSS','LoRo_HiLin_VII_2inTaraH','LoRo_HiLin_VII_2inhalak','LoRo_HiLin_VII_AinsamaE','LoRo_HiLin_VII_2infakk','LoRo_HiLin_VII_2inqaraD','LoRo_HiLin_VII_2indalaE','LoRo_HiLin_VII_Ainball','LoRo_HiLin_VII_2indaras','LoRo_HiLin_VII_2insalax','LoRo_HiLin_VII_2inqadd','LoRo_HiLin_VII_2inhawaY','LoRo_HiLin_VII_2infaraj','LoRo_HiLin_VII_AinHasad']
R_LL_VII_order = ['LoRo_LoLin_VII_2inTabaE','LoRo_LoLin_VII_2inzaEaj','LoRo_LoLin_VII_2insakab','LoRo_LoLin_VII_2inkatab','LoRo_LoLin_VII_2inqalaE','LoRo_LoLin_VII_2inxalaE','LoRo_LoLin_VII_2inHaraf','LoRo_LoLin_VII_2inzaraE','LoRo_LoLin_VII_AinxaTab','LoRo_LoLin_VII_2inxaTaf','LoRo_LoLin_VII_2injaVab','LoRo_LoLin_VII_2inSaraf','LoRo_LoLin_VII_2inSabag','LoRo_LoLin_VII_2inSalaH','LoRo_LoLin_VII_2injaraf','LoRo_LoLin_VII_2inTAE','LoRo_LoLin_VII_2insaraq','LoRo_LoLin_VII_AinHall','LoRo_LoLin_VII_2inhamal','LoRo_LoLin_VII_2inTamm','LoRo_LoLin_VII_2inHaTT','LoRo_LoLin_VII_2inVahal','LoRo_LoLin_VII_2injalaY','LoRo_LoLin_VII_2inzawaY']

#c/d orders
#R_LL_VIII_order = ['LoRo_LoLin_VIII_2i0taEal','LoRo_LoLin_VIII_2iEtaqad','LoRo_LoLin_VIII_2ixtabar','LoRo_LoLin_VIII_2iftakar','LoRo_LoLin_VIII_2iHtaram','LoRo_LoLin_VIII_2iEtamad','LoRo_LoLin_VIII_2iqtaraH','LoRo_LoLin_VIII_2intahaY','LoRo_LoLin_VIII_2iftarar','LoRo_LoLin_VIII_2ijtamaE','LoRo_LoLin_VIII_2iZZalam','LoRo_LoLin_VIII_2irtafaE','LoRo_LoLin_VIII_2ixtafat','LoRo_LoLin_VIII_2ihtazaz','LoRo_LoLin_VIII_2iltafaf','LoRo_LoLin_VIII_2iHtimal','LoRo_LoLin_VIII_2irtabaT','LoRo_LoLin_VIII_2ibtaEad','LoRo_LoLin_VIII_2iTTarad','LoRo_LoLin_VIII_2intaZar','LoRo_LoLin_VIII_2intaZam','LoRo_LoLin_VIII_2izdarad','LoRo_LoLin_VIII_2iHtaqar','LoRo_LoLin_VIII_2iHtawaY']
#R_LH_VIII_order = ['LoRo_HiLin_VIII_2iltaHaq','LoRo_HiLin_VIII_2ittaHad','LoRo_HiLin_VIII_2imtaraZ','LoRo_HiLin_VIII_2intasab','LoRo_HiLin_VIII_2iEtanaY','LoRo_HiLin_VIII_2iHtadad','LoRo_HiLin_VIII_2ibtada2','LoRo_HiLin_VIII_2ixtaTaf','LoRo_HiLin_VIII_2intazaE','LoRo_HiLin_VIII_2iltazam','LoRo_HiLin_VIII_2istamaE','LoRo_HiLin_VIII_2ihtadaY','LoRo_HiLin_VIII_2iEtaSar','LoRo_HiLin_VIII_2istalam','LoRo_HiLin_VIII_2irtawaY','LoRo_HiLin_VIII_2iftataH','LoRo_HiLin_VIII_2iqtaSar','LoRo_HiLin_VIII_2iltamam','LoRo_HiLin_VIII_2intawaY','LoRo_HiLin_VIII_2ijtaraf','LoRo_HiLin_VIII_2ibtalaY','LoRo_HiLin_VIII_2ittafaq','LoRo_HiLin_VIII_2irta0af','LoRo_HiLin_VIII_2iHtasaY']
#R_HL_VIII_order = ['HiRo_LoLin_VIII_2irtaxaS','HiRo_LoLin_VIII_2iftaxar','HiRo_LoLin_VIII_2intaqaY','HiRo_LoLin_VIII_2istaHaq','HiRo_LoLin_VIII_2ixtaraE','HiRo_LoLin_VIII_2intaqad','HiRo_LoLin_VIII_2iEtaVar','HiRo_LoLin_VIII_2iktasaH','HiRo_LoLin_VIII_2iftaqad','HiRo_LoLin_VIII_2iSTafaY','HiRo_LoLin_VIII_2ixtanaq','HiRo_LoLin_VIII_2irtamaY','HiRo_LoLin_VIII_2iHtaDar','HiRo_LoLin_VIII_2ikta0af','HiRo_LoLin_VIII_2intaqaS','HiRo_LoLin_VIII_2inta0al','HiRo_LoLin_VIII_2ittaham','HiRo_LoLin_VIII_2i0tahar','HiRo_LoLin_VIII_2irtasam','HiRo_LoLin_VIII_2iHtafal','HiRo_LoLin_VIII_2imtazaj','HiRo_LoLin_VIII_2intabah','HiRo_LoLin_VIII_2iSTanaE','HiRo_LoLin_VIII_2izdaHam']
#R_HH_VIII_order = ['HiRo_HiLin_VIII_2iftadaY','HiRo_HiLin_VIII_2intavar','HiRo_HiLin_VIII_2irtaHal','HiRo_HiLin_VIII_2i0tabak','HiRo_HiLin_VIII_2i0tadad','HiRo_HiLin_VIII_2iHta0am','HiRo_HiLin_VIII_2ikta2ab','HiRo_HiLin_VIII_2iHtakar','HiRo_HiLin_VIII_2i0tamam','HiRo_HiLin_VIII_2iltaSaq','HiRo_HiLin_VIII_2imtaEaD','HiRo_HiLin_VIII_2iHtajab','HiRo_HiLin_VIII_2intakas','HiRo_HiLin_VIII_2iktanaf','HiRo_HiLin_VIII_2intamaY','HiRo_HiLin_VIII_2iqtabas','HiRo_HiLin_VIII_2iHtifaZ','HiRo_HiLin_VIII_2iEtazal','HiRo_HiLin_VIII_2iftaEal','HiRo_HiLin_VIII_2ibtanaY','HiRo_HiLin_VIII_2intaHab','HiRo_HiLin_VIII_2iktarav','HiRo_HiLin_VIII_2irtaTam','HiRo_HiLin_VIII_2ibtakar']
#R_LL_VII_order = ['LoRo_LoLin_VII_2inTabaE','LoRo_LoLin_VII_2insakab','LoRo_LoLin_VII_2injalaY','LoRo_LoLin_VII_2inhamal','LoRo_LoLin_VII_2inzaraE','LoRo_LoLin_VII_2inxalaE','LoRo_LoLin_VII_2inSaraf','LoRo_LoLin_VII_AinHall','LoRo_LoLin_VII_AinxaTab','LoRo_LoLin_VII_2inTAE','LoRo_LoLin_VII_2inqalaE','LoRo_LoLin_VII_2inHaraf','LoRo_LoLin_VII_2inzaEaj','LoRo_LoLin_VII_2inSalaH','LoRo_LoLin_VII_2inHaTT','LoRo_LoLin_VII_2inSabag','LoRo_LoLin_VII_2inTamm','LoRo_LoLin_VII_2insaraq','LoRo_LoLin_VII_2injaVab','LoRo_LoLin_VII_2inVahal','LoRo_LoLin_VII_2inxaTaf','LoRo_LoLin_VII_2injaraf','LoRo_LoLin_VII_2inkatab','LoRo_LoLin_VII_2inzawaY']
#R_LH_VII_order = ['LoRo_HiLin_VII_2infakk','LoRo_HiLin_VII_AinsamaE','LoRo_HiLin_VII_2inTaraH','LoRo_HiLin_VII_2infaraj','LoRo_HiLin_VII_2indalaE','LoRo_HiLin_VII_Ainball','LoRo_HiLin_VII_Ainsakat','LoRo_HiLin_VII_2indaras','LoRo_HiLin_VII_2inqaraD','LoRo_HiLin_VII_2inqadd','LoRo_HiLin_VII_AinqaSS','LoRo_HiLin_VII_2insalax','LoRo_HiLin_VII_2inhalak','LoRo_HiLin_VII_2inhazam','LoRo_HiLin_VII_AinHasad','LoRo_HiLin_VII_2inhawaY']
#R_HL_VII_order = ['HiRo_LoLin_VII_2in0add','HiRo_LoLin_VII_Ain0adah','HiRo_LoLin_VII_2inqaTaE','HiRo_LoLin_VII_2inmaHaY','HiRo_LoLin_VII_2inqabaD','HiRo_LoLin_VII_2inkama0','HiRo_LoLin_VII_2inqaDD','HiRo_LoLin_VII_2inqahar','HiRo_LoLin_VII_2inEakas','HiRo_LoLin_VII_2infaEal','HiRo_LoLin_VII_2inxaraT','HiRo_LoLin_VII_2inEazal','HiRo_LoLin_VII_2inkasar','HiRo_LoLin_VII_2inbahar','HiRo_LoLin_VII_2indaha0','HiRo_LoLin_VII_2indaEas','HiRo_LoLin_VII_2indafaE','HiRo_LoLin_VII_2inzalaq','HiRo_LoLin_VII_2inxadaE','HiRo_LoLin_VII_2inqasam','HiRo_LoLin_VII_2in0all','HiRo_LoLin_VII_2inxanaq','HiRo_LoLin_VII_2in0aqq','HiRo_LoLin_VII_2inTafa2']
#R_HH_VII_order = ['HiRo_HiLin_VII_2inqa0aE','HiRo_HiLin_VII_2infa00','HiRo_HiLin_VII_2indavar','HiRo_HiLin_VII_2inHafar','HiRo_HiLin_VII_AinsaqaY','HiRo_HiLin_VII_2infaTar','HiRo_HiLin_VII_2infalaE','HiRo_HiLin_VII_2infalat','HiRo_HiLin_VII_2inHaVaf','HiRo_HiLin_VII_2indabag','HiRo_HiLin_VII_2insaTal','HiRo_HiLin_VII_2inkafa2','HiRo_HiLin_VII_2inxaVal','HiRo_HiLin_VII_2inbaTaH','HiRo_HiLin_VII_2insafar','HiRo_HiLin_VII_2infaqaE','HiRo_HiLin_VII_2inbatar','HiRo_HiLin_VII_2inxaSam','HiRo_HiLin_VII_2infaqaS','HiRo_HiLin_VII_2inHaSar']

# b orders
#R_HH_VII_order = ['HiRo_HiLin_VII_2infaTar','HiRo_HiLin_VII_2inxaVal','HiRo_HiLin_VII_2indabag','HiRo_HiLin_VII_AinsaqaY','HiRo_HiLin_VII_2inbatar','HiRo_HiLin_VII_2inxaSam','HiRo_HiLin_VII_2insafar','HiRo_HiLin_VII_2inkafa2','HiRo_HiLin_VII_2inHafar','HiRo_HiLin_VII_2infaqaS','HiRo_HiLin_VII_2insaTal','HiRo_HiLin_VII_2infalat','HiRo_HiLin_VII_2infalaE','HiRo_HiLin_VII_2inHaSar','HiRo_HiLin_VII_2inHaVaf','HiRo_HiLin_VII_2infa00','HiRo_HiLin_VII_2inbaTaH','HiRo_HiLin_VII_2indavar','HiRo_HiLin_VII_2inqa0aE','HiRo_HiLin_VII_2infaqaE']
#R_HL_VII_order = ['HiRo_LoLin_VII_2inTafa2','HiRo_LoLin_VII_2inxanaq','HiRo_LoLin_VII_2inqahar','HiRo_LoLin_VII_2inxaraT','HiRo_LoLin_VII_2inEakas','HiRo_LoLin_VII_2indaEas','HiRo_LoLin_VII_2inkasar','HiRo_LoLin_VII_2in0all','HiRo_LoLin_VII_2inxadaE','HiRo_LoLin_VII_2inkama0','HiRo_LoLin_VII_2inqabaD','HiRo_LoLin_VII_2infaEal','HiRo_LoLin_VII_2inmaHaY','HiRo_LoLin_VII_2indafaE','HiRo_LoLin_VII_2inbahar','HiRo_LoLin_VII_2in0aqq','HiRo_LoLin_VII_Ain0adah','HiRo_LoLin_VII_2inqaDD','HiRo_LoLin_VII_2indaha0','HiRo_LoLin_VII_2inqasam','HiRo_LoLin_VII_2inzalaq','HiRo_LoLin_VII_2in0add','HiRo_LoLin_VII_2inEazal','HiRo_LoLin_VII_2inqaTaE']
#R_LH_VII_order = ['LoRo_HiLin_VII_Ainsakat','LoRo_HiLin_VII_2inhawaY','LoRo_HiLin_VII_2inqadd','LoRo_HiLin_VII_2infaraj','LoRo_HiLin_VII_2inhalak','LoRo_HiLin_VII_2inTaraH','LoRo_HiLin_VII_2indaras','LoRo_HiLin_VII_2indalaE','LoRo_HiLin_VII_AinsamaE','LoRo_HiLin_VII_2insalax','LoRo_HiLin_VII_Ainball','LoRo_HiLin_VII_AinHasad','LoRo_HiLin_VII_AinqaSS','LoRo_HiLin_VII_2infakk','LoRo_HiLin_VII_2inqaraD','LoRo_HiLin_VII_2inhazam']
#R_LL_VII_order = ['LoRo_LoLin_VII_2injaVab','LoRo_LoLin_VII_2insaraq','LoRo_LoLin_VII_2inzawaY','LoRo_LoLin_VII_2insakab','LoRo_LoLin_VII_2inTAE','LoRo_LoLin_VII_2inTabaE','LoRo_LoLin_VII_2inHaTT','LoRo_LoLin_VII_2inxaTaf','LoRo_LoLin_VII_2inqalaE','LoRo_LoLin_VII_2injalaY','LoRo_LoLin_VII_2inxalaE','LoRo_LoLin_VII_2inhamal','LoRo_LoLin_VII_2inVahal','LoRo_LoLin_VII_2inkatab','LoRo_LoLin_VII_2inzaEaj','LoRo_LoLin_VII_2inzaraE','LoRo_LoLin_VII_2inSalaH','LoRo_LoLin_VII_AinxaTab','LoRo_LoLin_VII_2injaraf','LoRo_LoLin_VII_2inTamm','LoRo_LoLin_VII_2inHaraf','LoRo_LoLin_VII_AinHall','LoRo_LoLin_VII_2inSaraf','LoRo_LoLin_VII_2inSabag']
#R_HH_VIII_order = ['HiRo_HiLin_VIII_2i0tadad','HiRo_HiLin_VIII_2iHtakar','HiRo_HiLin_VIII_2imtaEaD','HiRo_HiLin_VIII_2iHtifaZ','HiRo_HiLin_VIII_2iEtazal','HiRo_HiLin_VIII_2ikta2ab','HiRo_HiLin_VIII_2i0tamam','HiRo_HiLin_VIII_2iktanaf','HiRo_HiLin_VIII_2irtaTam','HiRo_HiLin_VIII_2ibtanaY','HiRo_HiLin_VIII_2i0tabak','HiRo_HiLin_VIII_2iltaSaq','HiRo_HiLin_VIII_2intamaY','HiRo_HiLin_VIII_2intaHab','HiRo_HiLin_VIII_2iktarav','HiRo_HiLin_VIII_2intavar','HiRo_HiLin_VIII_2intakas','HiRo_HiLin_VIII_2iHtajab','HiRo_HiLin_VIII_2irtaHal','HiRo_HiLin_VIII_2iHta0am','HiRo_HiLin_VIII_2iftadaY','HiRo_HiLin_VIII_2iqtabas','HiRo_HiLin_VIII_2ibtakar','HiRo_HiLin_VIII_2iftaEal']
#R_HL_VIII_order = ['HiRo_LoLin_VIII_2ikta0af','HiRo_LoLin_VIII_2intaqad','HiRo_LoLin_VIII_2irtaxaS','HiRo_LoLin_VIII_2ixtanaq','HiRo_LoLin_VIII_2iSTafaY','HiRo_LoLin_VIII_2intaqaY','HiRo_LoLin_VIII_2irtasam','HiRo_LoLin_VIII_2iktasaH','HiRo_LoLin_VIII_2ixtaraE','HiRo_LoLin_VIII_2inta0al','HiRo_LoLin_VIII_2imtazaj','HiRo_LoLin_VIII_2irtamaY','HiRo_LoLin_VIII_2istaHaq','HiRo_LoLin_VIII_2intabah','HiRo_LoLin_VIII_2ittaham','HiRo_LoLin_VIII_2iEtaVar','HiRo_LoLin_VIII_2intaqaS','HiRo_LoLin_VIII_2i0tahar','HiRo_LoLin_VIII_2iHtafal','HiRo_LoLin_VIII_2iHtaDar','HiRo_LoLin_VIII_2iSTanaE','HiRo_LoLin_VIII_2izdaHam','HiRo_LoLin_VIII_2iftaxar','HiRo_LoLin_VIII_2iftaqad']
#R_LH_VIII_order = ['LoRo_HiLin_VIII_2ittafaq','LoRo_HiLin_VIII_2irtawaY','LoRo_HiLin_VIII_2iltamam','LoRo_HiLin_VIII_2iEtanaY','LoRo_HiLin_VIII_2ihtadaY','LoRo_HiLin_VIII_2iqtaSar','LoRo_HiLin_VIII_2intazaE','LoRo_HiLin_VIII_2ixtaTaf','LoRo_HiLin_VIII_2iltazam','LoRo_HiLin_VIII_2intasab','LoRo_HiLin_VIII_2ijtaraf','LoRo_HiLin_VIII_2iHtadad','LoRo_HiLin_VIII_2ibtada2','LoRo_HiLin_VIII_2imtaraZ','LoRo_HiLin_VIII_2iHtasaY','LoRo_HiLin_VIII_2irta0af','LoRo_HiLin_VIII_2ittaHad','LoRo_HiLin_VIII_2istalam','LoRo_HiLin_VIII_2istalam','LoRo_HiLin_VIII_2istamaE','LoRo_HiLin_VIII_2iEtaSar','LoRo_HiLin_VIII_2intawaY','LoRo_HiLin_VIII_2ibtalaY','LoRo_HiLin_VIII_2iltaHaq','LoRo_HiLin_VIII_2iftataH']
#R_LL_VIII_order = ['LoRo_LoLin_VIII_2iftakar','LoRo_LoLin_VIII_2ixtafat','LoRo_LoLin_VIII_2ijtamaE','LoRo_LoLin_VIII_2iHtawaY','LoRo_LoLin_VIII_2iHtaqar','LoRo_LoLin_VIII_2iHtaram','LoRo_LoLin_VIII_2iftarar','LoRo_LoLin_VIII_2intahaY','LoRo_LoLin_VIII_2ibtaEad','LoRo_LoLin_VIII_2iZZalam','LoRo_LoLin_VIII_2intaZam','LoRo_LoLin_VIII_2i0taEal','LoRo_LoLin_VIII_2ihtazaz','LoRo_LoLin_VIII_2izdarad','LoRo_LoLin_VIII_2ixtabar','LoRo_LoLin_VIII_2iEtaqad','LoRo_LoLin_VIII_2iltafaf','LoRo_LoLin_VIII_2iqtaraH','LoRo_LoLin_VIII_2iEtamad','LoRo_LoLin_VIII_2iTTarad','LoRo_LoLin_VIII_2irtabaT','LoRo_LoLin_VIII_2intaZar','LoRo_LoLin_VIII_2iHtimal','LoRo_LoLin_VIII_2irtafaE']



orders = [R_HH_VIII_order,R_LH_VIII_order,R_HL_VIII_order,R_LL_VIII_order,R_HH_VII_order,R_HL_VII_order,R_LH_VII_order,R_LL_VII_order]

parc = mne.read_labels_from_annot('fsaverage','AudCortex',subjects_dir='AraSurp/mri',hemi='lh')
label = [i for i in parc if i.name.startswith('audcortex-lh')][0]
fs_src = mne.read_source_spaces(workingdir + 'AraSurp/mri/fsaverage/bem/fsaverage-ico-4-src.fif')

#subjects = ['Y0310','Y0312','Y0315','Y0316','Y0318','Y0319','Y0320','Y0321','Y0322','Y0323','Y0324','Y0325','Y0326','Y0327']
#subjects = ['Y0318','Y0319','Y0320','Y0322','Y0323','Y0324','Y0325','Y0327'] #list e
#my_stc_names = ['R_HH_VIII-lh.stc','R_LH_VIII-lh.stc','R_HL_VIII-lh.stc','R_LL_VIII-lh.stc','R_HH_VII-lh.stc','R_HL_VII-lh.stc','R_LH_VII-lh.stc','R_LL_VII-lh.stc']
#subjects = ['Y0327'] # e list
#subjects = ['Y0319','Y0322','Y0323','Y0325', 'Y0327'] # e list
#subjects = ['Y0312'] #b list
#subjects = ['Y0316'] #d list

subjects = ['Y0310','Y0312','Y0315','Y0316','Y0318','Y0319','Y0320','Y0321','Y0322','Y0323','Y0324','Y0325','Y0326','Y0327']
my_stc_names = ['R_HH_VIII','R_LH_VIII','R_HL_VIII','R_LL_VIII','R_HH_VII','R_HL_VII','R_LH_VII','R_LL_VII']
stcs, dspm, subject, item, binyan, linearbin, rootbin, linearsurp, rootsurp, rootfreq, linearfreq = [],[],[],[],[],[],[],[],[],[],[]
for sbj in subjects:
	stc_path = workingdir + 'AraSurp/stc/%s_' %sbj
	x = 0
	for i in my_stc_names:
		epochnum = 1
		b = 0
		order = orders[x]
		catchme = ""
		while epochnum <25:
			try:
				#print stc_path + i + str(epochnum) + '-lh.stc'
				stc = mne.read_source_estimate(stc_path + i + str(epochnum) + '-lh.stc')
			except:
				catchme = "caught"
				print "caught"
			if catchme:
				epochnum = 26
				print "moving to next one"
			#else:
			#	stcs.append(stc)
			#	item.append(order[b])
			#	rootsurp.append(float(rootsurpdict[order[b]]))
			#	linearsurp.append(float(linearsurpdict[order[b]]))
			#	rootfreq.append(float(rootfreqdict[order[b]]))
			#	linearfreq.append(float(linearfreqdict[order[b]]))
			#	binyan.append(str.split(i,'_')[2].strip("-lh.stc"))
			#	epochnum = epochnum + 1
			#	b = b+1
			else:
				act = mne.extract_label_time_course(stc,label,src=fs_src,mode='mean')
				my_dspm = act[0]
				my_dspm = my_dspm[420:520] #needs altered to point to the relevant cluster. am i sure i should be putting it 420 in to make it start at 0?
				my_dspm = float(sum(my_dspm)/len(my_dspm))
				print my_dspm
				epochnum = epochnum + 1
				#for a in my_dspm:
				dspm.append(float(my_dspm))
				item.append(order[b])
				print order[b]
				rootsurp.append(rootsurpdict[order[b]])
				linearsurp.append(linearsurpdict[order[b]])
				rootfreq.append(rootfreqdict[order[b]])
				linearfreq.append(linearfreqdict[order[b]])
				binyan.append(str.split(i,'_')[2].strip("-lh.stc"))
				linearbin.append(i[3])
				rootbin.append(i[2])
				subject.append(sbj)
				b = b+1

		x = x+1


		ds_subject = eelbrain.Dataset()     
		ds_subject['data'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='AraSurp/mri',method='dSPM',fixed=True,parc='AudCortex') 
		src = ds_subject['data']
		src.source.set_parc('AudCortex')
		src_region = src.sub(source='audcortex-lh') #reducing the ds to just the sources of interest. can also sub with time. DO THIS!!
		ds_subject['data']=src_region
		beta = ds_subject.eval("data.ols(rootsurp)")
		beta2 = ds_subject.eval("data.ols(linearsurp)")
		betas.append(beta)
		betas2.append(beta2)
res_root = eelbrain.testnd.ttest_1samp('beta',match='subject',ds_root=ds,pmin=.05,samples=1,mintime=0.01,tstart=0.0,tstop=.300,minsource=10,tail=0)
res_linear = eelbrain.testnd.ttest_1samp('beta',match='subject',ds_lin=ds,pmin=.05,samples=1,mintime=0.01,tstart=0.0,tstop=.300,minsource=10,tail=0)


ds_subject['rootsurp'] = eelbrain.Var(rootsurp)   
                 
ds_subject['linearsurp'] = eelbrain.Var(linearsurp)                    
beta = ds_subject.eval("data.ols(rootsurp)")
beta2 = ds_subject.eval("data.ols(linearsurp)")
betas.append(beta)
betas2.append(beta2)



ds_lm = eelbrain.Dataset()
ds_lm['dSPM'] = eelbrain.Factor(dspm)
ds_lm['Subject'] = eelbrain.Factor(subject)
ds_lm['Item'] = eelbrain.Factor(item)
ds_lm['Binyan'] = eelbrain.Factor(binyan)
ds_lm['RootBin'] = eelbrain.Factor(rootbin)
ds_lm['LinearBin'] = eelbrain.Factor(linearbin)
ds_lm['RootSurp'] = eelbrain.Factor(rootsurp)
ds_lm['LinearSurp'] = eelbrain.Factor(linearsurp)
ds_lm['RootFreq'] = eelbrain.Factor(rootfreq)
ds_lm['LinearFreq'] = eelbrain.Factor(linearfreq)


%store ds_lm.as_table() >> lmm_input_312_316_319_322_323_325_327.txt

#betas = [] # don't copy me!
ds_subject = eelbrain.Dataset()     
ds_subject['data'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='AraSurp/mri',method='dSPM',fixed=True,parc='AudCortex') 
src = ds_subject['data']
src.source.set_parc('AudCortex')
src_region = src.sub(source='audcortex-lh') #reducing the ds to just the sources of interest. can also sub with time. DO THIS!!
ds_subject['data']=src_region

ds_subject['rootsurp'] = eelbrain.Var(rootsurp)   
                 
ds_subject['linearsurp'] = eelbrain.Var(linearsurp)                    
beta = ds_subject.eval("data.ols(rootsurp)")
beta2 = ds_subject.eval("data.ols(linearsurp)")
betas.append(beta)
betas2.append(beta2)

subjects = ['Y0318','Y0320']
ds_root = eelbrain.Dataset()
ds_root['subject'] = eelbrain.Factor(subjects, random=True)
ds_root['beta'] = eelbrain.combine(betas)

ds_lin = eelbrain.Dataset()
ds_lin['subject'] = eelbrain.Factor(subjects, random=True)
ds_lin['beta'] = eelbrain.combine(betas2)

res_root = eelbrain.testnd.ttest_1samp('beta',match='subject',ds_root=ds,pmin=.05,samples=1,mintime=0.01,tstart=0.0,tstop=.300,minsource=10,tail=0)
res_linear = eelbrain.testnd.ttest_1samp('beta',match='subject',ds_lin=ds,pmin=.05,samples=1,mintime=0.01,tstart=0.0,tstop=.300,minsource=10,tail=0)


###

#res = eelbrain.testnd.anova(ds['stc'].mean('source'), X='Binyan*RootSurp*LinearSurp',ds=ds,match='Subject',pmin=0.05, tstart=0.00, tstop=0.25, samples=10000, mintime=0.01) #the .mean('source' here is because i'm doing an ROI test: i'm not looking for space
#In [35]: res = eelbrain.testnd.anova(ds['stc'].mean('source'), X='Binyan*RootSurp*LinearSurp',ds=ds,match='Subject',pmin=0.05, tstart=0.00, tstop=0.30, samples=10000, mintime=0.01)
#In [36]: print res.clusters.as_table()
#id   tstart   tstop   duration   v         p        sig   effect               
#1    0.055    0.07    0.015      78.7626   0.0229   *     RootSurp x LinearSurp
#2    0.076    0.099   0.023      154.097   0.0075   **    RootSurp x LinearSurp
#3    0.129    0.141   0.012      53.9243   0.0399   *     RootSurp x LinearSurp




results_binyan = eelbrain.testnd.ttest_rel('stc', X='Binyan', ds=ds, sub=(ds['Subject']!= 'Y0315'),match='Subject', pmin=0.05, tstart=0.05, tstop=0.45, samples=1, mintime=0.01,minsource=10)

results_binyan = eelbrain.testnd.ttest_rel('stc', X='Binyan', ds=ds,match='Subject', pmin=0.05, tstart=0.0, tstop=0.5, samples=1, mintime=0.01,minsource=10)

statmap_binyan = results_binyan.masked_parameter_map(pmin=None)
image_binyan = eelbrain.plot.brain.bin_table(statmap_binyan,tstep=0.05,surf='inflated') 

results_root_viii = eelbrain.testnd.ttest_rel('stc', X='RootSurp', ds=ds, sub=(ds['Binyan']!= 'VIII'),match='Subject', pmin=0.05, tstart=0.0, tstop=0.35, samples=0, mintime=0.01,minsource=10)

statmap_root_viii = results_root_viii.masked_parameter_map(pmin=None)
image_root_viii = eelbrain.plot.brain.bin_table(statmap_root_viii,tstep=0.05,surf='inflated')


results_linear_viii = eelbrain.testnd.ttest_rel('stc', X='LinearSurp', ds=ds, sub=(ds['Binyan']!= 'VIII'),match='Subject', pmin=0.05, tstart=0.0, tstop=0.35, samples=0, mintime=0.01,minsource=10)

statmap_linear_viii = results_linear_viii.masked_parameter_map(pmin=None)
image_linear_viii = eelbrain.plot.brain.bin_table(statmap_linear_viii,tstep=0.05,surf='inflated')  

results_linear_vii = eelbrain.testnd.ttest_rel('stc', X='LinearSurp', ds=ds, sub=(ds['Binyan']!= 'VII'),match='Subject', pmin=0.05, tstart=0.0, tstop=0.35, samples=0, mintime=0.01,minsource=10)

statmap_linear_vii = results_linear_vii.masked_parameter_map(pmin=None)
image_linear_vii = eelbrain.plot.brain.bin_table(statmap_linear_vii,tstep=0.05,surf='inflated') 


results_root = eelbrain.testnd.ttest_rel('stc', X='RootSurp', ds=ds, sub=(ds['Subject']!= 'Y0315'),match='Subject', pmin=0.05, tstart=0.1, tstop=0.2, samples=100, mintime=0.01,minsource=10)

results_linear = eelbrain.testnd.ttest_rel('stc', X='LinearSurp', ds=ds, sub=(ds['Subject']!= 'Y0315'),match='Subject', pmin=0.05, tstart=0.2, tstop=0.3, samples=100, mintime=0.01,minsource=10)

results_root_with_15 = eelbrain.testnd.ttest_rel('stc', X='RootSurp', ds=ds,match='Subject', pmin=0.05, tstart=-0.4, tstop=0.4, samples=0, mintime=0.01,minsource=10)

results_linear_with_15 = eelbrain.testnd.ttest_rel('stc', X='LinearSurp', ds=ds,match='Subject', pmin=0.05, tstart=-0.4, tstop=0.4, samples=0, mintime=0.01,minsource=10)

statmap_root = results_root.masked_parameter_map(pmin=None)
image_root = eelbrain.plot.brain.bin_table(statmap_root,tstep=0.05,surf='inflated') 
#image.save_image('AraSurp/root_minus315_0_to_6.png')

statmap_linear = results_linear.masked_parameter_map(pmin=None)
image_linear = eelbrain.plot.brain.bin_table(statmap_linear,tstep=0.05,surf='inflated') 
#image_linear.save_image('AraSurp/linear_minus315_0_to_6.png')

# change tstep to what you want

res = eelbrain.testnd.ttest_ind('stc', X='LinearSurp', ds=ds, sub=(ds['Subject']!= 'Y0315'),match='Subject', pmin=0.05, tstart=0, tstop=0.6, samples=100, mintime=0.001)
res = eelbrain.testnd.ttest_rel('stc', X='LinearSurp', ds=ds,match='Subject', pmin=0.05, tstart=0, tstop=0.6, samples=1000, mintime=0.001)

sig_clusters=np.where(res.clusters['p']<=0.05)[0]


x_sign_clusters=np.where(res1.clusters['p']<=0.05)[0]
for i in range(len(x_sign_clusters)):
    cluster = res1.clusters[x_sign_clusters[i],'cluster']
    tstart = res1.clusters[x_sign_clusters[i]]['tstart']
    tstop = res1.clusters[x_sign_clusters[i]]['tstop']
#             #save significant cluster as a label for plotting.
    label = eelbrain.labels_from_clusters(cluster)
    label[0].name = 'label-lh'
    mne.write_labels_to_annot(label,subject='fsaverage', parc='cluster%s_FullAnalysis'%i ,subjects_dir='AraSurp/mri/', overwrite=True)
    src.source.set_parc('cluster%s_FullAnalysis' %i)
    src_region = src.sub(source='label-lh')
    ds['stc']=src_region
    timecourse = src_region.mean('source')
    i2= i+1
    activation = eelbrain.plot.UTSStat(timecourse,'RootSurp', ds=ds, legend='lower left', title='cluster%s time course' %i2)
    activation.add_vspan(xmin=tstart, xmax=tstop, color='black', fill=False)
    activation.save('AraSurp/cluster%s_timecourse_(%s-%s).png' %(i2,tstart, tstop))
    activation.close()

In [35]: for i in range(len(x_sign_clusters)):                                  
    ...:     cluster = res.clusters[x_sign_clusters[i],'cluster']               
    ...:     tstart = res.clusters[x_sign_clusters[i]]['tstart']                
    ...:     tstop = res.clusters[x_sign_clusters[i]]['tstop']                  
    ...: #             #save significant cluster as a label for plotting.       
label = eelbrain.labels_from_clusters(cluster)                     
label[0].name = 'label-lh'                                         
mne.write_labels_to_annot(label,subject='fsaverage', parc='cluster%s_FullAnalysis'%i ,subjects_dir=subjects_dir, overwrite=True)          
eelbrain.set_parc(src,'cluster%s_FullAnalysis' %i)                 
src_region = src.sub(source=label[0])                              
ds['stc']=src_region                                               
timecourse = src_region.mean('source') 
i2=i+1                                                                                         
activation = eelbrain.plot.UTSStat(timecourse,'LinearSurp', ds=ds, 
sub=(ds['Subject']!= 'Y0315'), legend='lower left', title='cluster%s time course' %i+1)                                                       
activation.add_vspan(xmin=tstart, xmax=tstop, color='black', fill=False)                                                                  
activation.save('AraSurp/cluster%s_timecourse_(%s-%s).png' %(i2,tstart, tstop))                                                           
activation.close()   



#for c in rootsurp:
 #    for tk in linsurp:
#		for b in binyan:
'''
#         # set parcellation
#         ds['stc']=src #reset data to full space
#         src.source.set_parc('FullLeftHemisphere') #choose atlas
#         src_region = src.sub(source='left_hemi-lh') #reducing the ds to just the sources of interest. can also sub with time.
#         ds['stc']=src_region
#         #run ttest
#         res = eelbrain.testnd.ttest_rel('stc', X='Prime_Type',c0='unrel', c1='semrel', ds=ds, sub=(ds['SOA']==current_soa)&(ds['Task']==current_task)&(ds['Prime_Type']!='id'), match='subject',pmin=pmin, tstart=0, tstop=0.6, samples=10000, mintime=0.001)
#         print res.clusters


'''
#ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='sammy_workspace/AraSurp/mri',method='dSPM',fixed=True,parc='aparc')


#vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir=subjects_dir) #fsaverage's source space

conditions = ['_R_HH_VIII', '_R_LH_VIII', '_R_HL_VIII', '_R_LL_VII','_R_HH_VII', '_R_LH_VII', '_R_HL_VII', '_R_LL_VII']
def get_var_name(**kwargs): return kwargs.keys()[0]

for cond in conditions:
	evoked = "ev" + cond
	filename = get_var_name(evoked=evoked)
	my_stc = mne.minimum_norm.apply_inverse(evoked,inv,lambda2=lambda2,verbose=False,method='dSPM')
	#stc_morphed = mne.morph_data(subject_from=subject, subject_to='fsaverage',stc_from=my_stc, grade=vertices_to,subjects_dir=subjects_dir)
	#stc_morphed.save('AraSurp/stc/%s%s' %(subject,filename))
	my_stc.save('AraSurp/stc/%s%s' %(subject,filename))	


parc = mne.read_labels_from_annot('fsaverage','AudCortex',subjects_dir='AraSurp/mri',hemi='lh')
label = [i for i in parc if i.name.startswith('transverse')][0]
subjects = ['R0157','R0316','R0318','R0319','R0320','R0328','R0329','R0333','R0334','R0345','R0346','R0347']
#
#321 322 323 'R0324','R0325','R0326','R0327',

for subj in subjects:
	src = mne.read_source_spaces('AraSurp/mri/%s/bem/%s-ico-4-src.fif' %(subj,subj))
	print "source space set up complete, reading in STCs..."
	stc_lowlinear = mne.read_source_estimate('AraSurp/stc/%s_Llin-lh.stc' %subj)
	stc_highlinear = mne.read_source_estimate('AraSurp/stc/%s_Hlin-lh.stc' %subj)
	tl_lowlinear = stc_lowlinear.extract_label_time_course(label,src=src,mode='mean')
	tl_highlinear = stc_highlinear.extract_label_time_course(label,src=src,mode='mean')
	print "plotting timecourse..."
	plt.plot(stc_highlinear.times,tl_highlinear[0],color='purple',label='highroot')
	plt.plot(stc_lowlinear.times,tl_lowlinear[0],color='green',label='lowroot')
	plt.axvline(0,color='lightgrey',alpha=2)
	plt.legend(loc=0)
	plt.ylabel('Activation (dSPM)')
	plt.xlabel('Time (s)')
	plt.title('Auditory Cortex - Linear Surprisal')
	plt.savefig('AraSurp/%s_linear_surprisal.png' %subj)
	plt.clf()
	

plt.clf()
stc_R_HH_VIII = mne.read_source_estimate('AraSurp/stc/Y0322ev_R_HH_VIII-lh.stc')



plt.clf()
for s in stcs:
	i = 0
	chartname = "tl_" + str(i)
	chartname = s.extract_label_time_course(label,src=src_morph,mode='mean')
	plt.plot(s.times,chartname[0],color='green',alpha=2)
	i = i +1
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Superior Temporal Gyrus')
plt.savefig('AraSurp/viii_stg_hh_lh.png')


plt.plot(stc_R_HH_VIII.times,tl_R_HH_VIII[0],color='purple',alpha=0.7,label='HH_VIII')
plt.plot(stc_R_LH_VIII.times,tl_R_LH_VIII[0],color='green',alpha=2,label='LH_VIII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Superior Temporal Gyrus')
plt.savefig('AraSurp/viii_stg_hh_lh.png')


stc_R_HH_VIII = mne.minimum_norm.apply_inverse(ev_R_HH_VIII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_LH_VIII = mne.minimum_norm.apply_inverse(ev_R_LH_VIII,inv,lambda2=lambda2,verbose=False,method='dSPM')


stc_R_HH_VIII.save('AraSurp/stc/%s_R_HH_VIII' %subject) 


stc_R_LH_VIII = mne.minimum_norm.apply_inverse(ev_R_LH_VIII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_LH_VIII.save('AraSurp/stc/%s_R_LH_VIII' %subject) 

stc_R_HL_VIII = mne.minimum_norm.apply_inverse(ev_R_HL_VIII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_HL_VIII.save('AraSurp/stc/%s_R_HL_VIII' %subject) 

stc_R_LL_VIII = mne.minimum_norm.apply_inverse(ev_R_LL_VIII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_LL_VIII.save('AraSurp/stc/%s_R_LL_VIII' %subject) 

stc_R_HH_VII = mne.minimum_norm.apply_inverse(ev_R_HH_VII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_HH_VII.save('AraSurp/stc/%s_R_HH_VII' %subject) 


stc_R_LH_VII = mne.minimum_norm.apply_inverse(ev_R_LH_VII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_LH_VII.save('AraSurp/stc/%s_R_LH_VII' %subject) 

stc_R_HL_VII = mne.minimum_norm.apply_inverse(ev_R_HL_VII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_HL_VII.save('AraSurp/stc/%s_R_HL_VII' %subject) 

stc_R_LL_VII = mne.minimum_norm.apply_inverse(ev_R_LL_VII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_LL_VII.save('AraSurp/stc/%s_R_LL_VII' %subject) 


#stcs = [stc_R_HH_VIII, stc_R_LH_VIII, stc_R_HL_VIII, stc_R_HH_VII, stc_R_LH_VII, stc_R_HL_VII]

#ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir='sammy_workspace/AraSurp/mri',method='dSPM',fixed=True,parc='aparc')


#parc = mne.read_labels_from_annot('fsaverage',parc='PALS_B12_Lobes',subjects_dir=subjects_dir)

#brain = eelbrain.plot.brain.cluster(src_region.mean('time'), subjects_dir='sammy_workspace/AraSurp/mri',surf='smoothwm')
'''

###binyan VIII charts
'''
stc_R_HH_VIII = mne.read_source_estimate('AraSurp/stc/Y0322ev_R_HH_VIII-lh.stc')

stc_R_LH_VIII = mne.read_source_estimate('AraSurp/stc/Y0322ev_R_LH_VIII-lh.stc')

stc_R_HH_VIII = mne.minimum_norm.apply_inverse(ev_R_HH_VIII,inv,lambda2=lambda2,verbose=False,method='dSPM')
stc_R_LH_VIII = mne.minimum_norm.apply_inverse(ev_R_LH_VIII,inv,lambda2=lambda2,verbose=False,method='dSPM')


parc = mne.read_labels_from_annot('fsaverage','aparc',subjects_dir='AraSurp/mri',hemi='lh')


label = [i for i in parc if i.name.startswith('superiortemporal-lh')][0]

tl_R_HH_VIII = stc_R_HH_VIII.extract_label_time_course(label,src=src_morph,mode='mean')
tl_R_LH_VIII = stc_R_LH_VIII.extract_label_time_course(label,src=src_morph,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VIII.times,tl_R_HH_VIII[0],color='purple',alpha=0.7,label='HH_VIII')
plt.plot(stc_R_LH_VIII.times,tl_R_LH_VIII[0],color='green',alpha=2,label='LH_VIII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Superior Temporal Gyrus')
plt.savefig('AraSurp/viii_stg_hh_lh.png')


label = [i for i in parc if i.name.startswith('middletemporal-lh')][0]

tl_R_HH_VIII = stc_R_HH_VIII.extract_label_time_course(label,src=src,mode='mean')
tl_R_LH_VIII = stc_R_LH_VIII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VIII.times,tl_R_HH_VIII[0],color='purple',alpha=0.7,label='HH_VIII')
plt.plot(stc_R_LH_VIII.times,tl_R_LH_VIII[0],color='green',alpha=2,label='LH_VIII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Middle Temporal Gyrus')
plt.savefig('AraSurp/viii_mtg_hh_lh.png')


label = [i for i in parc if i.name.startswith('transversetemporal-lh')][0]

tl_R_HH_VIII = stc_R_HH_VIII.extract_label_time_course(label,src=src,mode='mean')
tl_R_LH_VIII = stc_R_LH_VIII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VIII.times,tl_R_HH_VIII[0],color='purple',alpha=0.7,label='HH_VIII')
plt.plot(stc_R_LH_VIII.times,tl_R_LH_VIII[0],color='green',alpha=2,label='LH_VIII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Transverse Temporal Gyrus')
plt.savefig('AraSurp/viii_ttg_hh_lh.png')

#linear


label = [i for i in parc if i.name.startswith('superiortemporal-lh')][0]

tl_R_HH_VIII = stc_R_HH_VIII.extract_label_time_course(label,src=src,mode='mean')
tl_R_HL_VIII = stc_R_HL_VIII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VIII.times,tl_R_HH_VIII[0],color='purple',alpha=0.7,label='HH_VIII')
plt.plot(stc_R_HL_VIII.times,tl_R_HL_VIII[0],color='blue',alpha=2,label='HL_VIII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Superior Temporal Gyrus')
plt.savefig('salem_images/viii_stg_hh_hl.png')


label = [i for i in parc if i.name.startswith('middletemporal-lh')][0]

tl_R_HH_VIII = stc_R_HH_VIII.extract_label_time_course(label,src=src,mode='mean')
tl_R_HL_VIII = stc_R_HL_VIII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VIII.times,tl_R_HH_VIII[0],color='purple',alpha=0.7,label='HH_VIII')
plt.plot(stc_R_HL_VIII.times,tl_R_HL_VIII[0],color='blue',alpha=2,label='HL_VIII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Middle Temporal Gyrus')
plt.savefig('salem_images/viii_mtg_hh_hl.png')


label = [i for i in parc if i.name.startswith('transversetemporal-lh')][0]

tl_R_HH_VIII = stc_R_HH_VIII.extract_label_time_course(label,src=src,mode='mean')
tl_R_HL_VIII = stc_R_HL_VIII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VIII.times,tl_R_HH_VIII[0],color='purple',alpha=0.7,label='HH_VIII')
plt.plot(stc_R_HL_VIII.times,tl_R_HL_VIII[0],color='blue',alpha=2,label='HL_VIII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Transverse Temporal Gyrus')
plt.savefig('salem_images/viii_ttg_hh_hl.png')















#######binyan VII







stc_R_HH_VII = mne.read_source_estimate('sammy_workspace/AraSurp/meg/Y0310-R_HH_VII-stc')

stc_R_LH_VII = mne.read_source_estimate('sammy_workspace/AraSurp/meg/Y0310-R_LH_VII-stc')

label = [i for i in parc if i.name.startswith('superiortemporal-lh')][0]

tl_R_HH_VII = stc_R_HH_VII.extract_label_time_course(label,src=src,mode='mean')
tl_R_LH_VII = stc_R_LH_VII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VII.times,tl_R_HH_VII[0],color='purple',alpha=0.7,label='HH_VII')
plt.plot(stc_R_LH_VII.times,tl_R_LH_VII[0],color='green',alpha=2,label='LH_VII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Superior Temporal Gyrus')
plt.savefig('salem_images/vii_stg_hh_lh.png')


label = [i for i in parc if i.name.startswith('middletemporal-lh')][0]

tl_R_HH_VII = stc_R_HH_VII.extract_label_time_course(label,src=src,mode='mean')
tl_R_LH_VII = stc_R_LH_VII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VII.times,tl_R_HH_VII[0],color='purple',alpha=0.7,label='HH_VII')
plt.plot(stc_R_LH_VII.times,tl_R_LH_VII[0],color='green',alpha=2,label='LH_VII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Middle Temporal Gyrus')
plt.savefig('salem_images/vii_mtg_hh_lh.png')


label = [i for i in parc if i.name.startswith('transversetemporal-lh')][0]

tl_R_HH_VII = stc_R_HH_VII.extract_label_time_course(label,src=src,mode='mean')
tl_R_LH_VII = stc_R_LH_VII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VII.times,tl_R_HH_VII[0],color='purple',alpha=0.7,label='HH_VII')
plt.plot(stc_R_LH_VII.times,tl_R_LH_VII[0],color='green',alpha=2,label='LH_VII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Transverse Temporal Gyrus')
plt.savefig('salem_images/vii_ttg_hh_lh.png')

#linear

label = [i for i in parc if i.name.startswith('superiortemporal-lh')][0]

tl_R_HH_VII = stc_R_HH_VII.extract_label_time_course(label,src=src,mode='mean')
tl_R_HL_VII = stc_R_HL_VII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VII.times,tl_R_HH_VII[0],color='purple',alpha=0.7,label='HH_VII')
plt.plot(stc_R_HL_VII.times,tl_R_HL_VII[0],color='blue',alpha=2,label='HL_VII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Superior Temporal Gyrus')
plt.savefig('salem_images/vii_stg_hh_hl.png')


label = [i for i in parc if i.name.startswith('middletemporal-lh')][0]

tl_R_HH_VII = stc_R_HH_VII.extract_label_time_course(label,src=src,mode='mean')
tl_R_HL_VII = stc_R_HL_VII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VII.times,tl_R_HH_VII[0],color='purple',alpha=0.7,label='HH_VII')
plt.plot(stc_R_HL_VII.times,tl_R_HL_VII[0],color='blue',alpha=2,label='HL_VII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Middle Temporal Gyrus')
plt.savefig('salem_images/vii_mtg_hh_hl.png')


label = [i for i in parc if i.name.startswith('transversetemporal-lh')][0]

tl_R_HH_VII = stc_R_HH_VII.extract_label_time_course(label,src=src,mode='mean')
tl_R_HL_VII = stc_R_HL_VII.extract_label_time_course(label,src=src,mode='mean')

plt.clf()
plt.plot(stc_R_HH_VII.times,tl_R_HH_VII[0],color='purple',alpha=0.7,label='HH_VII')
plt.plot(stc_R_HL_VII.times,tl_R_HL_VII[0],color='blue',alpha=2,label='HL_VII')
plt.legend(loc=0)
plt.axvline(0,color='lightgrey',alpha=2)

plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('Transverse Temporal Gyrus')
plt.savefig('salem_images/vii_ttg_hh_hl.png')
'''


### spatiotemporal



'''
parc = mne.read_labels_from_annot('fsaverage','PALS_B12_Lobes',subjects_dir='sammy_workspace/AraSurp/mri',hemi='lh')

label = [i for i in parc if i.name.startswith('LOBE.TEMPORAL-lh')][0]


inverse_operator = inv


stcs = apply_inverse_epochs(epochs, inverse_operator, lambda2, method,
                            pick_ori="normal", return_generator=True)

src = inverse_operator['src']
fmin, fmax = 7.5, 40.
sfreq = raw.info['sfreq']


label_ts = mne.extract_label_time_course(stcs, label, src, mode='mean_flip',
                                         return_generator=True)


events[:, :, :, 0] += condition1.data1[:, :, np.newaxis]
X[:, :, :, 1] += condition2.data1[:, :, np.newaxis]

event_id_new = 64 #R_HH_VIII

epochs1 = mne.Epochs(raw,events_,event_id_new,tmin=-0.5,tmax=1.5,baseline=(-0.4,-0.2),reject=dict(mag=4e-12))

event_id_new = 34 #R_LH_VIII

epochs2 = mne.Epochs(raw,events_,event_id,tmin=-0.5,tmax=1.5,baseline=(-0.4,-0.2),reject=dict(mag=4e-12))


equalize_epoch_counts([epochs1, epochs2])

evoked1 = epochs1.average()
evoked2 = epochs2.average()

HighVIIIRoot= apply_inverse(evoked1, inverse_operator, lambda2, method)
LowVIIIRoot= apply_inverse(evoked2, inverse_operator, lambda2, method)


stc_R_LH_VIII.data1.shape

HH_VIII_vertices, HH_VIII_times, = stc_R_HH_VIII.data1.shape
LH_VIII_vertices, LH_VIII_times, = stc_R_LH_VIII.data1.shape

X1 = stc_R_HH_VIII.data1[:, :, np.newaxis]
X2 = stc_R_LH_VIII.data1[:, :, np.newaxis]


fmin, fmax = 3., 9.
sfreq = raw.info['sfreq']  # the sampling frequency
tmin = -0.4  # exclude the baseline period
con1, freqs1, times1, n_epochs1, n_tapers1 = spectral_connectivity(
    epochs1, method='pli', mode='multitaper', sfreq=sfreq, fmin=fmin, fmax=fmax,
    faverage=True, tmin=tmin, mt_adaptive=False, n_jobs=1)

#connectivity = 



T_obs, clusters, cluster_p_values, H0 = clu = \
spatio_temporal_cluster_test(X, connectivity=con1, n_jobs=1,
                                 threshold=t_threshold)
a = np.abs(stc_R_HH_VIII)


#, R_HL_VIII=41, R_LL_VIII=21, R_HH_VII=71, R_HL_VII=25, R_LH_VII=18, R_LL_VII=37)
'''
