# This has only  been test on Mac OS

import sys
import exifread
import os
import datetime
import argparse
import re
import subprocess
import json

parser = argparse.ArgumentParser()
parser.add_argument("dirName", help="Name of directory to process")
parser.add_argument("-r", "--recursive",
                    help="Process subdirectories", action="count", default=0)
args = parser.parse_args()

DATEFIX_REGEX = re.compile(r": ")

no_exif_files = []


def getExifCreated(fileName):
    try:
        f = open(fileName, 'rb')
        tags = exifread.process_file(f)
        tag = tags.get("EXIF DateTimeOriginal")
        if (tag):
            return re.sub(DATEFIX_REGEX, ':0', tags.get("EXIF DateTimeOriginal").values)
        else:
            return None
    except OSError:
        return None


def getExifTimeZone(fileName):
    try:
        f = open(fileName, 'rb')
        tags = exifread.process_file(f)
        tag = tags.get("EXIF Tag 0x9012")
        if (tag):
            return re.sub(DATEFIX_REGEX, ':0', tags.get("EXIF Tag 0x9012").values)
        else:
            return None
    except OSError:
        return None


def processDirectory(dirName):
    fileNames = os.listdir(dirName)
    count = 0
    for fileName in fileNames:
        if (fileName.startswith('.')):
            continue

        fileName = "{}/{}".format(dirName.rstrip('/'), fileName)
        if (os.path.isfile(fileName)):
            count += processFile(fileName)
        elif (os.path.isdir(fileName) and args.recursive):
            count += processDirectory(fileName)
    return count


def processFile(fileName):
    createdAt = getExifCreated(fileName)
    timeZone = getExifTimeZone(fileName)
    if (createdAt and createdAt != '0000:00:00 00:00:00'):
        if (timeZone != None):
            createdAt = datetime.datetime.strptime(
                createdAt+timeZone, '%Y:%m:%d %H:%M:%S%z')
            fileCreatedAt = datetime.datetime.fromtimestamp(
                os.stat(fileName).st_birthtime)

            if (createdAt != fileCreatedAt):
                os.system('exiftool -FileModifyDate="' +
                          createdAt.strftime('%Y:%m:%d %H:%M:%S%z') + '" "{}"'.format(fileName))
                print("Set created date to " +
                      createdAt.strftime('%Y:%m:%d %H:%M:%S%z') + timeZone + ": " + fileName)
                return 1
            else:
                print("Create dates match: {}".format(fileName))
                return 1
        else:
            createdAt = datetime.datetime.strptime(
                createdAt, '%Y:%m:%d %H:%M:%S')
            fileCreatedAt = datetime.datetime.fromtimestamp(
                os.stat(fileName).st_birthtime)

            if (createdAt != fileCreatedAt):
                os.system('exiftool -FileModifyDate="' +
                          createdAt.strftime('%Y:%m:%d %H:%M:%S%z') + '" "{}"'.format(fileName))
                print("Set created date to " +
                      createdAt.strftime('%Y:%m:%d %H:%M:%S%z') + ": " + fileName)
                return 1
            else:
                print("Create dates match: {}".format(fileName))
                return 1
    else:
        # No exifread compatibility for file
        # We're going to use exiftool command tool
        output = subprocess.check_output(
            'exiftool -json "{}"'.format(fileName), shell=True)
        exiftool_output = json.loads(output)
        fileCreatedAt = exiftool_output[0].get("FileModifyDate")
        if ("MediaCreateDate" in exiftool_output[0] and exiftool_output[0].get("MediaCreateDate") != '0000:00:00 00:00:00'):
            date = exiftool_output[0].get("MediaCreateDate")
        if ("CreationDate" in exiftool_output[0] and exiftool_output[0].get("CreationDate") != '0000:00:00 00:00:00'):
            date = exiftool_output[0].get("CreationDate")
        if ("DateTimeOriginal" in exiftool_output[0] and exiftool_output[0].get("DateTimeOriginal") != '0000:00:00 00:00:00'):
            date = exiftool_output[0].get("DateTimeOriginal")
        if ("MetadataDate" in exiftool_output[0] and exiftool_output[0].get("MetadataDate") != '0000:00:00 00:00:00'):
            date = exiftool_output[0].get("MetadataDate")
        if ("DateCreated" in exiftool_output[0] and exiftool_output[0].get("DateCreated") != '0000:00:00 00:00:00'):
            date = exiftool_output[0].get("DateCreated")
        if (date != None):
            if (date != fileCreatedAt):
                os.system('exiftool -FileModifyDate="' +
                          date + '" "{}"'.format(fileName))
                print("Set created date to " +
                      date + ": " + fileName)
            else:
                print("Create dates match: {}".format(fileName))
            return 1
        else:
            # No exif data available
            no_exif_files.append(fileName)
            return 0

    return 0


if (len(sys.argv) > 1):
    dirName = args.dirName
    count = 0
    if (os.path.isfile(dirName)):
        count += processFile(dirName)
    else:
        count += processDirectory(dirName)

    print("Done processing {} files".format(count))
    print(no_exif_files)
else:
    print("No files selected")
