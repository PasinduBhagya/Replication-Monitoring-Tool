import mysql.connector
import subprocess
from datetime import datetime
import os
import re

DATE_FOLDER = datetime.now().strftime("%Y-%m-%d")

def connectToDatabase():
    return mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana"
    )

def fetchFromDatabase(sql_query):
    database = connectToDatabase()
    dbcursor = database.cursor()
    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    database.close() 
    
    return output

def checkExtFileAvailability(extensions, username, serverIP, serverPath):
    exensionString = ""
    for extension in extensions.split(","):
        print(f"INFO: Looking for files with {extension} extension, on {serverIP} in {serverPath} path.")
        LINUX_COMMAND = f'''ssh {username}@{serverIP} -o ConnectTimeout=10  "cd {serverPath} && ls *.{extension}"'''
        try:
            COMMAND_OUTPUT = subprocess.check_output(LINUX_COMMAND, shell=True, stderr=subprocess.STDOUT)
            OUTPUT_AS_LIST = COMMAND_OUTPUT.decode('utf-8').split("\n")
            exensionString = exensionString + "*." + extension + " "
            
            return exensionString
        
        except subprocess.CalledProcessError as e:
            if e.returncode == 2:
                print(f"Warning: No files found with {extension} extension, on {serverIP} in {serverPath} path.")
            else:
                print(f"Error: Failed to execute the listing Command on {serverIP} server.")

        except subprocess.TimeoutExpired:
            print(f"Error: Connection to {serverIP} timed out. Please check your network connection and try again.")

def getLocalServerMD5Sum(localServerPath, extensions, localServerIP, localUsername, projectName):
    
    LOCAL_MD5SUM_HASH = {}
    if extensions == "Any":
        LINUX_COMMAND = f'''ssh {localUsername}@{localServerIP}  "cd {localServerPath} && md5sum *"'''
    else:
        exensionString = checkExtFileAvailability(extensions, localUsername, localServerIP, localServerPath)
        LINUX_COMMAND = f'''ssh {localUsername}@{localServerIP} -o ConnectTimeout=10  "cd {localServerPath} && md5sum {exensionString}"'''
        
    try:
        COMMAND_OUTPUT = subprocess.check_output(LINUX_COMMAND, shell=True, stderr=subprocess.STDOUT)

        print(f"INFO: Gathering MD5SUM - Project({projectName}) - IP({localServerIP}) - Path({localServerPath})")
                
        OUTPUT_AS_LIST = COMMAND_OUTPUT.decode('utf-8').split("\n")
        
        OUTPUT_AS_LIST = list(filter(bool, OUTPUT_AS_LIST))

        for resultLine in OUTPUT_AS_LIST:
            
            try:
                values = resultLine.split()
                key = values[1]
                value = values[0]
                # To check whether the return value is MD5sum
                md5_regex = r"^[a-fA-F0-9]{32}$"
                if bool(re.match(md5_regex, value)):
                    LOCAL_MD5SUM_HASH[key] = value

            except:
                print("Warning: Invalid output recived from the server: " + resultLine)

            
        
        return LOCAL_MD5SUM_HASH
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    
    except subprocess.TimeoutExpired:
            print(f"Error: Connection to {localServerIP} timed out. Please check your network connection and try again.")

def getBCPServerMD5Sum(bcpServerPath, extensions, BCPServerIP, BCPUsername, projectName):
    
    BCP_MD5SUM_HASH = {}
    if extensions == "Any":
        LINUX_COMMAND = f'''ssh {BCPUsername}@{BCPServerIP}  "cd {bcpServerPath} && md5sum *"'''
    else:
        exensionString = checkExtFileAvailability(extensions, BCPUsername, BCPServerIP, bcpServerPath)
        LINUX_COMMAND = f'''ssh {BCPUsername}@{BCPServerIP} -o ConnectTimeout=10  "cd {bcpServerPath} && md5sum {exensionString}"'''
            
    try:
        COMMAND_OUTPUT = subprocess.check_output(LINUX_COMMAND, shell=True, stderr=subprocess.STDOUT)

        print(f"INFO: Gathering - Project({projectName}) - IP({BCPServerIP}) - Path({bcpServerPath})")
                    
        OUTPUT_AS_LIST = COMMAND_OUTPUT.decode('utf-8').split("\n")
        
        OUTPUT_AS_LIST = list(filter(bool, OUTPUT_AS_LIST))

        for resultLine in OUTPUT_AS_LIST:
            
            try:
                values = resultLine.split()
                key = values[1]
                value = values[0]
                
                # To check whether the return value is MD5sum
                md5_regex = r"^[a-fA-F0-9]{32}$"
                if bool(re.match(md5_regex, value)):
                    BCP_MD5SUM_HASH[key] = value

            except:
                print("Warning: Invalid output recived from the server: " + resultLine)
        
        return BCP_MD5SUM_HASH
        
    except subprocess.CalledProcessError as e:
        print(f"Error: Information gathering command executing is failed {e}")
    
    except subprocess.TimeoutExpired:
            print(f"Error: Connection to {BCPServerIP} timed out. Please check your network connection and try again.")

def getRuleID():
    
    SYNC_STATUS = "Success"
    
    checkedRulesList = []

    if not os.path.isfile(f".cache/{DATE_FOLDER}_checkedRules"):
        with open(f".cache/{DATE_FOLDER}_checkedRules", 'a+') as cachedFile:
            pass

    with open(f".cache/{DATE_FOLDER}_checkedRules", 'r') as checkedRules:
        for checkedRule in checkedRules:
            checkedRulesList.append(int(checkedRule.strip()))
    
    sql_query = """ 
        select * from bcpSyncRules
    """
    rulesInfo = fetchFromDatabase(sql_query)
    
    for ruleInfo in rulesInfo:
        print("-"*90)
        print("INFO: Starting rule ID - " + str(ruleInfo[0]) + " " + str(ruleInfo[-1]))
        
        if int(ruleInfo[0]) in checkedRulesList:
            print(f"INFO: Skipping rule ID - {ruleInfo[0]}.")

        else:
            projectName = ruleInfo[1]
            # Creating a Blank Project File
            with open("DATA/" + DATE_FOLDER + "/" +  projectName, 'a') as projectFile:
                pass
            localServerPath = ruleInfo[2]
            bcpServerPath = ruleInfo[3]
            serversID = ruleInfo[4]
            extensions = ruleInfo[5]
            alias = ruleInfo[6]
            
            print("INFO: Servers ID - " + str(ruleInfo[4]))
            
            sql_query = f""" 
                select * from bcpServerDetails where serversID = "{serversID}"
            """
            serversInfo = fetchFromDatabase(sql_query)
            
            localServerIP = serversInfo[0][2]
            localUsername = serversInfo[0][3]
            BCPServerIP = serversInfo[0][4]
            BCPUsername = serversInfo[0][5]
            
            LOCAL_MD5SUM_HASH = getLocalServerMD5Sum(localServerPath, extensions, localServerIP, localUsername, projectName)
            BCP_MD5SUM_HASH = getBCPServerMD5Sum(bcpServerPath, extensions, BCPServerIP, BCPUsername, projectName)
            try:
                for key, value in LOCAL_MD5SUM_HASH.items():
                    if key in BCP_MD5SUM_HASH:
                        if value == BCP_MD5SUM_HASH[key]:
                            print(f"INFO: File {key} is same on the both servers.")
                        else:
                            print(f"Warning: File {key} is not same on the both servers.")
                            SYNC_STATUS = "Failed"        
                    else:
                        print(f"Warning: File {key} was not found in BCP Enviorment.")
                        SYNC_STATUS = "Failed"
                
                if not os.path.exists("DATA/" + DATE_FOLDER):
                    try:
                        os.makedirs("DATA/" + DATE_FOLDER)
                        print(f"INFO: {DATE_FOLDER} folder has been created successfully.")
                    except:
                        print("Error: Unable to create the DATA/" + DATE_FOLDER)
                    
                with open("DATA/" + DATE_FOLDER + "/" +  projectName, 'a') as projectFile:
                    projectFile.write(f"{alias},{SYNC_STATUS}\n")
                with open(f".cache/{DATE_FOLDER}_checkedRules", 'a') as checkedRules:
                    checkedRules.write(str(ruleInfo[0]) + "\n")
            except:
                print("Error: The server did not return data for given extensions.") 
            print("-"*90)    

        
def main():
    getRuleID()
    
if __name__ == "__main__":
    main()
