#!/usr/bin/python3

from pathlib import Path
import glob
import json
import os
import sys

try:
    from github import Github, GithubException
except ImportError:
    print("E: Please install pygithub package via pip")
    sys.exit(1)

try:
    from git import Repo
except ImportError:
    print("E: Please install gitpython package via pip")
    sys.exit(1)

home = str(Path.home())
with open(home + "/.githubtoken", "r") as f:
    token = str(f.read().strip())
g = Github(token)

ANDROID_BUILD_TOP = os.getenv("ANDROID_BUILD_TOP")
OUT = os.getenv("OUT")

GERRIT_USERNAME = os.getenv("GERRIT_USERNAME")

if not GERRIT_USERNAME:
    GERRIT_USERNAME = os.getenv("USER")

try:
    zip = os.path.abspath(sys.argv[1])
    zipName = zip.split("/")[-1]

    if "tequila" not in zipName and ("-OFFICIAL" not in zipName or "-EXPERIMENTAL" not in zipName) and ".zip" not in zipName:
        print("E: Incorrect file!")
        sys.exit(1)

except IndexError:
    print("E: Incorrect file!")
    sys.exit(1)

codename = zipName.split("-")[5].replace(".zip", "")
date = (zipName.split("-")[2] + "-" + zipName.split("-")[3]).split(".")[0]

if zipName.split("-")[4] == "EXPERIMENTAL":
    isExperimental = True
else:
    isExperimental = False

print("I: Releasing " + date + " build for " + codename)

repo = None
repos = g.get_organization("tequilaOS").get_repos()
for r in repos:  
    if codename in r.name and "platform_device_" in r.name:
        repo = r
        print("I: Repo found for your device: " + repo.name)
        break

if not repo:
    print("\nE: Can't find repo for " + codename) 
    sys.exit(1)

tag = date
title = zipName.split("-")[1] + "-" + tag

additional_files = [
    "recovery",
    "boot",
    "dtbo",
    "vendor_boot"
]

additional_files_path = OUT + "/obj/PACKAGING/target_files_intermediates/tequila_" + codename + "*/IMAGES/"

try:
    release = repo.create_git_release(tag, title, "Automated release of " + zipName, prerelease=isExperimental)
    print("I: Uploading build...")
    release.upload_asset(zip)
    for file_name in additional_files:
        try:
            file = glob.glob(additional_files_path + file_name + ".img")[0]
            print("I: Uploading " + file_name + "...")
            release.upload_asset(file)
        except IndexError:
            pass
    print("I: Assets uploaded!")
except GithubException as error:
    print("E: Failed creating release: " + error.data['errors'][0]['code'])
    sys.exit(1)

print("Released " + title + "!")
print("https://github.com/tequilaOS/" + repo.name + "/releases/tag/" + tag)

if isExperimental:
    print("W: Release is experimental, skipping OTA config generation!")
    sys.exit(0)

def getProp(prop):
    with open(OUT + "/system/build.prop", "r") as props:
        for line in props.read().splitlines():
            if prop in line:
                return line.replace(prop + "=", "")

datetime = int(getProp("ro.build.date.utc"))
url = "https://github.com/tequilaOS/" + repo.name + "/releases/download/" + tag + "/" + zipName
with open(zip + ".sha256sum", "r") as f:
    checksum = f.read().split(" ")[0]
filesize = os.path.getsize(zip)
version = zipName.split("-")[1]

template = {
  "response": [
    {
      "datetime": datetime,
      "filename": zipName,
      "id": checksum,
      "size": filesize,
      "url": url,
      "version": version
    }
  ]
}

with open(ANDROID_BUILD_TOP + "/tequila_ota/devices/" + codename + ".json", "w") as jsonFile:
    jsonFile.write(json.dumps(template, indent=2))

ota_repo = Repo(ANDROID_BUILD_TOP + "/tequila_ota")
ota_repo.git.add("devices/" + codename + ".json")
sha = ota_repo.index.commit("ota: " + codename + "-" + date + "\n")
ota_repo.git.push("ssh://" + GERRIT_USERNAME + "@review.tequilaos.org:29418/tequilaOS/tequila_ota", str(sha) + ":refs/for/main")
