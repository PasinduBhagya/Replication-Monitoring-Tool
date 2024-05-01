#!/usr/local/bin/python3.8
import sys
import subprocess
import mysql.connector
from tabulate import tabulate
from bcpMonFileCompare import main as fileComparison
from configparser import ConfigParser

config = ConfigParser()
config.read('./.env')

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

    sql_query = """ 
        select DISTINCT projectName from bcpServerDetails
    """
    try: 
        output = fetchFromDatabase(sql_query)
    
        for row in output:
            print(row[0])
    except:
        print("Error: Failed to Fetch Data from the database")

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
 
def addRules():
    database = connectToDatabase()
    dbcursor = database.cursor()
    
    print("INFO: Provide below Information for the Rule.")
    print("-"*80)
    listProjects()
    print("-"*80)
    projectName = input("Project Name:\t")
    localServerPath = input("Local Server Path:\t")
    bcpServerPath = input("BCP Server Path:\t")
    
    sql_query = f""" 
        select serversID, projectName, alias from bcpServerDetails where projectName = "{projectName}"
    """
    try: 
        dbcursor.execute(sql_query)
        output = dbcursor.fetchall()

        data_as_list = [list(item) for item in output]
        headers = ["ID", "Project Name", "Alias"]
        print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
    
        serversID = input("Select Servers ID from above list:\t")
        extensions = input("Extension Name: [Optional]\t")
        if extensions == "":
            extensions = "Any"
        alias = input("Alias:\t")

        sql_query = """INSERT INTO bcpSyncRules (projectName, localServerPath, bcpServerPath, serversID, extensions, alias) VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (projectName, localServerPath, bcpServerPath, serversID, extensions, alias)

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

    except:
        print("Error: Adding new record is failed")
    
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
    
def addNewServer():
    database = connectToDatabase()
    dbcursor = database.cursor()
    
    print("INFO: Provide below Information for the Rule.")
    projectName = input("Project Name:\t")    
    localServerIP = input("Local Server IP:\t")
    localUsername = input("Local Server Username:\t")
    print(f"INFO: Copying public Key to the {localServerIP} for {localUsername}")
    
    try:
        LINUX_COMMAND = f'''ssh-copy-id {localUsername}@{localServerIP}'''
        process = subprocess.check_output(LINUX_COMMAND, shell=True, stderr=subprocess.STDOUT)
    except:
        print(f"Error: Unable to copy the public to {localServerIP} for {localUsername}")
        print(f"Please copy the below Public Key of the /home/{localUsername}.ssh/authorized_keys manually of the {localServerIP}")
        print("-"*100)
        PubliKey = f'''ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0hPZhk2DqjoHNj4DIEMkjamuQvfHJvU5PXWLRBPEk3SYBVMslyS8YAdKeR9F6poLrkxr3N9PCr0oc7jPEKsFAz8AOUsv6sYO4WwHFaBxVHW7tfkU7ov+e91Wj0Msem9v202VUuZvKvZe3HrQ4Tgoua7aWwUj62+dqvBGdbILGNcxTZh9bYD0p2iTxuY4geB6WcHwI23wC5n9/lzWMd5CuX7CaAa32DRCNrtWR+Ymx7MrWkp3LA64ObaNvRNnXkvzAwj3/JhwjsBvEY2jzP4qAT7/Fg6IHL2nCQfO4qMlkhT7ihksdpLa+lfhBER5PIks3G1yZmxksfFsiY1nQ1P1h {localUsername}@localhost.localdomain'''
        print(PubliKey)
        print("-"*100)
    BCPServerIP = input("BCP Server IP:\t")
    BCPUsername = input("BCP Server Username:\t")
    
    try:
        LINUX_COMMAND = f'''ssh-copy-id {BCPUsername}@{BCPServerIP}'''
        process = subprocess.check_output(LINUX_COMMAND, shell=True, stderr=subprocess.STDOUT)
    except:
        print(f"Error: Unable to copy the public to {BCPServerIP} for {BCPUsername}")
        print(f"Please copy the below Public Key of the /home/{localUsername}.ssh/authorized_keys manually of the {localServerIP}")
        PubliKey = f'''ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0hPZhk2DqjoHNj4DIEMkjamuQvfHJvU5PXWLRBPEk3SYBVMslyS8YAdKeR9F6poLrkxr3N9PCr0oc7jPEKsFAz8AOUsv6sYO4WwHFaBxVHW7tfkU7ov+e91Wj0Msem9v202VUuZvKvZe3HrQ4Tgoua7aWwUj62+dqvBGdbILGNcxTZh9bYD0p2iTxuY4geB6WcHwI23wC5n9/lzWMd5CuX7CaAa32DRCNrtWR+Ymx7MrWkp3LA64ObaNvRNnXkvzAwj3/JhwjsBvEY2jzP4qAT7/Fg6IHL2nCQfO4qMlkhT7ihksdpLa+lfhBER5PIks3G1yZmxksfFsiY1nQ1P1h {localUsername}@localhost.localdomain'''
        print(PubliKey)
    
    # Copy the Public Key to the BCP Server
    
    alias = input("Alias:\t")

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
   
if __name__ == "__main__":
    main(sys.argv)

