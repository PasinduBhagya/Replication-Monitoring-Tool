#!/usr/local/bin/python3.8
import sys
import subprocess
import mysql.connector
import os

from tabulate import tabulate
from bcpMonFileCompare import main as fileComparison
from configparser import ConfigParser
from bcpMonValidations import isValidDir, isValidIP, isID, isDuplicateProject, isValidTime

config = ConfigParser()
baseDIR = os.path.dirname(os.path.realpath(os.path.dirname(__file__) + "/bcpsyn"))
config.read(baseDIR + "/.env")

jira_username = config.get('DATABASE', 'HOST')

def main(arguments):
    if len(arguments) == 1:
        print("Error: To few arguments. Unable to execute. Use --help flag to see arguments.")
        exit()
  
    if "--help" in arguments:
        print('''Usage: This tool can be used to add, remove, and read bcp sync related rules to the application. 

    Options and arguments.

        --help\t: Print this help message and exit.
          
        --list-projects\t: List all available projects along with their details
        --list-rules\t: Display a comprehensive list of rules associated with the projects
        --list-servers\t: Show all registered Local BCP server pairs
                 
        --add-rule\t: Add a new rule to specify synchronization criteria
        --add-new-server\t: Register a new Local BCP server pair
          
        --remove-rule-with-id\t: Remove a specific rule identified by its unique ID   
        --remove-server\t: Delete a Local BCP server pair (will remove all Rules associated with that pair)
        
        --run-rules\t: To manualy run the rules
        --show-logs\t: To be code     
    
    If you need any other support, please contact Pasindu Bhagya - https://github.com/PasinduBhagya/BCP-Grafana
    ''')
        exit()

    if any(element not in ["--help", 
                           "--list-projects", 
                           "--list-rules", 
                           "--list-servers", 
                           "--add-rule", 
                           "--add-new-server", 
                           "--remove-rule-with-id", 
                           "--remove-server",
                           "--show-logs",
                           "--run-rules"] for element in arguments[1:]):
        print('''\nError: Invalid arguments provided.\n''')
        exit()
        
    print("-"*30)
    if arguments[1:2][0] == "--list-projects":
        print("INFO: Listing Projects:")
        print("-"*30)
        listProjects()
        print("-"*30)

    elif arguments[1:2][0] == "--list-rules":
        print("INFO: Listing all Rules")
        listRules()
       
    elif arguments[1:2][0] == "--list-servers":
        print("INFO: Listing all Servers")
        listServers()
        
    elif arguments[1:2][0] == "--add-rule":
        addRules()
        
    elif arguments[1:2][0] == "--add-new-server":
        addNewServer()
        
    elif arguments[1:2][0] == "--remove-rule-with-id":
        removeRuleID()
        
    elif arguments[1:2][0] == "--remove-server":
        removServer()
        
    elif arguments[1:2][0] == "--show-logs":
        print("--show-logs")

    elif arguments[1:2][0] == "--run-rules":
        print("INFO: This will execute the on all rules. Do you wish to continue? [Yes]")
        confirmation = input("")
        if confirmation != "Yes":
            print("INFO: Exiting.")
            exit(0)
        else:
            fileComparison()
        
def connectToDatabase():
    return mysql.connector.connect(
        host=config.get('DATABASE', 'HOST'),
        user=config.get('DATABASE', 'USER'),
        password=config.get('DATABASE', 'PASSWORD'),
        database=config.get('DATABASE', 'DATABASE'),
    )

def fetchFromDatabase(sql_query):
    database = connectToDatabase()
    dbcursor = database.cursor()
    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    database.close() 
    
    return output

def listProjects():

    projectList = []

    sql_query = """ 
        select DISTINCT projectName from bcpServerDetails
    """
    try: 
        output = fetchFromDatabase(sql_query)
    
        for row in output:
            projectList.append(row[0])
    except:
        print("Error: Failed to Fetch Data from the database")
        exit()
    
    return projectList

def listRules():
    sql_query = """ 
        select * from bcpSyncRules
    """
    try:
        output = fetchFromDatabase(sql_query)
        data_as_list = [list(item) for item in output]
        headers = ["ID", "Project Name", "Local Server Path", "BCP Server Path", "serversID", "Extensions", "Alias"]
        print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
    except:
        print("Error: Failed to Fetch Data from the database")

def listServers():
    sql_query = """ 
        select * from bcpServerDetails
    """
    try:
        output = fetchFromDatabase(sql_query)
        
        data_as_list = [list(item) for item in output]
        headers = ["Servers ID", "Project Name", "Local Server IP", "Local Server Username", "BCP Server IP", "BCP Server Username", "Alias"]
        print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
        
    except:
        print("Error: Failed to Fetch Data from the database")

# Need validation here 
def addRules():
    database = connectToDatabase()
    dbcursor = database.cursor()
    
    print("INFO: Provide below Information for the Rule.")
    print("-"*80)
    print(listProjects())
    print("-"*80)
    while True:
        projectName = input("Project Name:\t")
        projectList = listProjects()
        if isDuplicateProject(projectName, projectList):
            if inputValidation(projectName, FIELD_NAME="Project Name", inputType="None"):
                break
            else:
                print("Error: Please select a from the Project List")
    
    while True:
        localServerPath = input("Local Server Path:\t")
        if inputValidation(localServerPath, FIELD_NAME="Local Server Path", inputType="Dir"):
            break
    
    while True:
        bcpServerPath = input("BCP Server Path:\t")
        if inputValidation(bcpServerPath, FIELD_NAME="BCP Server Path", inputType="Dir"):
            break
    
    sql_query = f""" 
        select serversID, projectName, alias from bcpServerDetails where projectName = "{projectName}"
    """
    try: 
        dbcursor.execute(sql_query)
        output = dbcursor.fetchall()

        data_as_list = [list(item) for item in output]
        headers = ["ID", "Project Name", "Alias"]
        print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
    
        while True:
            serversID = input("Select Servers ID from above list:\t")
            if inputValidation(serversID, FIELD_NAME="Server ID", inputType="ID"):
                break
        
        extensions = input("Extensions Name: [Optional]\t")
        
        if extensions == "":
            extensions = "Any"
        
        while True:
            scheduledTime = input("Executing Time [In 24 hour Format]:\t")
            if inputValidation(scheduledTime, FIELD_NAME="Executing Time", inputType="Time"):
                break
        
        while True:
            alias = input("Alias:\t")
            if inputValidation(alias, FIELD_NAME="Alias", inputType="None"):
                break
        
        sql_query = """INSERT INTO bcpSyncRules (projectName, localServerPath, bcpServerPath, serversID, extensions, scheduledTime, alias) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (projectName, localServerPath, bcpServerPath, serversID, extensions, scheduledTime, alias)

        dbcursor.execute(sql_query, values)
        database.commit()

        sql_query = f""" 
            select * from bcpSyncRules where projectName = "{projectName}" AND localServerPath = "{localServerPath}" AND bcpServerPath = "{bcpServerPath}" AND alias = "{alias}"
        """
        dbcursor.execute(sql_query)
        output = dbcursor.fetchall()

        data_as_list = [list(item) for item in output]
        headers = ["ID", "Project Name", "Local Server Path", "BCP Server Path", "serversID", "Extensions", "Alias"]
        print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
        print("INFO: Rule added successfully.")

    except Exception as e:
        print("Error: Adding new record is failed" + e)

# Need validation here   
def removeRuleID():
    listRules()
    database = connectToDatabase()
    dbcursor = database.cursor()
    
    ruleID = input("Rule ID to remove:\t")
    sql_query = f""" 
        DELETE FROM bcpSyncRules WHERE ruleID = '{ruleID}';
    """
    try:
        dbcursor.execute(sql_query)
        database.commit()
        dbcursor.close()
        database.close()
        print("INFO: Rule has been removed successfully.")
    except:
        print("Error: Failed to remove Data from the database")    

# Need validation here    
def addNewServer():
    database = connectToDatabase()
    dbcursor = database.cursor()

    with open(config.get('FILEPATH', 'PublicKeyPath'), 'r') as PublicKey:
        for line in PublicKey:
            KeyValue = line.strip().split()[1]
    
    print("INFO: Provide below Information for the Rule.")
    
    while True:
        projectName = input("Project Name:\t")
        if inputValidation(projectName, FIELD_NAME="Project Name", inputType="None"):
            break
    
    while True:
        localServerIP = input("Local Server IP:\t")
        if inputValidation(localServerIP, FIELD_NAME="Local Server IP", inputType="IP"):
            break

    while True:
        localUsername = input("Local Server Username:\t")
        if inputValidation(localUsername, FIELD_NAME="Local Server Username", inputType="None"):
            break
    
    print(f"INFO: Copying public Key to the {localServerIP} for {localUsername}")
    
    try:
        LINUX_COMMAND = f'''ssh-copy-id {localUsername}@{localServerIP}'''
        process = subprocess.check_output(LINUX_COMMAND, shell=True, stderr=subprocess.STDOUT)
    except:
        print(f"Error: Unable to copy the public to {localServerIP} for {localUsername}")
        print(f"Please copy the below Public Key of the /home/{localUsername}.ssh/authorized_keys manually of the {localServerIP}")
        print("-"*100)
        PubliKey = f'''ssh-rsa {KeyValue} {localUsername}@{config.get('OTHER', 'HOSTNAME')}'''
        print(PubliKey)
        print("-"*100)
    
    while True:
        BCPServerIP = input("BCP Server IP:\t",)
        if inputValidation(BCPServerIP, FIELD_NAME="BCP Server IP", inputType="IP"):
            break
    
    while True:
        BCPUsername = input("BCP Server Username:\t")
        if inputValidation(BCPUsername, FIELD_NAME="BCP Server Username", inputType="None"):
            break    
    
    try:
        LINUX_COMMAND = f'''ssh-copy-id {BCPUsername}@{BCPServerIP}'''
        process = subprocess.check_output(LINUX_COMMAND, shell=True, stderr=subprocess.STDOUT)
    except:
        print(f"Error: Unable to copy the public to {BCPServerIP} for {BCPUsername}")
        print(f"Please copy the below Public Key of the /home/{BCPUsername}.ssh/authorized_keys manually of the {BCPServerIP}")
        PubliKey = f'''ssh-rsa {KeyValue} {localUsername}@{config.get('OTHER', 'HOSTNAME')}'''
        print(PubliKey)
    
    # Copy the Public Key to the BCP Server
    
    while True:
        alias = input("Alias:\t")
        if inputValidation(alias, FIELD_NAME="Alias", inputType="None"):
            break  

    sql_query = """INSERT INTO bcpServerDetails (projectName, localServerIP, localUsername, BCPServerIP, BCPUsername, alias) VALUES (%s, %s, %s, %s, %s, %s)"""
    values = (projectName, localServerIP, localUsername, BCPServerIP, BCPUsername, alias)

    dbcursor.execute(sql_query, values)
    database.commit()

    sql_query = f""" 
        select * from bcpServerDetails where projectName = "{projectName}" AND localServerIP = "{localServerIP}" AND localUsername = "{localUsername}" AND BCPServerIP = "{BCPServerIP}" AND BCPUsername = "{BCPUsername}"
    """
    try:
        dbcursor.execute(sql_query)
        output = dbcursor.fetchall()

        data_as_list = [list(item) for item in output]
        headers = ["Servers ID", "Project Name", "Local Server IP", "Local Server Username", "BCP Server IP", "BCP Server Username", "Alias"]
        print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
        print("INFO: New Server added successfully.")
    except:
        print("Error: Failed to Fetch Data from the database")

# Need validation here
def removServer():
    listServers()
    removeServerID = input("Servers ID:\t")
    
    database = connectToDatabase()
    dbcursor = database.cursor()
    
    sql_query = f""" 
        select * from bcpSyncRules where serversID = "{removeServerID}"
    """
    output = fetchFromDatabase(sql_query)
    data_as_list = [list(item) for item in output]
    headers = ["ID", "Project Name", "Local Server Path", "BCP Server Path", "serversID", "Extensions", "Alias"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
    
    print("INFO: Above mentioned Rules will be removed with Proect: [Enter to Confirm]\t")
    
    confirmation = input()
    
    if confirmation == "":
        
        sql_query = f""" 
            DELETE FROM bcpSyncRules WHERE serversID = '{removeServerID}';
        """
        
        dbcursor.execute(sql_query)
               
        sql_query = f""" 
            DELETE FROM bcpServerDetails WHERE serversID = '{removeServerID}';
        """
        try:
            dbcursor.execute(sql_query)
            database.commit()
            dbcursor.close()
            database.close()
        except:
            print("Error: Failed to Add Data to the database")
            
        print("INFO: Server has been removed successfully.")
    else:
        print("INFO: Server was not removed")

def inputValidation(STRING_TO_CHECK, FIELD_NAME, inputType):
    if not STRING_TO_CHECK.strip():
        print(f"Error: {FIELD_NAME} is required.")
        return False
    else:
        if inputType == "Dir":
            if isValidDir(STRING_TO_CHECK.strip()):
                return True
            else:
                print(f"Error: {STRING_TO_CHECK.strip()} is not a valid directory.")
                return False

        if inputType == "IP":
            if isValidIP(STRING_TO_CHECK.strip()):
                return True
            else:
                print(f"Error: {STRING_TO_CHECK.strip()} is not a valid IP Address")
                return False
            
        if inputType == "ID":
            if isID(STRING_TO_CHECK.strip()):
                return True
            else:
                print(f"Error: ID should be an Interger")
                return False
        if inputType == "Time":
            if isValidTime(STRING_TO_CHECK.strip()):
                return True
            else:
                print(f"Error: {FIELD_NAME} is in incorrect format. Corrent Format - 23:45")
                return False
            
        if inputType == "None":
            return True

if __name__ == "__main__":
    main(sys.argv)

