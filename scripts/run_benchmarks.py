#!/usr/bin/env python3

import os, sys, signal
import json
import subprocess
from optparse import OptionParser
from functools import partial
from multiprocessing.dummy import Pool
from time import time

parser = OptionParser()
parser.add_option("--runall", dest="runall", action="store_true",
                help="Run all experiments listed in Evaluation, default: %default",
                default=False)
parser.add_option("-t", "--type", dest="type", action="append", choices=["fuse", "parallel"],
                help="Type of trasformation to verify, specify 'fuse' for fusion, specify 'parallel' for parallelization"
                ", if omitted, all would be run",
                default=[])
parser.add_option("-c", "--case", dest="case", action="append", choices=["size_counting", "css", "cycletree", "list"],
                help="Case to verify, , could be repeated to specify multiple"
                ", specify 'size_counting', 'css', 'cycletree' or 'list' for fusibility verification"
                ", specify 'size_counting' or 'cycletree' for parallelizability verification"
                ", if omitted, all would be run",
                default=[])
parser.add_option("--retreet_entrypoint", dest="retreet",
                help="Entrypoint to Retreet run script, default: %default",
                default="/home/user/Retreet/exec.sh")
parser.add_option("--mona_entrypoint", dest="mona",
                help="Entrypoint to MONA, default: %default",
                default="/usr/local/bin/mona")
parser.add_option("-B", "--case_study_base", dest="case_study_base",
                help="Case study base directory path, default: %default",
                default="/home/user/Retreet/case_study")
parser.add_option("-O", "--output_base", dest="output_base",
                help="Generated MONA files base directory path, default: %default",
                default="/home/user/Retreet/output")

(options, args) = parser.parse_args()
if options.type == []:
    options.type = ["fuse", "parallel"]
if options.case == []:
    options.case = ["size_counting", "css", "cycletree", "list"]
if options.runall:
    options.type = ["fuse", "parallel"]
    options.case = ["size_counting", "css", "cycletree", "list"]

def run_subprocess(args, printout=False, trans_type="fuse"):
    result = subprocess.Popen(args, start_new_session=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if printout:
        stdout, stderr = result.communicate()
        stdout = stdout.decode('UTF-8').splitlines()
        stdout = [s.strip() for s in stdout]
        # print(stdout)
        # print("retcode =", result.returncode)
        if result.returncode == -9:
            print("Out of memory")
        process_mona_output(stdout, trans_type)
        # if stderr:
        #     print(stderr)
        #     stderr = stderr.decode('UTF-8').splitlines()
        #     stderr = [s.strip() for s in stderr]
        #     for line in stderr:
        #         print(line)
        #     print()

def process_mona_output(stdout, trans_type="fuse"):
    collect = []
    print_whole_analysis = False
    for i in range(len(stdout)):            
        if not print_whole_analysis:
            if "ANALYSIS" in stdout[i]:
                collect.append(stdout[i])
                if "satisfiable" not in stdout[i + 1]:
                    print_whole_analysis = True
                    if trans_type == "fuse":
                        collect.append("Result: NOT Fusible")
                    elif trans_type == "parallel":
                        collect.append("Result: NOT Parallelizable")
            if "unsatisfiable" in stdout[i]:
                if trans_type == "fuse":
                    collect.append("Result: Fusible")
                elif trans_type == "parallel":
                    collect.append("Result: Parallelizable")
                else:
                    collect.append(stdout[i])
            if "Total time" in stdout[i]:
                collect.append(stdout[i])
        else:
            collect.append(stdout[i])
    for line in collect:
        print(line)
    print()

def run_benchmark(trans_type, case_study):
    prefix = options.case_study_base
    output = options.output_base + "/"
    if trans_type == "fuse":
        if case_study == "size_counting":
            prefix += "/size_counting/"
            # fusible
            args = [options.retreet, "fuse", prefix+"size_counting_fusible.retreet", prefix+"fusible_size_counting_fused.retreet", prefix+"fusible_size_counting_relation.retreet"]
            print("Checking fusibility of fusible size_counting traversals.")
            run_subprocess(args)
            args = [options.mona, output+"fuse_size_counting_fusible.mona"]
            run_subprocess(args, True)
            # infusible
            args = [options.retreet, "fuse", prefix+"size_counting_infusible.retreet", prefix+"infusible_size_counting_fused.retreet", prefix+"infusible_size_counting_relation.retreet"]
            print("Checking fusibility of infusible size_counting traversals.")
            run_subprocess(args)
            args = [options.mona, output+"fuse_size_counting_infusible.mona"]
            run_subprocess(args, True)
        elif case_study == "css":
            prefix += "/css/"
            args = [options.retreet, "fuse", prefix+"css.retreet", prefix+"fusible_css_fused.retreet", prefix+"fusible_css_relation.retreet"]
            print("Checking fusibility of fusible CSS minification traversals.")
            run_subprocess(args)
            args = [options.mona, output+"fuse_css.mona"]
            run_subprocess(args, True)
        elif case_study == "cycletree":
            prefix += "/cycletree/"
            args = [options.retreet, "fuse", prefix+"cycletree.retreet", prefix+"fusible_cycletree_fused.retreet", prefix+"fusible_cycletree_relation.retreet"]
            print("Checking fusibility of fusible cycletree traversals.")
            run_subprocess(args)
            print("Problem broken down into 5 MONA queries.")
            args = [options.mona, output+"fuse_cycletree_1.mona"]
            run_subprocess(args, True)
            args = [options.mona, output+"fuse_cycletree_2.mona"]
            run_subprocess(args, True)
            args = [options.mona, output+"fuse_cycletree_3.mona"]
            run_subprocess(args, True)
            args = [options.mona, output+"fuse_cycletree_4.mona"]
            run_subprocess(args, True)
            args = [options.mona, output+"fuse_cycletree_5.mona"]
            run_subprocess(args, True)
        elif case_study == "list":
            prefix += "/shiftsum/"
            args = [options.retreet, "fuse", prefix+"shiftsum_fusible.retreet", prefix+"fusible_shiftsum_fused.retreet", prefix+"fusible_shiftsum_relation.retreet"]
            print("Checking fusibility of fusible list_sum and list_shift traversals.")
            run_subprocess(args)
            args = [options.mona, output+"fuse_shiftsum_fusible.mona"]
            run_subprocess(args, True)
    else:
        if case_study == "size_counting":
            prefix += "/size_counting/"
            args = [options.retreet, "parallel", prefix+"size_counting_parallel.retreet"]
            print("Checking parallelizability of fusible size_counting traversals.")
            run_subprocess(args)
            args = [options.mona, output+"size_counting_parallel.mona"]
            run_subprocess(args, True, trans_type)
        elif case_study == "cycletree":
            prefix += "/cycletree/"
            args = [options.retreet, "parallel", prefix+"cycletree_parallel.retreet"]
            print("Checking parallelizability of fusible cycletree traversals.")
            run_subprocess(args)
            args = [options.mona, output+"cycletree_parallel.mona"]
            run_subprocess(args, True, trans_type)
            


def run_benchmarks():
    for trans_type in options.type:
        for case_study in options.case:
            run_benchmark(trans_type, case_study)

def main():
    run_benchmarks()

if __name__ == "__main__":
    main()
