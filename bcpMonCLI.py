import sys
import mysql.connector
from tabulate import tabulate

arguments = sys.argv

def main(arguments):
    if len(arguments) == 1:
        print("Error: To few arguments. Unable to execute. Use --help flag to see arguments.")
        exit()
  
    if "--help" in arguments:
        print('''Usage: This tool can be used to add, remove, and read bcp sync related rules to the application. 

    Options and arguments.

        --help\t: Print this help message and exit.
          
        --list-projects\t:
        --list-rules\t:
        --list-servers\t:
                 
        --add-rule\t:
        --add-new-server\t:
          
        --remove-rule-with-id\t:       
        --remove-server\t:
        --show-logs\t:       
    
    If you need any other support, please contact Pasindu Bhagya - pasindub@codegen.net.
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
                           "--show-logs"] for element in arguments[1:]):
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

def listProjects():

    sql_query = """ 
        select DISTINCT projectName from bcpServerDetails
    """
    output = fetchFromDatabase(sql_query)
    for row in output:
        print(row[0])

def listRules():
    sql_query = """ 
        select * from bcpSyncRules
    """
    output = fetchFromDatabase(sql_query)
    data_as_list = [list(item) for item in output]
    headers = ["ID", "Project Name", "Local Server Path", "BCP Server Path", "serversID", "Extensions", "Alias"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))

def listServers():
    sql_query = """ 
        select * from bcpServerDetails
    """
    output = fetchFromDatabase(sql_query)
    
    data_as_list = [list(item) for item in output]
    headers = ["Servers ID", "Project Name", "Local Server IP", "Local Server Username", "BCP Server IP", "BCP Server Username", "Alias"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
 
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

def removeRuleID():
    listRules()
    database = connectToDatabase()
    dbcursor = database.cursor()
    
    ruleID = input("Rule ID to remove:\t")
    sql_query = f""" 
        DELETE FROM bcpSyncRules WHERE ruleID = '{ruleID}';
    """

    dbcursor.execute(sql_query)
    database.commit()
    dbcursor.close()
    database.close()
    print("INFO: Rule has been removed successfully.")    
    
def addNewServer():
    database = connectToDatabase()
    dbcursor = database.cursor()
    
    print("INFO: Provide below Information for the Rule.")
    projectName = input("Project Name:\t")
    localServerIP = input("Local Server IP:\t")
    localUsername = input("Local Server Username:\t")
    
    # Copy the Public Key to the Local Server
    
    BCPServerIP = input("BCP Server IP:\t")
    BCPUsername = input("BCP Server Username:\t")
    
    # Copy the Public Key to the BCP Server
    
    alias = input("Alias:\t")

    sql_query = """INSERT INTO bcpServerDetails (projectName, localServerIP, localUsername, BCPServerIP, BCPUsername, alias) VALUES (%s, %s, %s, %s, %s, %s)"""
    values = (projectName, localServerIP, localUsername, BCPServerIP, BCPUsername, alias)

    dbcursor.execute(sql_query, values)
    database.commit()

    sql_query = f""" 
        select * from bcpServerDetails where projectName = "{projectName}" AND localServerIP = "{localServerIP}" AND localUsername = "{localUsername}" AND BCPServerIP = "{BCPServerIP}" AND BCPUsername = "{BCPUsername}"
    """
    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()

    data_as_list = [list(item) for item in output]
    headers = ["Servers ID", "Project Name", "Local Server IP", "Local Server Username", "BCP Server IP", "BCP Server Username", "Alias"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
    print("INFO: New Server added successfully.")

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
        dbcursor.execute(sql_query)
   
        print("INFO: Server has been removed successfully.")
    else:
        print("INFO: Server was not removed")
 
    database.commit()
    dbcursor.close()
    database.close()
        
    
if __name__ == "__main__":
    import sys
    main(sys.argv)

