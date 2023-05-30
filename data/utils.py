import requests
import os
import sys

def getRequest(url):
    return requests.get(url, allow_redirects=True)

def saveCSVLocally(path,url):
    try:
        r = getRequest(url)
        content = r.content
    except:
        content = bytes("Could not fetch data","utf-8")
    open(path,"wb").write(content)

def removeOldDBIfExists(sql_path, requires_confirmation=True):
    if os.path.exists(sql_path):
        if requires_confirmation:
            confirmation = input("Are you sure you want to delete the old database? (no backup will be made) \n(y/n): ")
        else: 
            confirmation = "y" # if no confirmation required, automatically deletes old db
            
        if confirmation.lower() == "y":
            os.remove(sql_path)
            print("old database deleted successfully.")
        else:
            print("Deletion cancelled. Not fetching new data")
            sys.exit()
    else:
        print("Database does not exist. Fetching new one...")