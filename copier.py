import sys
import os
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("dirName", help="Name of directory to process")
parser.add_argument("-r", "--recursive",
                    help="Process subdirectories", action="count", default=0)
args = parser.parse_args()

DATEFIX_REGEX = re.compile(r": ")


def processDirectory(dirName):
    fileNames = os.listdir(dirName)
    count = 0
    for fileName in fileNames:
        if (fileName.startswith('.')):
            continue

        filePath = "{}/{}".format(dirName.rstrip('/'), fileName)
        if (os.path.isfile(filePath)):
            count += processFile(fileName, filePath, dirName)
        elif (os.path.isdir(filePath) and args.recursive):
            count += processDirectory(fileName)
    return count


def processFile(fileName, filePath, dirName):
    fileName = fileName.split(".")[0] + ".jpeg"
    os.system('cp -p "{}not_original/{}" "{}yes_exif/{}"'.format(
        dirName, fileName, dirName, fileName))
    return 1


if (len(sys.argv) > 1):
    dirName = args.dirName
    count = 0
    if (os.path.isfile(dirName)):
        count += processFile(dirName)
    else:
        count += processDirectory(dirName)

    print("Done processing {} files".format(count))
else:
    print("No files selected")
