import os
from datetime import datetime, timedelta
import mysql.connector
import shutil
from configparser import ConfigParser

config = ConfigParser()
baseDIR = os.path.dirname(os.path.realpath(os.path.dirname(__file__) + "/bcpsyn"))
config.read("./.env")

FOLDER_NAME = datetime.now().strftime("%Y-%m-%d")
exeTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
YESTERDAY_DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
LogTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

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

def removeTodayData(FOLDER_NAME):
    database = connectToDatabase()
    dbcursor = database.cursor()
    sql_query = f'''delete from statusProgress where dateTime = "{FOLDER_NAME} 00:00:00"'''
    dbcursor.execute(sql_query)
    database.commit()
    dbcursor.close()
    database.close()

def addToDatabase(csvFileName):
    database = connectToDatabase()
   
    if os.path.isfile(f"/var/lib/mysql-files/{csvFileName}"):
        os.remove(f"/var/lib/mysql-files/{csvFileName}")
    try:
        shutil.copy(f"DATA/{FOLDER_NAME}/{csvFileName}", "/var/lib/mysql-files/")
        dbcursor = database.cursor()
        sql_query = f""" 
            LOAD DATA INFILE '/var/lib/mysql-files/{csvFileName}'
            INTO TABLE statusProgress
            FIELDS TERMINATED BY ','
            ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            (dateTime, itemName, status, itemType)
        """
        dbcursor.execute(sql_query)
        database.commit()
        dbcursor.close()
        database.close()
        print(f"INFO: {exeTime} Importing to database is completed.")
    except Exception as e:
        print(f"Error: {exeTime} An error occurred while copying the file. " + str(e))

def getItemsFromDatabase(PROJECT, YESTERDAY_DATE):
    database = connectToDatabase()
    item_list_per_project = []
    dbcursor = database.cursor()
    sql_query = f""" 
        SELECT itemName FROM statusProgress WHERE dateTime = "{YESTERDAY_DATE}" AND itemType = "{PROJECT}"
    """
    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    for row in output:
        item_list_per_project.append(row[0])
    return item_list_per_project

def getProjectStatusFromDatabase(PROJECT):
    database = connectToDatabase()
    status_list_per_project = []
    dbcursor = database.cursor()
    sql_query = f""" 
        SELECT status FROM statusProgress WHERE dateTime = "{FOLDER_NAME}" AND itemType = "{PROJECT}"
    """
    dbcursor.execute(sql_query)
    output = dbcursor.fetchall()
    for row in output:
        status_list_per_project.append(row[0])
    print(f"INFO: {exeTime} Status of {PROJECT} - " + str(status_list_per_project))
    if "Failed" in status_list_per_project or "No Data" in status_list_per_project:
        print(f"INFO: {exeTime} One or more Items has failed or has no data on {PROJECT}. Therefore overall project status set to Failed.")
        PROJECT_STATUS = "Failed"
    elif len(status_list_per_project) == 0:
        print(f"INFO: {exeTime} No Data was found for {PROJECT}. Therefore overall project status set to No Data.")
        PROJECT_STATUS = "No Data"
    else:
        print(f"INFO: {exeTime} All Items are in Success state on {PROJECT}. Therefore overall project status set to Success.")
        PROJECT_STATUS = "Success"
    
    return PROJECT_STATUS 
   

def main():

    if os.path.isfile("DATA/" + FOLDER_NAME + "/allStatusFile.csv"):
        os.remove("DATA/" + FOLDER_NAME + "/allStatusFile.csv")
    if os.path.isfile("DATA/" + FOLDER_NAME + "/ProjectStatusFile.csv"):
        os.remove("DATA/" + FOLDER_NAME + "/ProjectStatusFile.csv")
    
    if os.path.exists("DATA/" + FOLDER_NAME): 
        
        SYC_RESULTS_FILES = os.listdir("DATA/" + FOLDER_NAME) # Get the Date with the Folder name
        
        print(f"INFO: {exeTime} Listing Project Names " + str(SYC_RESULTS_FILES))

        for PROJECT in SYC_RESULTS_FILES:
            print("-"*100)
            newResultsItemsPerProj = []

            # Get Previous ItemNames from Project for Yesterday
            itemsPerProjList = getItemsFromDatabase(PROJECT, YESTERDAY_DATE)
                        
            RESULTS_FILE_NAME = "DATA/" + FOLDER_NAME + "/" + PROJECT # DATA/2024-04-19/CLIPPER <-- This the File contains Success and Failed Status of each Folder

            print(f"{LogTime} INFO: Reading " + RESULTS_FILE_NAME)

            print(f"{LogTime} INFO: From Database for {PROJECT} on {YESTERDAY_DATE} - " + str(itemsPerProjList))
            
            with open(RESULTS_FILE_NAME, 'r') as resultsFile:
                for line in resultsFile:
                    newResultsItemsPerProj.append(line.split(',')[0])
                    # Adding today status to the allStatusFile.csv file
                    with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
                        allStatusFile.write(f"{FOLDER_NAME},{line.strip()},{PROJECT}\n")
            
            print(f"{LogTime} INFO: From new Results file for{PROJECT} on {FOLDER_NAME} - " + str(newResultsItemsPerProj))

            missingItemsFromPreviousDate = set(itemsPerProjList) - set(newResultsItemsPerProj) # Set these for Missing Items
            # Adding missing items for allStatusFile.csv file as no data
            for item in missingItemsFromPreviousDate:
                with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
                    allStatusFile.write(f"{FOLDER_NAME},{item.strip()},No Data,{PROJECT}\n")
            
            newItemsForToday = set(newResultsItemsPerProj) - set(itemsPerProjList) # Set them as new Items for today
            
            print(f"{LogTime} INFO: Missing From Previous Date " + str(missingItemsFromPreviousDate))
            print(f"{LogTime} INFO: New Items for Today " + str(newItemsForToday))

        print("#"*100)
        print(f"{LogTime} INFO: Adding all Item Status to the Database.")
        # Add to the DB using CSV file allStatusFile.csv
        addToDatabase(csvFileName="allStatusFile.csv")

        print("#"*100)
        
        for PROJECT in SYC_RESULTS_FILES:
            print("-"*100)
            PROJECT_STATUS = getProjectStatusFromDatabase(PROJECT)
        
            # Writing the Project overall status to the ProjectStatusFile.csv  
            with open("DATA/" + FOLDER_NAME + "/ProjectStatusFile.csv", 'a') as projectStatusFile:
                projectStatusFile.write(f"{FOLDER_NAME},{PROJECT},{PROJECT_STATUS},Summary\n")
            
            print(f"{LogTime} INFO: Project status of {PROJECT} is - " + PROJECT_STATUS)

        # Add to the DB using ProjectStatusFile.csv
        addToDatabase(csvFileName="ProjectStatusFile.csv")    

    else:
        print( f"Error: {exeTime}" + FOLDER_NAME + " was not found..")

if __name__ == "__main__":
    main()

    
