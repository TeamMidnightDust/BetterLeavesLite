import os
import zipfile
import shutil

def unpackMods():
    for root, dirs, files in os.walk("./input/mods"):
        for infile in files:
            if infile.endswith(".jar"):
                print("Unpacking mod: "+infile)
                zf = zipfile.ZipFile(os.path.join(root, infile), 'r')
                zf.extractall(os.path.join(root, infile.replace(".jar", "_temp")))
                zf.close()

def cleanupMods():
    if (os.path.exists("./input/mods")): shutil.rmtree("./input/mods")
    os.makedirs("./input/mods")

def scanModsForTextures():
    for root, dirs, files in os.walk("./input/mods"):
        for infile in files:
            if len(root.split("assets")) > 1:
                assetpath = root.split("assets")[1][1:]
                modid = assetpath.split("textures")[0].replace("/", "")
                if "textures/block" in root and infile.endswith(".png") and "leaves" in infile:
                    print(f"Found texture {assetpath}/{infile} in mod {modid}")
                    inputfolder = os.path.join("./input/assets/", assetpath)
                    os.makedirs(inputfolder, exist_ok=True)
                    shutil.copyfile(os.path.join(root, infile), os.path.join(inputfolder, infile))
