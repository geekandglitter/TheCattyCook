import os, shutil, glob

SOURCE_DIR = '/home/runner/.site-packages'
DEST_DIR = '/home/runner/.local/lib/python3.6/site-packages'

def move_site_packages():
    if not os.path.isdir(DEST_DIR):
        os.makedirs(DEST_DIR)

    for filePath in glob.glob(SOURCE_DIR + '/*'):
        file_name = filePath.split('/')[-1]
        if not os.path.exists(DEST_DIR + '/' + file_name):
            print(filePath)
            shutil.move(filePath, DEST_DIR)