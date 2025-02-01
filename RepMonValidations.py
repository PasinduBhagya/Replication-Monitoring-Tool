import re
from datetime import datetime

LogTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

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

def isValidProject(projectName, projectList):
    if projectName not in projectList:
        print(f"{LogTime} Error: Please select a from the Project List")
        return False
    else:
        return True

def isValidTime(STRING_TO_CHECK):
    timeRegExpress = r'^(?:[01]\d|2[0-3]):(?:[0-5]\d)$'
    if re.match(timeRegExpress, STRING_TO_CHECK):
        return True
    else:
        return False
    
def isValidServerID(STRING_TO_CHECK):
    # Check if it is in the Current Server ID list
    pass