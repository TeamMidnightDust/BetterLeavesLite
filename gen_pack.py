#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script can automatically generate blockstate and block model files, as well as textures for the Better Leaves Lite resourcepack."""

# Depencency imports
import argparse
import json
import time

# Local imports
from src.generator import autoGen
from src.download_helper import downloadPack
from src.zip_utils import makeZip
import src.json_utils

def writeMetadata(args):
    edition = args.edition
    if isinstance(edition, list): edition = " ".join(args.edition)
    with open("./input/pack.mcmeta") as infile, open("pack.mcmeta", "w") as outfile:
        for line in infile:
            line = line.replace("${version}", args.version).replace("${edition}", edition).replace("${year}", str(time.localtime().tm_year))
            outfile.write(line)

# This is the main entry point, executed when the script is run
if __name__ == '__main__':
    start_time = time.perf_counter()
    parser = argparse.ArgumentParser(
                    description='This script can automatically generate files for the Better Leaves Lite resourcepack.',
                    epilog='Feel free to ask for help at http://discord.midnightdust.eu/')

    parser.add_argument('version', type=str)
    parser.add_argument('edition', nargs="*", type=str, default="§cCustom Edition", help="Define your edition name")
    parser.add_argument('--legacy', '-l', action='store_true', help="Use legacy models (from 8.1) for all leaves")
    parser.add_argument('--programmer', '-p', action='store_true', help="Use programmer art textures")
    parser.add_argument('--minify', '-m', action='store_true', help="Minify all JSON output files")
    parser.add_argument('--download', '-d', help="Downloads the requested resourcepack beforehand")
    args = parser.parse_args()

    print(f"Arguments: {args}")
    print()
    print("Motschen's Better Leaves Lite")
    print("https://github.com/TeamMidnightDust/BetterLeavesLite")
    print()
    if args.minify: src.json_utils.minify = True
    if args.download != None: downloadPack(args.download)

    # Loads overrides from the json file
    f = open('./input/overrides.json')
    data = json.load(f)
    f.close()

    autoGen(data, args);
    writeMetadata(args)
    print()
    print("Zipping it up...")
    makeZip(f"Better-Leaves-{args.version}.zip" if not args.programmer else f"Better-Leaves-(Programmer-Art)-{args.version}.zip", args.programmer);
    print("Done!")
    print("--- Finished in %s seconds ---" % (round((time.perf_counter() - start_time)*1000)/1000))
