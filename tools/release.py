#!/usr/bin/python3

from pathlib import Path
import json
import os
import sys

try:
    from github import Github, GithubException
except ImportError:
    sys.exit("E: Please install pygithub package via pip")

try:
    from git import Repo
except ImportError:
    sys.exit("E: Please install gitpython package via pip")

home = str(Path.home())
token = str(open(home + "/.githubtoken", "r").read().strip())
g = Github(token)

ANDROID_BUILD_TOP = os.getenv("ANDROID_BUILD_TOP")
OUT = os.getenv("OUT")

try:
    zip = os.path.abspath(sys.argv[1])
    zipName = zip.split("/")[-1]

    if "tequila" not in zipName and ("-OFFICIAL" not in zipName or "-EXPERIMENTAL" not in zipName) and ".zip" not in zipName:
        sys.exit("E: Incorrect file!")

except IndexError:
    sys.exit("E: Incorrect file!")

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
    sys.exit("\nE: Can't find repo for " + codename) 

tag = date
title = "tequila-" + tag

try:
    release = repo.create_git_release(tag, title, "Automated release of " + zipName, prerelease=isExperimental)
    print("I: Uploading asset...")
    release.upload_asset(zip)
    print("I: Asset uploaded!")
except GithubException:
    sys.exit("E: Release already exists!")

print("Released " + title + "!")
print("https://github.com/tequilaOS/" + repo.name + "/releases/tag/" + tag)

if isExperimental:
    sys.exit("W: Release is experimental, OTA config and telegram message are not going to be created.")

def getProp(prop):
    props = open(OUT + "/system/build.prop", "r").read().splitlines()
    for line in props:
        if prop in line:
            return line.replace(prop + "=", "")

datetime = int(getProp("ro.build.date.utc"))
url = "https://github.com/tequilaOS/" + repo.name + "/releases/download/" + tag + "/" + zipName
checksum = open(zip + ".sha256sum", "r").read().split(" ")[0]
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

jsonFile = open(ANDROID_BUILD_TOP + "/tequila_ota/devices/" + codename + ".json", "w")
jsonFile.write(json.dumps(template, indent=2))
jsonFile.close()

ota_repo = Repo("tequila_ota")
ota_repo.git.add("devices/" + codename + ".json")
ota_repo.index.commit("ota: " + codename + "-" + date)
ota_repo.remote(name="tequila").push()
