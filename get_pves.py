from tools  import setup_logger
import argparse
import logging
from pathlib import Path
import toblerone as tob
from toblerone.classes import CommonParser, ImageSpace, Surface
import regtricks as rt
import numpy as np
import nibabel as nib
import os

def get_PVEs(fsdir, ref, out_dir):
    PVEs = tob.pvestimation.cortex(fsdir=fsdir, ref=ref, struct2ref='I')
    tis_names = ['gm', 'wm', 'nonbrain']
    refSpace = ImageSpace(ref)
    for idx in range(3):
        refSpace.save_image(PVEs[:,:,:,idx], os.path.join(out_dir, f'pve_{tis_names[idx]}.nii.gz'))


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
        "-v", "--verbose",
        help="If this option is provided, stdout will go to the terminal "
            +"as well as to a logfile. Default is False.",
        action="store_true"
    )
    '''
        parser.add_argument(
            "--asl2struct",
            help="Path to the matrix from native space to structural space.",
            required=True
        )
    '''
    args = parser.parse_args()
    fs_dir=Path(args.fs).resolve(strict=True)
    ref=str(Path(args.ref).resolve(strict=True))
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    output=str(output_dir)

    logger = setup_logger("Toberone", os.path.join(output, 'tob.log'), "INFO", args.verbose)
    logger.info(args)

    get_PVEs(fsdir=fs_dir, ref=ref, out_dir=output)

    pass



if __name__ == '__main__':
    main()