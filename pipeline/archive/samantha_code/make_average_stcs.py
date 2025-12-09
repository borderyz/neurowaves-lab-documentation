## RUN THIS *ipython* IN THE EELBRAIN ENVIRONMENT


# D. A. Chacón (2020)

# Based off of code from Julien Dirani
# ---File structure----
# ROOT>
#     MRI>
#         subjs
#     MEG>
#         subjs
#     STC>

# epochs rejection based on log files not included


# ----------File structure-----------#
# ROOT>
#     MRI>
#         subjs
#     MEG>
#         subjs
#     STC>


import mne, eelbrain, os, glob, pickle
import numpy as np
import pandas as pd
from os.path import join

from main import *

mne.set_log_level(verbose='WARNING')

#=========Edit here=========#

SNR = 3 # 3 for ANOVAs, 2 for regressions
fixed = True # False for orientation free (=unsigned), True for fixed orientation (=signed)

#os.chdir(ROOT) #setting current dir
exp = 'savant_main/'
#os.chdir(ROOT) #setting current dir
subjects_dir = ('new_baseline/' + exp + '/mri')
#subjects = ['Y0312','Y0321','Y0366','Y0367','Y0368','Y0369','Y0371','Y0372','Y0373','Y0374','Y0375','Y0377','Y0378','Y0381','Y0382','Y0383','Y0388','Y0393']
#subjects = ['Y0366',Y0367','Y0368','Y0369','Y0371','Y0373','Y0374','Y0375','Y0377','Y0378']
#'Y0388',
subjects = ['Y0119','Y0208','Y0312','Y0321','Y0368','Y0371','Y0367','Y0369','Y0373','Y0374','Y0378','Y0379','Y0381','Y0382','Y0387','Y0393','Y0395','Y0396']
#subjects = ['Y0321','Y0367','Y0368','Y0369','Y0373','Y0374','Y0375','Y0377','Y0378','Y0379','Y0381','Y0382','Y0383','Y0387','Y0388','Y0393','Y0394']
#'Y0367' - didn't work?,'Y0312','Y0321','Y0366','Y0368','Y0369','Y0371','Y0373','Y0374','Y0377','Y0378'
# '''==========================================================================='''
# '''                             PART 3: Create STCs                           '''
# '''==========================================================================='''

#---------------------------average STCs------------------------------------#

for subj in subjects:
    if os.path.exists('stc_average/' + exp + '%s' %subj):
        print('Looks like we started this subject already! Lets just check in :)')
#        print('STCs ALREADY CREATED FOR SUBJ = %s' %subj)
    else:
        os.makedirs('stc_average/' + exp + '%s' %subj)
    if True:
        print(">> STCs for subj=%s:"%subj)
        print('Importing data...')

        #info = pickle.load(open('savant_tark/meg/%s/%s-info.pickled' %(subj,subj), 'rb'))
        #temp#epochs_rej = mne.read_epochs('savant_tark/meg/%s/%s_TarkAra_1-40-ica-rej-epo.fif' %(subj,subj))
        #epochs_ica = mne.read_epochs("new_baseline/" + exp + "meg/%s/%s_TarkAra_1-40-ica-epo.fif" %(subj,subj))
        epochs_ica = mne.read_epochs("new_baseline/" + exp + "meg/%s/%s_SavantAra_1-40-ica-epo.fif" %(subj,subj))

        info = epochs_ica.info
        pickle.dump(info, open('new_baseline/' + exp + 'meg/%s/%s-info.pickled' %(subj,subj), 'wb'))
        info = pickle.load(open('new_baseline/' + exp + 'meg/%s/%s-info.pickled' %(subj,subj), 'rb'))



#        rejfile = pd.read_csv("MEG/%s/%s_rejfile.pickled" %(subj,subj), sep="\t")
        #temp#rejfile = pickle.load(open("savant_tark/meg/%s/%s_rejfile.pickled" %(subj,subj), 'rb'))
        #temp#rejs = rejfile['accept'].x

#        rej_id = np.where(rejfile.accept==True)[0]

        #temp#epochs = mne.read_epochs("savant_tark/meg/%s/%s-all-epo.fif" %(subj,subj))
        #temp#epochs_rej = epochs[rejs]
        trans = mne.read_trans('new_baseline/' + exp + 'meg/%s/%s-trans.fif' %(subj,subj))

        bem_fname = join(subjects_dir, '%s/bem/%s-inner_skull-bem-sol.fif'%(subj,subj))
        src_fname = join(subjects_dir, '%s/bem/%s-ico-4-src.fif' %(subj,subj))
        fwd_fname = 'new_baseline/' + exp + 'meg/%s/%s-average-fwd.fif' %(subj,subj)
        cov_fname = 'new_baseline/' + exp + 'meg/%s/%s-average-cov.fif' %(subj,subj)


        #----------------------Source space---------------------------#
        print('Generating source space...')
        if os.path.isfile(src_fname):
            print('src for subj = %s already exists, loading file...' %subj)
            src = mne.read_source_spaces(fname=src_fname)
            print('Done.')
        else:
            print('src for subj = %s does not exist, creating file...' %subj)
            src = mne.setup_source_space(subject=subj, spacing='ico4', subjects_dir=subjects_dir)
            src.save(src_fname, overwrite=True)
            print('Done. File saved.')

        #-------------------------- BEM ------------------------------#
        if not os.path.isfile(bem_fname):
            print('BEM for subj=%s does not exists, creating...' %subj)
            conductivity = (0.3,) # for single layer
            model = mne.make_bem_model(subject=subj, ico=4, conductivity=conductivity, subjects_dir=subjects_dir)
            bem = mne.make_bem_solution(model)
            mne.write_bem_solution(bem_fname, bem)

        #--------------------Forward solution-------------------------#
        print('Creating forward solution...')
        if os.path.isfile(fwd_fname):
            print('forward solution for subj=%s exists, loading file.' %subj)
            fwd = mne.read_forward_solution(fwd_fname)
            print('Done.')
        else:
            print('forward solution for subj=%s does not exist, creating file.' %subj)
            fwd = mne.make_forward_solution(info=info, trans=trans, src=src, bem=bem_fname, ignore_ref=True)
            mne.write_forward_solution(fwd_fname, fwd)
            print('Done. File saved.')


        #----------------------Covariance------------------------------#
        print('Getting covariance')
        if os.path.isfile(cov_fname):
            print('covariance matrix for subj=%s exists, loading file...' %subj)
            cov = mne.read_cov(cov_fname)
            print('Done.')
        else:
            print('covariance matrix for subj=%s does not exist, creating file...' %subj)
            cov = mne.compute_covariance(epochs_ica,tmin=None,tmax=0, method=['shrunk', 'diagonal_fixed', 'empirical'])
            cov.save(cov_fname)
            print('Done. File saved.')


        #---------------------Inverse operator-------------------------#
        print('Making inverse operator')
        if fixed == True:
            fwd = mne.convert_forward_solution(fwd, surf_ori=True)

        inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, #loose=None,
          fixed=fixed) #fixed=False: Ignoring dipole direction.
        lambda2 = 1.0 / SNR ** 2.0

        #--------------------------STCs--------------------------------#

        print('%s: Creating STCs...'%subj)
        '''
        trialNumber = 0
        i = 0 # iterating over the 'epochs' (good and bad)
        j = 0 # iterating over the 'epochs_ICA' (good ICA'd only)

        #temp#while i < len(epochs):
        while i < len(epochs_ica):
            intersect = []
            #temp#for item in epochs[i].event_id.keys():
            for item in epochs_ica[i].event_id.keys():
                #temp#if rejfile[i]['accept'] == True:
                    if os.path.exists('stc/' + exp + '%s/%s_%s_%s_dSPM-lh' %(subj, subj, str(i), item)):
                        print('STC already made')
                        i += 1
                        j += 1
                        trialNumber += 1
                    else:
                        print(i,item, ", creating STC...")

                        evoked = epochs_ica[j].average()
                        stc = mne.minimum_norm.apply_inverse_epochs(epochs_ica[j], inv, lambda2=lambda2, method="dSPM", nave=evoked.nave)
                        stc = stc[0]

                        vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir=subjects_dir) #fsaverage's source space
                        morph_mat = mne.compute_morph_matrix(subject_from=subj, subject_to='fsaverage', vertices_from=stc.vertices, vertices_to=vertices_to, subjects_dir=subjects_dir)
                        stc_morph = mne.compute_source_morph(stc,subject_from=subj, subject_to='fsaverage', #stc_from=stc,
                         #vertices_to=vertices_to,
                         #morph_mat=morph_mat
                         spacing=4,
                         subjects_dir = subjects_dir
                         ).apply(stc)
                        stc_morph.save('stc/' + exp + '%s/%s_%s_%s_dSPM' %(subj, subj, str(i), item))
                        del stc, stc_morph
                        i += 1
                        j += 1
                        trialNumber += 1
                #temp#else:
                #temp#    print(i, item, "rejected!")
                #temp#    i += 1
#                print(item)
#                if item in critical_conditions.keys():
#                    intersect.append(item)





        '''
        epochs_ica.equalize_event_counts(event_id)
        evoked = []
        for item in epochs_ica.event_id.keys():
            print(item)
            evoked.append(epochs_ica[item].average())

        for ev in evoked:
            stc = mne.minimum_norm.apply_inverse(ev, inv, lambda2=lambda2, method='dSPM') # This will get you signed data: said for pick_ori which can only be performed on free data
            # mophing stcs to the fsaverage using precomputed matrix method:
            vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir=subjects_dir) #fsaverage's source space
            morph_mat = mne.compute_morph_matrix(subject_from=subj, subject_to='fsaverage', vertices_from=stc.vertices, vertices_to=vertices_to, subjects_dir=subjects_dir)
            stc_morph = mne.compute_source_morph(stc,subject_from=subj, subject_to='fsaverage', #stc_from=stc,
#                #vertices_to=vertices_to,
#                #morph_mat=morph_mat
                spacing=4,
                subjects_dir = subjects_dir
                ).apply(stc)
            stc_morph.save('stc_average/'+ exp + '%s/%s_%s_dSPM' %(subj,subj,ev.comment))
#            del stc, stc_morph
        print('>> DONE CREATING STCS FOR SUBJ=%s'%subj)
        print('-----------------------------------------\n')

        #deleting variables
        del info, trans, src, fwd, cov, inv#, epochs_rej, evoked
