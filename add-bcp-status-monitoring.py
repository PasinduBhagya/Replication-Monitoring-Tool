import sys
import mysql.connector
from tabulate import tabulate

arguments = sys.argv

def main(arguments):
  
    if "--help" in arguments:
        print('''Usage: This tool can be use to add, remove and read bcp sync related rules to the application. 

    Options and arguments.

        --help\t: Print this help message and exit.
          
        --list-projects\t:
        --list-rules\t:
        --list-servers\t:
                 
        --add-rule\t:
        --add-new-server\t:
          
        --remove-rule-with-id\t:       
        --remove-server\t:       
    
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
                           "--remove-server"] for element in arguments[1:]):
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
        print("--add-new-server")
    elif arguments[1:2][0] == "--remove-rule-with-id":
        removeRuleID()
    elif arguments[1:2][0] == "--remove-server":
        print("--remove-server")

def listProjects():
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    dbcursor = database.cursor()

    sql_query = f""" 
        select DISTINCT projectName from bcpSyncRules
    """

    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    for row in output:
        print(row[0])

def listRules():
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    dbcursor = database.cursor()

    sql_query = f""" 
        select * from bcpSyncRules
    """

    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    
    data_as_list = [list(item) for item in output]
    headers = ["ID", "Name", "Source Path", "Destination Path", "Extensions"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))

def listServers():
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    dbcursor = database.cursor()

    sql_query = f""" 
        select * from bcpServerDetails
    """

    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    
    data_as_list = [list(item) for item in output]
    headers = ["Project Name", "Local Server IP", "Local Server Username", "DR Server IP", "DR Server Username"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
 
def addRules():
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    dbcursor = database.cursor()
    print("INFO: Provide below Information for the Rule.")
    projectName = input("Project Name:\t")
    srcPath = input("Local Server Path:\t")
    destPath = input("BCP Server Path:\t")
    extensions = input("Extension Name: [Optional]\t")

    sql_query = f"""INSERT INTO bcpSyncRules (projectName, srcPath, destPath, extensions) VALUES (%s, %s, %s, %s)"""
    values = (projectName, srcPath, destPath, extensions)

    dbcursor.execute(sql_query, values)
    database.commit()

    sql_query = f""" 
        select * from bcpSyncRules where projectName = "{projectName}" AND srcPath = "{srcPath}" AND destPath = "{destPath}"
    """
    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()

    data_as_list = [list(item) for item in output]
    headers = ["Project Name", "Local Server Path", "BCP Server Path", "Extension Name"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
    print("INFO: Rule added successfully.")
    

    # INSERT INTO bcpSyncRules (projectName, srcPath, destPath, extensions) VALUES ("YAS", "/usr/local/tbx/yasqa/Scheduler_Resources/", "/usr/local/tbx/yasqa/Scheduler_Resources/", "");
    
def removeRuleID():
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    dbcursor = database.cursor()
    ruleID = input("Rule ID to remove:\t")
    sql_query = f""" 
        DELETE FROM bcpSyncRules WHERE ruleID = '{ruleID}';

    """

    dbcursor.execute(sql_query)
    database.commit()
    dbcursor.close()
    database.close()
    print("INFO: Rule has been removed successfuly")    
    
def addNewServer():
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    dbcursor = database.cursor()
    print("INFO: Provide below Information for the Rule.")
    projectName = input("Project Name:\t")
    srcIP = input("Local Server IP:\t")
    srcUsername = input("Local Server Username:\t")
    dstIP = input("BCP Server IP:\t")
    dstUsername = input("BCP Server Username:\t")

    sql_query = f"""INSERT INTO bcpServerDetails (projectName, srcIP, srcUsername, dstIP, dstUsername) VALUES (%s, %s, %s, %s, %s)"""
    values = (projectName, srcIP, srcUsername, dstIP, dstUsername)

    dbcursor.execute(sql_query, values)
    database.commit()

    sql_query = f""" 
        select * from bcpServerDetails where projectName = "{projectName}" AND srcIP = "{srcIP}" AND srcUsername = "{srcUsername}" AND dstIP = "{dstIP}" AND dstUsername = "{dstUsername}"
    """
    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()

    data_as_list = [list(item) for item in output]
    headers = ["Project Name", "Local Server IP", "Local Server Username", "DR Server IP", "DR Server Username"]
    print(tabulate(data_as_list, headers=headers, tablefmt="grid"))
    print("INFO: New Server added successfully.")


main(arguments)





# bcp-sync-mon --list-projects

# bcp-sync-mon --add-rule --project="YAS" --src-path="/usr/local/tbx/yasqa/Scheduler_Resources/" --dst-path="/usr/local/tbx/yasqa/Scheduler_Resources/" --extensions="zip"
# --add-new-server 


# bcp-sync-mon --list-rules --project="YAS"
# bcp-sync-mon --remove-rule --rule-id=1
