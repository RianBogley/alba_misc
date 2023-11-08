# %% IMPORT MODULES ##############################################################
import pymeshlab
import os
import nipype
import scipy
import matplotlib.pyplot as plt
import nipype.interfaces.freesurfer as fs

##################################################################################
# %% SETTINGS: ###################################################################
# Specify filepath to freesurfer data:
fs_filepath = 'L:/language/rbogley/3D_Printing/'

# Specify output filepath for STL files:
fs_output = 'L:/language/rbogley/3D_Printing/FreeSurfer_Output/'
meshlab_output = 'L:/language/rbogley/3D_Printing/Finished_STL_Output/'

# Find all files in fs_output directory and extract PIDNs:
fs_output_files = os.listdir(fs_output)
pidn_list = [file.split('_')[0] for file in fs_output_files]
# Remove duplicates:
pidn_list = list(set(pidn_list))

# Print all PIDNs:
print(pidn_list)

##################################################################################
# %% MESHLAB #####################################################################

def meshlab_smooth_merge(pidn,
                         fs_input = fs_output,
                         meshlab_output = meshlab_output):
    """
    Smooth and merge cortical and subcortical STL files using MeshLab.
    """
    cortical_stl = os.path.join(fs_input, f'{pidn}_cortical.stl')
    subcortical_stl = os.path.join(fs_input, f'{pidn}_subcortical.stl')

    # Check if both files exist:
    if not os.path.exists(cortical_stl):
        print(f'{pidn} cortical file does not exist.')
        return
    if not os.path.exists(subcortical_stl):
        print(f'{pidn} subcortical file does not exist.')
        return

    # Create a new MeshSet:
    ms = pymeshlab.MeshSet()

    # Load both STL files into MeshLab:
    ms.load_new_mesh(cortical_stl)
    ms.load_new_mesh(subcortical_stl)

    # Apply ScaleDependent Laplacian Smooth Filter to both meshes using 100 smoothing steps and a delta of 0.1%:
    ms.apply_filter('apply_coord_laplacian_smoothing_scale_dependent', stepsmoothnum=100, delta=pymeshlab.Percentage(0.1), selected=False)

    # Flatten visible layers to single mesh:
    ms.flatten_visible_layers()

    # Generate by merging all visible layers:
    # ms.generate_by_merging_all_visible_meshes()

    # Export as STL file called "PIDN_Smoothed_Merged.stl":
    ms.save_current_mesh(os.path.join(meshlab_output, f'{pidn}_Smoothed_Merged.stl'))

for pidn in pidn_list:
    # Check if finished STL file exists in meshlab_output:
    if os.path.exists(os.path.join(meshlab_output, f'{pidn}_Smoothed_Merged.stl')):
        print(f'{pidn} already exists. Skipping...')
    else:
        print(f'Starting {pidn}...')
        meshlab_smooth_merge(pidn)
        print(f'{pidn} finished.')

#%%
##################################################################################
##################################################################################
################################# WIP BELOW ######################################
##################################################################################
##################################################################################
##################################################################################
# %% : ######################################################################
# SEE HERE: https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.freesurfer.html

pidn = ''
# Append PIDN to filepath using os
fs_filepath = os.path.join(fs_filepath, pidn) 

# Within PIDN folder, find the following STL files:
cortical_stl = os.path.join(fs_filepath, f'{pidn}_cortical.stl')
subcortical_stl = os.path.join(fs_filepath, f'{pidn}_subcortical.stl')

# 1. Set all freesurfer filepaths and files:

fs_mri_filepath = os.path.join(fs_filepath, 'mri')
fs_surf_filepath = os.path.join(fs_filepath, 'surf')
fs_lh_pial = os.path.join(fs_surf_filepath, 'lh.pial')
fs_rh_pial = os.path.join(fs_surf_filepath, 'rh.pial')
fs_aseg = os.path.join(fs_mri_filepath, 'aseg.mgz')

# Verify that all files exist:
if os.path.exists(fs_lh_pial) and os.path.exists(fs_rh_pial) and os.path.exists(fs_aseg):
    print('All necessary FreeSurfer files exist.')
else:
    print('One or more files do not exist. Please check filepath and files.')


#%%
# 2. Combine lh and rh pial surfaces into single cortical STL file
hemis_combine = fs.MRIsCombine()
hemis_combine.inputs.in_files = [fs_lh_pial, fs_rh_pial]
hemis_combine.inputs.out_file = cortical_stl
hemis_combine.cmdline
hemis_combine.run()


#%%
print('\nMerging lh.pial and rh.pial into cortical.stl')
cortical_convert = fs.MRIsConvert()




cortical_convert.inputs.out_datatype = 'stl'
cortical_convert.run() 
print('Cortical STL file created.')


mris_convert --combinesurfs $filepath_3DP/surf/lh.pial $filepath_3DP/surf/rh.pial $filepath_3DP/cortical.stl



# 3. Generate subcortical STL file

# 4. Smooth both STL files using MeshLab and merge into single STL file




# Navigate into /surf/ folder of freesurfer data:




##################################################################################

# %%


##################################################################################
##################################################################################
##################################################################################
##################################################################################
##################################################################################

#! /bin/sh






echo "Starting subcortical processing, which will result in subcortical.stl"
mri_convert $filepath_3DP/mri/aseg.mgz $filepath_3DP/subcortical.nii

mri_binarize --i $filepath_3DP/subcortical.nii \
             --match 2 3 24 31 41 42 63 72 77 51 52 13 12 43 50 4 11 26 58 49 10 17 18 53 54 44 5 80 14 15 30 62 \
             --inv \
             --o $filepath_3DP/bin.nii

fslmaths $filepath_3DP/subcortical.nii \
         -mul $filepath_3DP/bin.nii \
         $filepath_3DP/subcortical.nii.gz

cp $filepath_3DP/subcortical.nii.gz $filepath_3DP/subcortical_tmp.nii.gz

gunzip -f $filepath_3DP/subcortical_tmp.nii.gz

for i in 7 8 16 28 46 47 60 251 252 253 254 255
do
    mri_pretess $filepath_3DP/subcortical_tmp.nii \
    $i \
    $filepath_3DP/mri/norm.mgz \
    $filepath_3DP/subcortical_tmp.nii
done

fslmaths $filepath_3DP/subcortical_tmp.nii -bin $filepath_3DP/subcortical_bin.nii

mri_tessellate $filepath_3DP/subcortical_bin.nii.gz 1 $filepath_3DP/subcortical

mris_convert $filepath_3DP/subcortical $filepath_3DP/subcortical.stl

mri_convert --in_type mgz --out_type nii --out_orientation RAS $filepath_3DP/mri/rh.ribbon.mgz $filepath_3DP/rh_ribbon.nii.gz

mri_convert --in_type mgz --out_type nii --out_orientation RAS $filepath_3DP/mri/lh.ribbon.mgz $filepath_3DP/lh_ribbon.nii.gz

mris_convert $filepath_3DP/surf/rh.pial $filepath_3DP/rh_pial.stl

mris_convert $filepath_3DP/surf/lh.pial $filepath_3DP/lh_pial.stl

echo "subcortical.stl processing complete."

echo "Renaming output files."
cd $filepath_3DP
mv cortical.stl $PIDN"_cortical.stl"
mv subcortical.stl $PIDN"_subcortical.stl"
mv rh_pial.stl $PIDN"_rh_pial.stl"
mv lh_pial.stl $PIDN"_lh_pial.stl"
echo "Files renamed."

echo "All done with subject $PIDN! Happy printing :-)"

#optional return to 3D Printing directory:
cd /mnt/production/3D_Printing/
pwd
ls
