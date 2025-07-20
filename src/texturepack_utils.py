import os
import zipfile
import shutil
from src.utilities import printCyan

def unpackTexturepacks(rootFolder="./input/texturepacks"):
    for root, dirs, files in os.walk(rootFolder):
        for infile in files:
            if infile.endswith(".zip"):
                print("Unpacking texturepack: "+infile)
                zf = zipfile.ZipFile(os.path.join(root, infile), 'r')
                zf.extractall(os.path.join(root, infile.replace(".zip", "_temp")))
                zf.close()

def cleanupTexturepacks(rootFolder="./input/texturepacks"):
    for root, dirs, files in os.walk(rootFolder):
        for folder in dirs:
            if folder.endswith("_temp"):
                shutil.rmtree(os.path.join(root, folder))

def scanPacksForTexture(baseRoot, baseInfile, rootFolder="./input/texturepacks"):
    for root, dirs, files in os.walk(rootFolder):
        for infile in files:
            if "assets" in root and "assets" in baseRoot:
                if infile.endswith(".png") and (len(root.split("/")) > 3) and (baseInfile == infile) and (root.split("assets")[1] == baseRoot.split("assets")[1]):
                    printCyan(" Using texture from: " + root.split("assets")[0].replace(rootFolder, ""))
                    return root;
    return baseRoot
