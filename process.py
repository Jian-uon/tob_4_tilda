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
import subprocess

class Process(object):

    def __init(self):



        pass

    def main(self):
        parser = argparse.ArgumentParser(
            description="This script performs toblerone to obtain PEVs from T1.")

        parser.add_argument(
            "--input",
            help="Path to the T1 image.",
            required=True
        )

        parser.add_argument(
            "--subject",
            help="Path to the reference image.",
            #required=True
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
        args = parser.parse_args()
        t1=Path(args.fs).resolve(strict=True)
        sub_name=args.subject
        if sub_name is None:
            sub_name = 'BRC_T1'
        output_dir = Path(os.path.join(args.output, sub_name))
        output_dir.mkdir(exist_ok=True)
        output = str(output_dir)

        logger = setup_logger("TILDA", os.path.join(output, 't1.log'), "INFO", args.verbose)
        logger.info(args)
        pass


    def t1_process(self, t1, path):
        logger = logging.getLogger("T1_processsing")

        logger.info("Start to run T1 processing")    
        t1_process_call = [
            "struc_preproc.sh",
            "--input", t1,
            "--path", path,
            "--subject", "BRC_T1",
            "--subseg", 
            "--freesurfer"
        ]
        process = subprocess.Popen(t1_process_call, stdout=subprocess.PIPE, shell=True)
       
        while 1:
            retcode = process.poll()
            line = process.stdout.readline().decode("utf-8")
            logger.info(line)
            if line == "" and retcode is not None:
                break
        if retcode != 0:
            logger.info(f"retcode={retcode}")
            logger.exception("Process failed.")

        logger.info("T1 processing finished.")
        pass


    def fieldmap_process(self, fieldmaps_path, output, mag1, mag2, ph1, ph2):
        logger = logging.getLogger("fieldmap_processsing")
        logger.info("Start to run fieldmap processing") 

        if output is None:
            output = Path(os.path.join(fieldmaps_path, "fieldmaps"))
        output.mkdir(exist_ok=True)
        output = str(output)

        step1 = [
            "fslmaths",
            mag1, "-add 3.14", os.path.join(output, "fieldmap_magshift1.nii.gz")
        ]

        step2 = [
            "fslmaths",
            mag2, "-add 3.14", os.path.join(output, "fieldmap_magshift2.nii.gz")
        ]

        step3 = [
            "fslroi",
            os.path.join(output, "fieldmap_magshift2.nii.gz"), 
            os.path.join(output, "fieldmap_magshift2_expand.nii.gz"), 
            "0 80 0 80 -1 15"
        ]

        step3 = [
            "bet",
            os.path.join(output, "fieldmap_magshift2_expand.nii.gz"), 
            os.path.join(output, "fieldmap_mag_brain.nii.gz"),
            "-f 0.6"
        ]

        step4 = [
            "fslmaths",
            os.path.join(output, "fieldmap_mag_brain.nii.gz"),
            os.path.join(output, "fieldmap_mag_brain_mask.nii.gz"),

        ]

        step5 = [
            "fslmaths",
            os.path.join(output, "fieldmap_mag_brain_mask.nii.gz"),
            os.path.join(output, "fieldmap_mask_ero.nii.gz"),
        ]

        step6 = [
            "fslmaths",
            os.path.join(output, "fieldmap_mag_brain_mask.nii.gz"),
            os.path.join(output, "fieldmap_mask_ero.nii.gz"),
        ]


        
        process = subprocess.Popen(step1, stdout=subprocess.PIPE, shell=True)
       
        while 1:
            retcode = process.poll()
            line = process.stdout.readline().decode("utf-8")
            logger.info(line)
            if line == "" and retcode is not None:
                break
        if retcode != 0:
            logger.info(f"retcode={retcode}")
            logger.exception("Process failed.")

        logger.info("T1 processing finished.")
        pass


    def asl_process(self, asl, output, calib, t1, wm, gm, csf, brain, struct2std_warp, fmap, fmapmag, fmapmagbrain, ):
        logger = logging.getLogger("T1_processsing")

        logger.info("Start to run T1 processing")    
        t1_process_call = [
            "struc_preproc.sh",
            "--input", t1,
            "--path", path,
            "--subject", "BRC_T1",
            "--subseg", 
            "--freesurfer"
        ]
        process = subprocess.Popen(t1_process_call, stdout=subprocess.PIPE, shell=True)
       
        while 1:
            retcode = process.poll()
            line = process.stdout.readline().decode("utf-8")
            logger.info(line)
            if line == "" and retcode is not None:
                break
        if retcode != 0:
            logger.info(f"retcode={retcode}")
            logger.exception("Process failed.")

        logger.info("T1 processing finished.")
        pass




if __name__ == '__main__':
    main()
    pass
