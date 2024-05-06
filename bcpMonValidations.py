import re
import os

def isValidDir(STRING_TO_CHECK):
    dir_pattern = r'^/[a-zA-Z0-9_/\\.-]*$'
    if re.match(dir_pattern, STRING_TO_CHECK):
        return True
    else:
        return False

def isValidIP(STRING_TO_CHECK):
    ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ip_pattern, STRING_TO_CHECK):
        return True
    else:
        return False

def isID(STRING_TO_CHECK):
    return STRING_TO_CHECK.isdigit()

def isDuplicateProject(projectName, projectList):
    if projectName not in projectList:
        print("Error: Please select a from the Project List")
        return False
    else:
        return True

def getABSPath():
    current_directory = os.getcwd()
    print("here")
    # Join the current directory path with the relative path of the file
    file_path = os.path.abspath(os.path.join(current_directory, "bcpMonValidations.py"))
    
    print("Absolute path of bcpMonValidations.py:", file_path)