#!/usr/bin/python3

import subprocess

browngh = subprocess.Popen(["python3", "browngh.py"])
eonline = subprocess.Popen(["python3", "eonline.py"])
myjoyonline = subprocess.Popen(["python3", "myjoyonline.py"])
peacefm = subprocess.Popen(["python3", "peacefm.py"])
ghanafa = subprocess.Popen(["python3", "ghanafa.py"])
newsghana = subprocess.Popen(["python3", "newsghana.py"])
newsapi = subprocess.Popen(["python3", "newsapi.py"])

# running the processes asynchronously
browngh.wait()
eonline.wait()
myjoyonline.wait()
peacefm.wait()
ghanafa.wait()
newsghana.wait()
newsapi.wait()