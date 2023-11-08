#! /bin/sh
echo Enter PIDN:
read PIDN
PIDN_3DP=$PIDN"_3DP"

#temp filepath:
filepath="/mnt/production/3D_Printing/"$PIDN"/"

#echo "Enter working directory filepath (e.g. /mnt/production/test/):"
#read filepath
#filepath=$filepath"/"
filepath_3DP=$filepath$PIDN_3DP"/"

#temp T1_filename:
#T1_filename="T1_"$PIDN".nii"

#echo "Enter T1 filename found in the above directory (e.g. t1_mprage.nii):"
#read T1_filename

#echo "Running recon-all on $PIDN, output will be in: $filepath_3DP."

#recon-all -s $PIDN_3DP -i $filepath$T1_filename -sd $filepath -all
#echo "recon-all is complete for $PIDN"
cd $filepath_3DP
ls
cd surf/

echo "Combining lh.pial and rh.pial into cortical.stl"
mris_convert --combinesurfs $filepath_3DP/surf/lh.pial $filepath_3DP/surf/rh.pial $filepath_3DP/cortical.stl
echo "cortical.stl processing complete."


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

#optional copy the final files to another directory:
cp $PIDN"_cortical.stl" /rbogley/3D_Printing/FreeSurfer_Output/.
cp $PIDN"_subcortical.stl" /rbogley/3D_Printing/FreeSurfer_Output/.
cp $PIDN"_rh_pial.stl" /rbogley/3D_Printing/FreeSurfer_Output/.
cp $PIDN"_lh_pial.stl" /rbogley/3D_Printing/FreeSurfer_Output/.

#optional return to 3D Printing directory:
cd /mnt/production/3D_Printing/
pwd
ls
