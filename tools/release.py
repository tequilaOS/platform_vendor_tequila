#!/usr/bin/python3

from pathlib import Path
import json
import os
import sys

from jinja2 import Undefined

try:
    from github import Github, GithubException
except ImportError:
    sys.exit("Please install pygithub package via pip")

try:
    from git import Repo
except ImportError:
    sys.exit("Please install gitpython package via pip")

try:
    import telegram_send
except ImportError:
    sys.exit("Please install telegram-send package via pip")

home = str(Path.home())
token = str(open(home + "/.githubtoken", "r").read().strip())
g = Github(token)

ANDROID_BUILD_TOP = os.getenv("ANDROID_BUILD_TOP")
OUT = os.getenv("OUT")

try:
    zip = os.path.abspath(sys.argv[1])
    zipName = zip.split("/")[-1]

    if "tequila" not in zipName or "-OFFICIAL" not in zipName or "-EXPERIMENTAL" not in zipName or ".zip" not in zipName:
        sys.exit("Incorrect file!")

except IndexError:
    sys.exit("Incorrect file!")

codename = zipName.split("-")[5].replace(".zip", "")
date = (zipName.split("-")[2] + "-" + zipName.split("-")[3]).split(".")[0]

if zipName.split("-")[4] == "EXPERIMENTAL":
    isExperimental = True
else:
    isExperimental = False

print("Releasing " + date + " build for " + codename)

repo = None
repos = g.get_organization("tequilaOS").get_repos()
for r in repos:  
    if codename in r.name and "device_" in r.name:
        repo = r
        print("Repo found for your device: " + repo.name)
        break

if not repo:
    sys.exit("\nERROR: Can't find repo for " + codename) 

tag = date
title = "tequila-" + tag

try:
    release = repo.create_git_release(tag, title, "Automated release of " + zipName, prerelease=isExperimental)
    print("Uploading asset...")
    release.upload_asset(zip)
    print("Asset uploaded!")
except GithubException:
    sys.exit("Release already exists!")

props = open(OUT + "/system/build.prop", "r").read().splitlines()
for line in props:
    if "ro.build.date.utc" in line:
        datetime = int(line.replace("ro.build.date.utc=", ""))

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

repo = Repo("tequila_ota")
repo.git.add("devices/" + codename + ".json")
repo.index.commit("ota: " + codename + "-" + date)
repo.remote(name="tequila").push()

print("Released " + title + "!")

date = zipName.split("-")[2]
date = date[0:4] + "/" + date[4:6] + "/" + date[6:8]

message = (
    f"<b>tequilaOS | 12.1</b>\n"
    f"<b>Device:</b> {codename}\n"
    f"<b>Date:</b> {date}\n"
    f"\n"
    f"<a href='https://tequilaOS.pl/download?device={codename}'>Download</a>\n"
    f"\n"
    f"@tequilaOS | @tequilaOSChat"
)

telegram_send.send(conf="~/.config/tequilatg.conf", parse_mode="html", messages=[message])
