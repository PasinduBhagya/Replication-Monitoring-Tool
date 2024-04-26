import os
from datetime import datetime, timedelta
import mysql.connector
import shutil

FOLDER_NAME = datetime.now().strftime("%Y-%m-%d")
YESTERDAY_DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def addToDatabase(csvFileName):
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    if os.path.isfile(f"/var/lib/mysql-files/{csvFileName}"):
        os.remove(f"/var/lib/mysql-files/{csvFileName}")
    try:
        shutil.copy("DATA/" + FOLDER_NAME + f"/{csvFileName}", "/var/lib/mysql-files/")
    except:
        print("Error: An error occured file copying the file.")
    dbcursor_1 = database.cursor()

    sql_query = f""" 
        LOAD DATA INFILE '/var/lib/mysql-files/{csvFileName}'
        INTO TABLE statusProgress
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
    """

    dbcursor_1.execute(sql_query)
    database.commit()

    dbcursor_1.close()
    database.close()
    print("INFO: Importing to database is completed.")

def getItemsFromDatabase(PROJECT,YESTERDAY_DATE):
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    item_list_per_project = []
    dbcursor = database.cursor()

    sql_query = f""" 
        select itemName from statusProgress where dateTime = "{YESTERDAY_DATE}" AND itemType = "{PROJECT}"
    """

    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    for row in output:
        item_list_per_project.append(row[0])
    
    return item_list_per_project

def getProjectStatusFromDatabase(PROJECT):
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    
    status_list_per_project = []
    dbcursor_2 = database.cursor()

    sql_query = f""" 
        select status from statusProgress where dateTime = "{FOLDER_NAME}" AND itemType = "{PROJECT}"
    """

    dbcursor_2.execute(sql_query)
    output = dbcursor_2.fetchall()
    for row in output:
        status_list_per_project.append(row[0])
    
    print(f"INFO: Status of {PROJECT}" + str(status_list_per_project))
    if "Failed" in status_list_per_project:
        print(f"INFO: One or more Items has failed on {PROJECT}. Therefore overall project status set to Failed.")
        PROJECT_STATUS = "Failed"
    elif "No Data" in status_list_per_project:
        print(f"INFO: One or more Items has no data on {PROJECT}. Therefore overall project status set to Failed.")
        PROJECT_STATUS = "Failed"
    else:
        print(f"INFO: All Items are in Success state on {PROJECT}. Therefore overall project status set to Success.")
        PROJECT_STATUS = "Success"
    return PROJECT_STATUS    

def main():

    if os.path.isfile("DATA/" + FOLDER_NAME + "/allStatusFile.csv"):
        os.remove("DATA/" + FOLDER_NAME + "/allStatusFile.csv")
    if os.path.isfile("DATA/" + FOLDER_NAME + "/ProjectStatusFile.csv"):
        os.remove("DATA/" + FOLDER_NAME + "/ProjectStatusFile.csv")
    
    if os.path.exists("DATA/" + FOLDER_NAME): 
        
        # Project Names
        SYC_RESULTS_FILES = os.listdir("DATA/" + FOLDER_NAME) # Get the Date with the Folder name
        
        print("INFO: Listing Project Names " + str(SYC_RESULTS_FILES))

        for PROJECT in SYC_RESULTS_FILES:
            print("-"*100)
            newResultsItemsPerProj = []

            # Get Previous ItemNames from Project for Yesterday
            itemsPerProjList = getItemsFromDatabase(PROJECT, YESTERDAY_DATE)
                        
            RESULTS_FILE_NAME = "DATA/" + FOLDER_NAME + "/" + PROJECT # DATA/2024-04-19/CLIPPER <-- This the File contains Success and Failed Status of each Folder

            print("INFO: Reading " + RESULTS_FILE_NAME)

            print(f"INFO: From Database for {PROJECT} on {YESTERDAY_DATE} - " + str(itemsPerProjList))
            
            with open(RESULTS_FILE_NAME, 'r') as resultsFile:
                for line in resultsFile:
                    newResultsItemsPerProj.append(line.split(',')[0])
                    # Adding today status to the allStatusFile.csv file
                    with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
                        allStatusFile.write(f"{FOLDER_NAME},{line.strip()},{PROJECT}\n")
            
            print(f"INFO: From new Results file for{PROJECT} on {FOLDER_NAME} - " + str(newResultsItemsPerProj))

            missingItemsFromPreviousDate = set(itemsPerProjList) - set(newResultsItemsPerProj) # Set these for Missing Items
            # Adding missing items for allStatusFile.csv file as no data
            for item in missingItemsFromPreviousDate:
                with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
                    allStatusFile.write(f"{FOLDER_NAME},{item.strip()},No Data,{PROJECT}\n")
            
            newItemsForToday = set(newResultsItemsPerProj) - set(itemsPerProjList) # Set them as new Items for today
            
            print("INFO: Missing From Previous Date " + str(missingItemsFromPreviousDate))
            print("INFO: New Items for Today " + str(newItemsForToday))

        print("#"*100)
        print("INFO: Adding all Item Status to the Database.")
        # Add to the DB using CSV file allStatusFile.csv
        addToDatabase(csvFileName="allStatusFile.csv")

        print("#"*100)
        
        for PROJECT in SYC_RESULTS_FILES:
            print("-"*100)
            PROJECT_STATUS = getProjectStatusFromDatabase(PROJECT)
        
            # Writing the Project overall status to the ProjectStatusFile.csv  
            with open("DATA/" + FOLDER_NAME + "/ProjectStatusFile.csv", 'a') as projectStatusFile:
                projectStatusFile.write(f"{FOLDER_NAME},{PROJECT},{PROJECT_STATUS},Summary\n")
            
            print(f"INFO: Project status of {PROJECT} is - " + PROJECT_STATUS)

        # Add to the DB using ProjectStatusFile.csv
        addToDatabase(csvFileName="ProjectStatusFile.csv")    

    else:
        print( "Error: " + FOLDER_NAME + "was not found..")

if __name__ == "__main__":
    main()

    
