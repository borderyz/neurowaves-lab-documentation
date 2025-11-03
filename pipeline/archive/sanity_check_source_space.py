################################################################################
#     Generating Source Spaces and FWD Models + Sanity Checks: Post coreg      #
################################################################################

# ********** #
## ***** Please change this script to match your file names and paths ***** ##
# BUT DO NOT OVERWRITE THE COPY ON THE SERVER #
# ********** #


# The following code is an example of how to generate the source space for a
# single subject from the BEM, plot the sources in the cortical reconstruction,
# compute a forward solution, and generate two maps of sensitivities in source space

import mne

subject = 'Y0119'
subjects_dir = '../input_data_experimental/mri/'

# Plot the BEM:
mne.viz.plot_bem(subject=subject, subjects_dir = subjects_dir, brain_surfaces='white',orientation='coronal')

## Compute the source space
#UNCOMMENT
#src = mne.setup_source_space(subject,spacing='ico4',subjects_dir=subjects_dir)
#UNCOMMENT
#src.save('../input_data_experimental/mri/%s/bem/%s-ico-4-src.fif' %(subject,subject), overwrite=True)
src = mne.read_source_spaces('../input_data_experimental/mri/%s/bem/%s-ico-4-src.fif' %(subject,subject))
# Plot the bem with the sources
mne.viz.plot_bem(subject=subject, subjects_dir=subjects_dir,brain_surfaces='white',
src=src, orientation='coronal')

# More detailed way of plotting the sources:
import numpy as np
from mayavi import mlab
from surfer import Brain
subjects_dir = '../input_data_experimental/mri/'

brain = Brain(subject,'lh','inflated',subjects_dir=subjects_dir)
surf=brain.geo['lh']
vertidx = np.where(src[0]['inuse'])[0]
mlab.points3d(surf.x[vertidx], surf.y[vertidx], surf.z[vertidx], color=(1,1,0),scale_factor=1.5)

## Create the bem solution.
conductivity = (0.3,) # for single layer
#UNCOMMENT
directory = r'C:\Users\hz3752\PycharmProjects\meg-pipeline\input_data_experimental\mri'

model = mne.make_bem_model(subject=subject,ico=4,conductivity=conductivity,subjects_dir=directory)
#UNCOMMENT
bem = mne.make_bem_solution(model)
#UNCOMMENT
path = r'C:\Users\hz3752\PycharmProjects\meg-pipeline\input_data_experimental\mri\Y0119\bem\Y0119-inner_skull-bem.fif'

mne.write_bem_solution(path,bem)

bem = mne.read_bem_solution(path)

# Make forward solution
# See here for detail:
#https://martinos.org/mne/stable/auto_tutorials/plot_forward.html
#https://martinos.org/mne/dev/generated/mne.viz.plot_alignment.html


raw_fname='meg/%s/%s_MASC_1-raw.fif' %(subject,subject)

#UNCOMMENT
#fwd = mne.make_forward_solution(raw_fname,trans='../input_data_experimental/meg/%s/%s-trans.fif' %(subject,subject),src=src,bem=bem,meg=True,eeg=False,ignore_ref=True)
#UNCOMMENT
#mne.write_forward_solution('../input_data_experimental/meg/%s/%s-fwd.fif' %(subject,subject),fwd)
fwd = mne.read_forward_solution('../input_data_experimental/meg/%s/%s-fwd.fif' %(subject,subject))
# The ico4 source space has 2562 sources per hemi = 5124 sources total
# fwd solution with free orientation has 3 dipoles at each source = 15372
# and 208 channels
# Check that this matches:
print(fwd['sol']['data'].shape)

# We can get the gain matrix:
leadfield = fwd['sol']['data']


# Compute sensitivity maps
mag_map = mne.sensitivity_map(fwd, ch_type='mag',mode='free')
mag_map.save('../input_data_experimental/meg/%s/%s_sensitivity-free' %(subject,subject))
brainmap = mag_map.plot(time_label='Magnetometer Sensitivity', subjects_dir=subjects_dir,clim=dict(lims=[0,50,100]),hemi='split')

# Using fixed
fwd_fixed = mne.convert_forward_solution(fwd, surf_ori=True,force_fixed=True,
use_cps=True)
leadfield = fwd_fixed['sol']['data']

# Compute sensitivity maps
mag_map = mne.sensitivity_map(fwd, ch_type='mag',mode='fixed')
mag_map.save('../input_data_experimental/meg/%s/%s_sensitivity-fixed' %(subject,subject))
brainmap = mag_map.plot(time_label='Magnetometer Sensitivity', subjects_dir=subjects_dir,clim=dict(lims=[0,50,100]),hemi='split')

