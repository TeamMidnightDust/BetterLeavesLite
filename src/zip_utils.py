import os
import zipfile

# See https://stackoverflow.com/a/1855118
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))

# Creates a compressed zip file
def makeZip(filename, programmer_art=False):
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        zipdir('assets/', zipf)
        zipf.write('pack.mcmeta')
        zipf.write('pack_programmer_art.png', arcname='pack.png') if programmer_art else zipf.write('pack.png')
        zipf.write('LICENSE')
        zipf.write('README.md')
