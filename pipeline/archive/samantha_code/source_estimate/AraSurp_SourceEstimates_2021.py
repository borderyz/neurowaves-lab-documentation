import pyface.qt
#import wx
import mne
import eelbrain
import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
from mne.preprocessing import ICA
import pickle
from surfer import Brain
import eelbrain

'''for brain plotting:
import os #for doing brain stuff
os.environ['ETS_TOOLKIT'] = 'wx' #for doing brain plotting stuff
import mne
import eelbrain
from surfer import Brain
'''

#main_exp_dir = '/media/nellab/My Passport/Tag.py workspace/meg/TagSurp/'
main_exp_dir = '/home/scw9/wray_workspace/AraSurp_mne/'


subjects_dir = main_exp_dir + 'mri'
#Y0333_AraSurp_12Sept18-NR
'''
subjects = ['Y0358']
for s in subjects:
	subject = s
	subject1 = subject
	ica = ICA(n_components=0.95,method='fastica',random_state=42,max_iter=15000)
	#ica = ICA(n_components=0.95,method='fastica',random_state=42)
	raw = mne.io.read_raw_fif('meg/%s/%s_AraSurp_NR-raw.fif' %(subject,subject1),preload=True)
	raw.filter(l_freq=0.1,h_freq=40,method='iir')
	ica.fit(raw,reject = dict(mag=4e-12))
	#ica.fit(raw)
	ica.plot_sources(raw)
        #raw_input('Press enter to continue')   #python 2
	input('Press enter to continue')  #python 3
	raw=ica.apply(raw,exclude=ica.exclude)
	raw.save('meg/%s/%s-ica-raw.fif' %(subject,subject1), overwrite=True)
	del raw,ica
'''

'''no nave version
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
		fs = mne.read_source_spaces(subjects_dir + '/%s/bem/%s-ico-4-src.fif' % (subject_to, subject_to))
		#vertices_to = [fs[0]['vertno'], fs[1]['vertno']]
		vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir=subjects_dir)
		subject_from = subject

		for stc_from in eps:
			print ("Morphing source estimate for epoch %d" %counter) #python 3
			# use the morph function
			morph = mne.compute_source_morph(stc_from, subject_from, subject_to, spacing=4, subjects_dir=subjects_dir)
			stc = morph.apply(stc_from)
			eps_morphed.append(stc)
			counter += 1
			eps = eps_morphed
	if save_to_disk:
		pass
		#with open(op.join(stc_cont, '%s_stc_epochs.pickled' %subject), 'w') as fileout:
			#pickle.dump(eps, fileout)
	return eps
'''

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



event_id = dict(Hroot_Hlin_VIII=64, Lroot_Hlin_VIII=34, Hroot_Llin_VIII=41, Lroot_Llin_VIII=21, Hroot_Hlin_VII=71, Hroot_Llin_VII=25, Lroot_Hlin_VII=18, Lroot_Llin_VII=37, Hroot_Hlin_I=7, Lroot_Hlin_I=6, Hroot_Llin_I=5, Lroot_Llin_I=11, NA_Hroot_Hlin_I=12, NA_Hroot_Hlin_VII=15, NA_Hroot_Hlin_VIII=16, NA_Hroot_Llin_I=13, NA_Hroot_Llin_VII=20, NA_Hroot_Llin_VIII=10,NA_Lroot_Hlin_I=14, NA_Lroot_Hlin_VII=8, NA_Lroot_Hlin_VIII=9, NA_Lroot_Llin_I=76, NA_Lroot_Llin_VII=4, NA_Lroot_Llin_VIII=30)

#subjects = ['P009','P015','P022','P028','P030','P031','P033','P034']
#subjects = ['P002','P009','P010','P015','P018','P022','P026','P028','P030','P031','P033','P034','P035','P036','P037','P038','P039','P040']
#subjects = ['P036','P037','P038','P039','P040']
subjects = ['Y0322','Y0323','Y0327','Y0333','Y0345','Y0346','Y0347','Y0348','Y0349','Y0350','Y0351','Y0352','Y0353','Y0355','Y0356','Y0357','Y0358','Y0359']
#'Y0157','Y0215','Y0319','Y0320','Y0321',

for s in subjects:
	subject = s

	raw = mne.io.read_raw_fif(main_exp_dir + 'meg/%s/%s-ica-raw.fif' %(subject,subject),preload=True)

	events = mne.find_events(raw,min_duration=0.002)
	events_ = events
	events_[:,0] = events_[:,0] + 50 #includes 50ms audio delay

	reject = dict(mag=4e-12)
	#epochs = mne.Epochs(raw,events_,event_id,tmin=-0.1,tmax=1.1,baseline=(-0.1,0),reject=reject)
	epochs = mne.Epochs(raw,events_,event_id,tmin=-0.1,tmax=1.1,baseline=((None,None)),reject=reject) #no baseline correction
	epochs.drop_bad()
	#%store epochs.drop_log >> 'P036_droplog.txt'
	#rejfile = eelbrain.load.unpickle('TagSurp/meg/%s/epoch selection/TagSurp_raw_epoch-man.pickled' %subject)
	####if standard rejfile is not sufficient due to automatic epoch rejection:
	eelbrain.gui.select_epochs(epochs,mark=['MEG 087','MEG 130'])

	input('NOTE: Save as meg/%s/%s_rejfile.pickled. \nPress enter when you are done rejecting epochs in the GUI...'%(subject,subject))
	if os.path.isfile(main_exp_dir + 'meg/%s/epoch selection/AraSurp_raw_epoch-man_corrected.pickled'%subject):
		rejfile = eelbrain.load.unpickle(main_exp_dir + 'meg/%s/epoch selection/AraSurp_raw_epoch-man_corrected.pickled' %subject)
	else:
		rejfile = eelbrain.load.unpickle(main_exp_dir + 'meg/%s/epoch selection/AraSurp_raw_epoch-man.pickled' %subject)
	rejs = rejfile['accept'].x
	epochs_rej = epochs[rejs]
	epochs = epochs_rej
	#print epochs
	#'''

	#trans = mne.read_trans(main_exp_dir + 'meg/%s/%s-trans.fif' %(subject,subject))
	#bem = glob.glob(subjects_dir + '/%s/bem/*-bem-sol.fif' %subject)[0]

	'''

	#make evokeds
	ev_Hroot_Hlin_VIII = epochs['Hroot_Hlin_VIII']
	ev_Lroot_Hlin_VIII = epochs['Lroot_Hlin_VIII']
	ev_Hroot_Llin_VIII = epochs['Hroot_Llin_VIII']
	ev_Lroot_Llin_VIII = epochs['Lroot_Llin_VIII']
	ev_Hroot_Hlin_VII = epochs['Hroot_Hlin_VII']
	ev_Hroot_Llin_VII = epochs['Hroot_Llin_VII']
	ev_Lroot_Hlin_VII = epochs['Lroot_Hlin_VII']
	ev_Lroot_Llin_VII = epochs['Lroot_Llin_VII']
	ev_Hroot_Hlin_I = epochs['Hroot_Hlin_I']
	ev_Lroot_Hlin_I = epochs['Lroot_Hlin_I']
	ev_Hroot_Llin_I = epochs['Hroot_Llin_I']
	ev_Lroot_Llin_I = epochs['Lroot_Llin_I']
	ev_NA_Hroot_Hlin_I = epochs['NA_Hroot_Hlin_I']
	ev_NA_Hroot_Hlin_VII = epochs['NA_Hroot_Hlin_VII']
	ev_NA_Hroot_Hlin_VIII = epochs['NA_Hroot_Hlin_VIII']
	ev_NA_Hroot_Llin_I = epochs['NA_Hroot_Llin_I']
	ev_NA_Hroot_Llin_VII = epochs['NA_Hroot_Llin_VII']
	ev_NA_Hroot_Llin_VIII = epochs['NA_Hroot_Llin_VIII']
	ev_NA_Lroot_Hlin_I = epochs['NA_Lroot_Hlin_I']
	ev_NA_Lroot_Hlin_VII = epochs['NA_Lroot_Hlin_VII']
	ev_NA_Lroot_Hlin_VIII = epochs['NA_Lroot_Hlin_VIII']
	ev_NA_Lroot_Llin_I = epochs['NA_Lroot_Llin_I']
	ev_NA_Lroot_Llin_VII = epochs['NA_Lroot_Llin_VII']
	ev_NA_Lroot_Llin_VIII = epochs['NA_Lroot_Llin_VIII']

	'''
	'''
	####make evoked averages!
	epochs.equalize_event_counts(event_id)

	ev_Hroot_Hlin_VIII = epochs['Hroot_Hlin_VIII'].average()
	ev_Lroot_Hlin_VIII = epochs['Lroot_Hlin_VIII'].average()
	ev_Hroot_Llin_VIII = epochs['Hroot_Llin_VIII'].average()
	ev_Lroot_Llin_VIII = epochs['Lroot_Llin_VIII'].average()
	ev_Hroot_Hlin_VII = epochs['Hroot_Hlin_VII'].average()
	ev_Hroot_Llin_VII = epochs['Hroot_Llin_VII'].average()
	ev_Lroot_Hlin_VII = epochs['Lroot_Hlin_VII'].average()
	ev_Lroot_Llin_VII = epochs['Lroot_Llin_VII'].average()
	ev_Hroot_Hlin_I = epochs['Hroot_Hlin_I'].average()
	ev_Lroot_Hlin_I = epochs['Lroot_Hlin_I'].average()
	ev_Hroot_Llin_I = epochs['Hroot_Llin_I'].average()
	ev_Lroot_Llin_I = epochs['Lroot_Llin_I'].average()
	ev_NA_Hroot_Hlin_I = epochs['NA_Hroot_Hlin_I'].average()
	ev_NA_Hroot_Hlin_VII = epochs['NA_Hroot_Hlin_VII'].average()
	ev_NA_Hroot_Hlin_VIII = epochs['NA_Hroot_Hlin_VIII'].average()
	ev_NA_Hroot_Llin_I = epochs['NA_Hroot_Llin_I'].average()
	ev_NA_Hroot_Llin_VII = epochs['NA_Hroot_Llin_VII'].average()
	ev_NA_Hroot_Llin_VIII = epochs['NA_Hroot_Llin_VIII'].average()
	ev_NA_Lroot_Hlin_I = epochs['NA_Lroot_Hlin_I'].average()
	ev_NA_Lroot_Hlin_VII = epochs['NA_Lroot_Hlin_VII'].average()
	ev_NA_Lroot_Hlin_VIII = epochs['NA_Lroot_Hlin_VIII'].average()
	ev_NA_Lroot_Llin_I = epochs['NA_Lroot_Llin_I'].average()
	ev_NA_Lroot_Llin_VII = epochs['NA_Lroot_Llin_VII'].average()
	ev_NA_Lroot_Llin_VIII = epochs['NA_Lroot_Llin_VIII'].average()
	#'''

	'''
	factors = condition_format.split('_')
	fts = {f: {} for f in factors}
	for cond in event_id.keys():
		cond_split = cond.split('_')
		for i, l in enumerate(cond_split):
			fts[factors[i]].setdefault(l, [])
			fts[factors[i]][l].append(event_id[cond])
	factors = factors
	factorial_trigger_scheme = fts

	for factor in factorial_trigger_scheme.keys():
		for level in factorial_trigger_scheme[factor].keys():
			print "Making evoked for %s" %level
			ep = epochs[np.in1d(epochs.events[:,2], factorial_trigger_scheme[factor][level])]
			#av = ep.average()
			#av.comment = level
			#evokeds.append(av)
			evokeds.append(ep)
			conds.append(level)
	'''

	trans = mne.read_trans(main_exp_dir + 'meg/%s/%s-trans.fif' %(subject,subject))
	bem = glob.glob(subjects_dir + '/%s/bem/*-bem-sol.fif' %subject)[0]
	src = mne.setup_source_space(subject=subject,spacing='ico4',subjects_dir=subjects_dir)
	mne.write_source_spaces(main_exp_dir + 'meg/%s/%s-src.fif' %(subject,subject),src,overwrite=True)
	cov = mne.compute_covariance(epochs,tmin=None,tmax=None,method='empirical') #no baseline correction
	pickle.dump(cov,open(main_exp_dir + 'meg/%s/%s-cov' %(subject,subject),'wb'))
	info = epochs.info
	pickle.dump(info,open(main_exp_dir + 'meg/%s/%s-info' %(subject,subject),'wb'))
	fwd = mne.make_forward_solution(info, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	fwd = mne.convert_forward_solution(fwd,force_fixed=True)
	mne.write_forward_solution(main_exp_dir + 'meg/%s/%s-fwd.fif'  %(subject,subject),fwd,overwrite=True)
	inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, loose=0,fixed=True)
	pickle.dump(inv,open(main_exp_dir + 'meg/%s/%s-inv' %(subject,subject),'wb'))


	####writing everything the first time
	'''
	##cov = mne.compute_covariance(epochs,tmin=-0.1,tmax=0,method='empirical')
	cov = mne.compute_covariance(epochs,tmin=None,tmax=None,method='empirical') #no baseline correction
	pickle.dump(cov,open(main_exp_dir + 'meg/%s/%s-cov' %(subject,subject),'wb'))

	#src = mne.read_source_spaces(main_exp_dir + 'meg/%s/%s-src.fif' %(subject,subject))
	#info = epochs.info
	#pickle.dump(info,open(main_exp_dir + 'meg/%s/%s-info' %(subject,subject),'wb'))
	src = mne.setup_source_space(subject=subject,spacing='ico4',subjects_dir=subjects_dir)
	mne.write_source_spaces(main_exp_dir + 'meg/%s/%s-src.fif' %(subject,subject),src,overwrite=True)

	#check at this place everything is inside the brain!

	##cov_eq = mne.compute_covariance(epochs,tmin=-0.1,tmax=0,method='empirical')
	#cov_eq = mne.compute_covariance(epochs,tmin=None,tmax=None,method='empirical') #no baseline correction
	#pickle.dump(cov_eq,open(main_exp_dir + 'meg/%s/%s-cov_eq' %(subject,subject),'wb'))

	info_eq = epochs.info
	pickle.dump(info_eq,open(main_exp_dir + 'meg/%s/%s-info_eq' %(subject,subject),'wb'))
	#fwd = mne.make_forward_solution(info, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	#fwd = mne.convert_forward_solution(fwd,force_fixed=True)
	#mne.write_forward_solution(main_exp_dir + 'meg/%s/%s-fwd.fif'  %(subject,subject),fwd,overwrite=True)
	fwd_eq = mne.make_forward_solution(info_eq, trans,src,bem,meg=True,eeg=False,ignore_ref=True)
	fwd_eq = mne.convert_forward_solution(fwd_eq,force_fixed=True)
	mne.write_forward_solution(main_exp_dir + 'meg/%s/%s-fwd_eq.fif'  %(subject,subject),fwd_eq,overwrite=True)
	#inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, loose=0,fixed=True)
	#pickle.dump(inv,open(main_exp_dir + 'meg/%s/%s-inv' %(subject,subject),'wb'))
	inv_eq = mne.minimum_norm.make_inverse_operator(info_eq, fwd_eq, cov_eq, depth=None, loose=0,fixed=True)
	pickle.dump(inv_eq,open(main_exp_dir + 'meg/%s/%s-inv_eq' %(subject,subject),'wb'))
	'''


	####reading everything in after it's been written
	#'''
	src = mne.read_source_spaces(main_exp_dir + 'meg/%s/%s-src.fif' %(subject,subject))
	cov = eelbrain.load.unpickle(main_exp_dir + 'meg/%s/%s-cov' %(subject,subject))
	info = eelbrain.load.unpickle(main_exp_dir + 'meg/%s/%s-info' %(subject,subject))
	fwd = mne.read_forward_solution(main_exp_dir + 'meg/%s/%s-fwd.fif'  %(subject,subject))
	fwd = mne.convert_forward_solution(fwd,force_fixed=True) #missing from previous exps... FUCKING GREAT!!!
	inv = eelbrain.load.unpickle(main_exp_dir + 'meg/%s/%s-inv' %(subject,subject))
	#'''


	conditions = [ev_compound, ev_reduplicate, ev_phonemic_in, ev_infix_in, ev_circumfix, ev_prefix, ev_morph_simple]

	filenames = ['compound', 'reduplicate','phonemic_in','infix_in','circumfix','prefix','morph_simple']
	i = 0
	vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir=subjects_dir)

	for cond in conditions:
		#'''
		###for epoch stcs
		myepochs = epochs[filenames[i]].average()
		mynave = myepochs.nave
		eps = make_epoch_stcs(cond,mynave)
		a = 1
		for ep in eps:
			ep.save(main_exp_dir + 'stc/%s%s%s' %(subject,filenames[i],a))
			a = a+1
		i = i+1

		###for average stcs
		'''
		lambda2 = 1.0 / 3.0 ** 2
		my_stc = mne.minimum_norm.apply_inverse(cond,inv_eq,lambda2=lambda2,verbose=False,method='dSPM')
		if i == 0:
			subject_from = subject
			subject_to = 'fsaverage'
			morph = mne.compute_source_morph(my_stc, subject_from, subject_to, spacing=4,subjects_dir=subjects_dir)
			stc_morphed = morph.apply(my_stc)
			stc_morphed.save(main_exp_dir + 'average_stc_equalized_counts/%s%s' %(subject,filenames[i]))
		else:
			stc_morphed = morph.apply(my_stc)
			stc_morphed.save(main_exp_dir + 'average_stc_equalized_counts/%s%s' %(subject,filenames[i]))
		i = i+1
		###my_stc.save('TagInfRed/stc/%s%s' %(subject,filenames[i]))
		#'''




#############Read in to DS##############################
subjects = ['P002','P009','P010','P015','P018','P022','P026','P028','P030','P031','P033','P034','P035','P036','P037'] #needs 26 once that's done

subjects_all = ['P002','P009','P010','P015','P018','P022','P026','P028','P030','P031','P033','P034','P035','P036','P037','P038','P039','P040']
subjects_no_18 = ['P002','P009','P010','P015','P022','P026','P028','P030','P031','P033','P034','P035','P036','P037','P038','P039','P040']

subjects = subjects_all
#my_stc_names = ['compound', 'reduplicate','phonemic_in','infix_in','circumfix','prefix','morph_simple']
my_stc_names = ['compound', 'reduplicate']

stcs,subject,cond = [],[],[]
for sbj in subjects:
	stc_path = main_exp_dir + 'average_stc_equalized_counts/%s' %sbj
	for i in my_stc_names:
		stc = mne.read_source_estimate(stc_path + i + '-lh.stc')
		stcs.append(stc)
		cond.append(str.split(i,'%s' %sbj)[0])
		subject.append(sbj)
		del stc
		print ("done!")



ds = eelbrain.Dataset()
ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir=subjects_dir,method='dSPM',fixed=True,parc='aparc')
ds['Condition'] = eelbrain.Factor(cond)
ds['Subject'] = eelbrain.Factor(subject,random=True)
ds_backup = ds

'''
tstart = .4
tstop = .41
newtime = ds['stc']
mytime = newtime.sub(time=(tstart,tstop))
ds['stc']=mytime
'''

src = ds['stc']
#src.source.set_parc('aparc')
src_region = src.sub(source='superiortemporal-lh')
ds['stc']=src_region

timecourse = ds['stc'].mean('source')
activation = eelbrain.plot.UTSStat(timecourse,'Condition',match='Subject',ds=ds,xlim=(0.0,1),legend='upper right', title='STG-lh, TagSurp, n=all (19)')


plt.plot(timecourse.time,timecourse[0],color='red')
plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('STG-lh activity - n=15')
tstart = .7
plt.axvline(tstart,color='lightgrey',alpha=2)
plt.xlim = tstart
plt.savefig('tagsurp_stg-lh.png')
plt.clf()


fig = eelbrain.plot.brain.dspm(ds['stc'],fmin=0.0001, fmax=1.5, surf="inflated",smoothing_steps=15,w=1000, h=800, hemi='lh',views=['lat','ven'])
fig.set_parallel_view(scale=95)

fig.save_movie(main_exp_dir + 'n19_compounds_reduplicates.mov',time_dilation=32,framerate=72,tmin=0,tmax=1.0) #doesn't work

res = eelbrain.testnd.ttest_ind('stc', x='Condition', c1='compound', c0='reduplicate', ds=ds, pmin=0.05, tstart=0., tstop=0.8, samples=0, match='Subject', mintime=0.02, minsource=20)
brain = eelbrain.plot.brain.cluster(res.t, surf='inflated', views=['lat','ven'], cortex='low_contrast', subjects_dir=subjects_dir, smoothing_steps=10, w=1000, h=800, hemi='lh')
brain.set_parallel_view(scale=95)
brain.save_movie(main_exp_dir + 'test_tmap_movie.mov',time_dilation=32,framerate=72,tmin=0,tmax=0.8)


x = [(0.0,0.01),(0.01,0.02),(0.02,0.03),(0.03,0.04),(0.04,0.05),(0.05,0.06),(0.06,0.07),(0.07,0.08),(0.08,0.09),(0.09,0.1),(0.1,0.11),(0.11,0.12),(0.12,0.13),(0.13,0.14),(0.14,0.15),(0.15,0.16),(0.16,0.17),(0.17,0.18),(0.18,0.19),(0.19,0.20),(0.2,0.21),(0.21,0.22),(0.22,0.23),(0.23,0.24),(0.24,0.25),(0.25,0.26),(0.26,0.27),(0.27,0.28),(0.28,0.29),(0.29,0.3),(0.3,0.31),(0.31,0.32),(0.32,0.33),(0.33,0.34),(0.34,0.35),(0.35,0.36),(0.36,0.37),(0.37,0.38),(0.38,0.39),(0.39,0.40),(0.4,0.41),(0.41,0.42),(0.42,0.43),(0.43,0.44),(0.44,0.45),(0.45,0.46),(0.46,0.47),(0.47,0.48),(0.48,0.49),(0.49,0.5),(0.5,0.51),(0.51,0.52),(0.52,0.53),(0.53,0.54),(0.54,0.55),(0.55,0.56),(0.56,0.57),(0.57,0.58),(0.58,0.59),(0.59,0.60),(0.6,0.61),(0.61,0.62),(0.62,0.63),(0.63,0.64),(0.64,0.65),(0.65,0.66),(0.66,0.67),(0.67,0.68),(0.68,0.69),(0.69,0.7),(0.7,0.71),(0.71,0.72),(0.72,0.73),(0.73,0.74),(0.74,0.75),(0.75,0.76),(0.76,0.77),(0.77,0.78),(0.78,0.79),(0.79,0.80),(0.80,0.81),(0.81,0.82),(0.82,0.83),(0.83,0.84),(0.84,0.85),(0.85,0.86),(0.86,0.87),(0.87,0.88),(0.88,0.89),(0.89,0.9),(0.9,0.91),(0.91,0.92),(0.92,0.93),(0.93,0.94),(0.94,0.95),(0.95,0.96),(0.96,0.97),(0.97,0.98),(0.98,0.99),(0.99,1.0)]

for a,b in x:
	ds = ds_backup
	tstart = a
	tstop = b
	newtime = ds['stc']
	mytime = newtime.sub(time=(tstart,tstop))
	ds['stc']=mytime
	fig = eelbrain.plot.brain.dspm(ds['stc'],fmin=0.0001, fmax=1.5, surf="inflated",smoothing_steps=15)
    	fig.save_image(main_exp_dir + 'NordMap/figs/tmap_movies/words_from_letters_fixationCross/words_from_letters_fixationCross_%s-%s.png' %(a,b))

parc = mne.read_labels_from_annot('fsaverage','aparc',subjects_dir=subjects_dir,hemi='lh') #read in the parcellation here. Typical options are aparc or Brodmann
labels = [i for i in parc if (i.name == 'superiortemporal-lh')]
label = labels[0]
fig.add_label(label,color="black",borders=True) #plot your ROI

parc = mne.read_labels_from_annot('fsaverage','PALS_B12_Brodmann',subjects_dir=subjects_dir,hemi='lh') #read in the parcellation here. Typical options are aparc or Brodmann
labels = [i for i in parc if (i.name == 'Brodmann.22-lh')]
label = labels[0]
fig.add_label(label,color="black",borders=True) #plot your ROI


fig.add_annotation('aparc',borders=True,remove_existing=True) #plot your ROI
fig.add_annotation('PALS_B12_Brodmann',borders=True,remove_existing=True) #plot your ROI
