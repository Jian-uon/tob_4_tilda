from tools import setup_logger
import argparse
import logging
from pathlib import Path
import toblerone as tob
import regtricks as rt
import numpy as np
import nibabel as nib
import os, ntpath


def project(fsdir, ref, output, src, tf_mat=None, save_proj=True, load=False):
    logger = logging.getLogger("Toberone")
    logger.info("Loading surfaces of reference image for both left and right Hemisphere(pial and white).")
    LWS = os.path.join(fsdir, 'surf/lh.white')
    LPS = os.path.join(fsdir, 'surf/lh.pial')
    RWS = os.path.join(fsdir, 'surf/rh.white')
    RPS = os.path.join(fsdir, 'surf/rh.pial')
    lhemi = tob.Hemisphere(LWS, LPS, side='L')
    rhemi = tob.Hemisphere(RWS, RPS, side='R')

    spc = rt.ImageSpace(ref)

    lprojector_path = os.path.join(output, 'lprojector.h5')
    rprojector_path = os.path.join(output, 'rprojector.h5')

    if load == True and os.path.exists(rprojector_path) and os.path.exists(lprojector_path):
        logger.info("Load local projectors")
        lproj = tob.Projector.load(lprojector_path)
        rproj = tob.Projector.load(rprojector_path)
    else:
        logger.info("Ccomputing projectors")
        lproj = tob.Projector(lhemi, spc)
        rproj = tob.Projector(rhemi, spc)

    if save_proj:
        lproj.save(os.path.join(output, 'lprojector.h5'))
        rproj.save(os.path.join(output, 'rprojector.h5'))
        logger.info("Projectos saved.")

    if tf_mat != None:
        logger.info("Transforming asl image from native space to structural space.")
        asl_in_t1 = register(src=src, ref=ref, tf_mat=asl2struct)
    else:
        logger.info("ASL image is regarded in the structural space.")
        asl_in_t1 = nib.load(src).get_fdata()

    prefix = ntpath.basename(src).split('.')[0]

    lvol_on_surf = lproj.vol2surf(asl_in_t1.flatten(), edge_scale=False)
    rvol_on_surf = rproj.vol2surf(asl_in_t1.flatten(), edge_scale=False)
    logger.info("Use WM surface to display metric files.")
    lsurf = tob.Surface(LWS)
    rsurf = tob.Surface(RWS)
    lsurf.save_metric(lvol_on_surf, os.path.join(output, prefix + '_surf_on_lws.func.gii'))
    rsurf.save_metric(rvol_on_surf, os.path.join(output, prefix + '_surf_on_rws.func.gii'))
    logger.info("Metric files saved.")


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
        "--asl2str",
        help="Path to the transformation matrix from native space to structural space",
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
    output = args.output
    Path(output).mkdir(exist_ok=True)
    prefix = ntpath.basename(src).split('.')[0]

    logger = setup_logger("Toberone", os.path.join(output, prefix+'_tob_proj.log'), "INFO", args.verbose)
    logger.info(args)
    project(fsdir=fs_dir, ref=ref, output=output, src=src, tf_mat=asl2str, save_proj=True, load=False)

    pass



if __name__ == '__main__':
    main()