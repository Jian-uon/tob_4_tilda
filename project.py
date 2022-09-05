from tools import setup_logger
import argparse
import logging
from pathlib import Path
import toblerone as tob
import regtricks as rt
import numpy as np
import nibabel as nib
import os, ntpath
from nilearn import datasets

def project(fsdir, ref, output, src, surf, hemi, tf_mat, save_proj=True, load=True, projector=None):
    logger = logging.getLogger("Toberone")
    logger.info("Loading surfaces of reference image for {} {}.".format(surf, hemi))
    '''
    if hemi == 'left':
        hs='lh'
    elif hemi == 'right':
        hs='rh'
    else:
        logger.info("Hemisphere does not exists.")
    '''
    LWS = os.path.join(fsdir, 'surf', 'lh.white')
    LPS = os.path.join(fsdir, 'surf', 'lh.pial')
    RWS = os.path.join(fsdir, 'surf', 'rh.white')
    RPS = os.path.join(fsdir, 'surf', 'rh.pial')
    if hemi == 'left':
        raw_hemi = tob.Hemisphere(LWS, LPS, side='L')
    elif hemi == 'right':
        raw_hemi = tob.Hemisphere(RWS, RPS, side='R')
    else:
        logger.info("Hemisphere does not exist.")

    #projector = "{}_{}_projector.h5".format(surf, hemi)
    projector_path = projector

    t1_spc = rt.ImageSpace(ref)

    if load == True and projector != None and os.path.exists(projector_path):
        logger.info("Load local projectors {}".format(projector_path))
        proj = tob.Projector.load(projector_path)
    else:
        logger.info("Ccomputing projectors")
        proj = tob.Projector(raw_hemi, t1_spc)

    if  projector != None and os.path.exists(projector_path) and save_proj:
        out_path = os.path.join(output, "{}_{}_projector.h5".format(surf, hemi))
        proj.save(out_path)
        logger.info("Projectors saved.")
    
    if tf_mat != None:
        logger.info("Transforming asl image from native space to structural space.")
        asl2str_reg = rt.Registration.from_flirt(tf_mat, src=src, ref=ref)
        asl_in_t1 = asl2str_reg.apply_to_image(src, ref=ref).get_fdata()

        #asl_in_t1 = register_to_t1(src=src, ref=ref, tf_mat=tf_mat)
    else:
        logger.info("ASL image is regarded in the structural space.")
        #To do: specify native space for ASL image
        asl_in_t1 = nib.load(src).get_fdata()

    prefix = ntpath.basename(src).split('.')[0]
    print(proj)
    vol_on_surf = proj.vol2surf(vdata=asl_in_t1.flatten(), edge_scale=False)


    logger.info("Use fsaverage mesh to display metric files.")
    fsaverage = datasets.fetch_surf_fsaverage()
    surf = tob.Surface(fsaverage["{}_{}".format(surf, hemi)])
    surf.save_metric(vol_on_surf, os.path.join(output, prefix + "_surf_on_{}_{}.func.gii".format(surf, hemi)))
    logger.info("Metric file({} {}) on fsaverage saved.".format(surf, hemi))


    #surf_in_vol = proj.surf2vol(vol_on_surf, edge_scale=False)
    #spc.save_image(surf_in_vol, 'asl_surf_in_t1.nii.gz')

def register_to_t1(src, ref, tf_mat):
    asl2str_reg = rt.Registration.from_flirt(tf_mat, src=src, ref=ref)
    asl_in_t1 = asl2str_reg.apply_to_image(src, ref=ref).get_fdata()
    return asl_in_t1

def main(): 
    parser = argparse.ArgumentParser(
        description="This script performs toblerone to obtain PEVs from T1.")

    parser.add_argument(
        "--fs",
        help="Path to the FreeSurfer results.",
        required=True
    )

    parser.add_argument(
        "--ref",
        help="Path to the reference image.",
        required=True
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path to output.",
        required=True
    )

    parser.add_argument(
        "--src",
        help="Path to the asl image.",
        required=True
    )

    parser.add_argument(
        "--hemi",
        help="The hemisphere which the projection based on",
        required=False
    )

    parser.add_argument(
        "--surf",
        help="Projection for which surface(pial/white)",
        required=True
    )

    parser.add_argument(
        "--asl2str",
        help="Path to the transformation matrix from native space to structural space",
        required=False
    )

    parser.add_argument(
        "--projector",
        help="projector",
        required=False
    )

    parser.add_argument(
        "-v", "--verbose",
        help="If this option is provided, stdout will go to the terminal "
            +"as well as to a logfile. Default is False.",
        action="store_true"
    )

    args = parser.parse_args()
    fs_dir=args.fs#str(Path(args.fs).resolve(strict=True))
    ref=args.ref
    src=args.src
    asl2str=args.asl2str
    projector=args.projector
    output = args.output
    Path(output).mkdir(exist_ok=True)
    prefix = ntpath.basename(src).split('.')[0]
    surf = args.surf
    hemi = args.hemi
    logger = setup_logger("Toberone", os.path.join(output, prefix+'_tob_proj.log'), "INFO", args.verbose)
    logger.info(args)

    project(fsdir=fs_dir, ref=ref, output=output, src=src, tf_mat=asl2str, save_proj=True, load=True, surf=surf, hemi=hemi, projector = projector)

    pass



if __name__ == '__main__':
    main()