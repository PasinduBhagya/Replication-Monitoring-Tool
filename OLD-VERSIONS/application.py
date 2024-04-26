import os
from datetime import datetime
import mysql.connector
import shutil

FOLDER_NAME = datetime.now().strftime("%Y-%m-%d")
# FOLDER_NAME = "2024-04-23"

def addToDatabase():
    database = mysql.connector.connect(
        host="localhost",
        user="bcp_grafana",
        password="bcp_Grafana@123",
        database="bcp_grafana")
    dbcursor = database.cursor()

    sql_query = f""" 
        LOAD DATA INFILE '/var/lib/mysql-files/allStatusFile.csv'
        INTO TABLE statusProgress
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        IGNORE 1 ROWS
    """

    dbcursor.execute(sql_query)
    database.commit()

    dbcursor.close()
    database.close()
    print("INFO: Importing to database is completed.")


def checkFile(PROJECT):
    if os.path.isfile("PROJECT_INFO/" + PROJECT):
        print("INFO: Project file was found for " + PROJECT)
    else:
        print("INFO: No Project file was found for " + PROJECT + ". Creating a new File.")
        with open("PROJECT_INFO/" + PROJECT, 'w') as file:
            pass

def checkFileContent(PROJECT, SYNCED_FOLDER_NAME):
    with open("PROJECT_INFO/" + PROJECT, 'r') as fileContent: # Read the content of the PROJECT_INFO/CLIPPER
        if SYNCED_FOLDER_NAME not in fileContent.read(): # Check whether the WebApps is avaible on PROJECT_INFO/CLIPPER or not and if not will added
            with open("PROJECT_INFO/" + PROJECT, 'a') as fileContentToAppend:
                fileContentToAppend.write(SYNCED_FOLDER_NAME + "\n")

def addMissingData(PROJECT, FOLDER_NAME):
        if os.path.isfile("PROJECT_INFO/" + PROJECT):
            with open("PROJECT_INFO/" + PROJECT, 'r') as items:
                for item in items:
                    with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
                        allStatusFile.write(f"{FOLDER_NAME},{item.strip()},No Data,{PROJECT}\n")
                        PROJECT_STATUS = "No Data"

        return PROJECT_STATUS

def main():

    if os.path.isfile("DATA/" + FOLDER_NAME + "/allStatusFile.csv"):
        os.remove("DATA/" + FOLDER_NAME + "/allStatusFile.csv")
    
    if os.path.exists("DATA/" + FOLDER_NAME): 
        
        # Project Names
        SYC_RESULTS_FILES = os.listdir("DATA/" + FOLDER_NAME) # Get the Date with the Folder name
        
        print("INFO: Listing Project Names.")
        print(SYC_RESULTS_FILES) # Print the Folder Name list => ["CLIPPER", "TB", "YAS"]

        with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
            allStatusFile.write(f"date,itemName,status,itemType\n")

        for PROJECT in SYC_RESULTS_FILES:
            
            checkFile(PROJECT) # CLIPPER
            
            PROJECT_STATUS = "Success"
            RESULTS_FILE_NAME = "DATA/" + FOLDER_NAME + "/" + PROJECT # DATA/2024-04-19/CLIPPER <-- This the File contains Success and Failed Status of each Folder

            # Check for Duplicate data

            # Checking for Missing Data
            with open(RESULTS_FILE_NAME, 'r') as resultsContent:
                if not resultsContent.read():
                    print(f"Warning: The content of the {PROJECT} is not available. Setting the Project status to No Data.")
                    print("INFO: Data was found on " + RESULTS_FILE_NAME)
                
                    PROJECT_STATUS = addMissingData(PROJECT, FOLDER_NAME)

            print("INFO: Reading " + RESULTS_FILE_NAME)

            with open(RESULTS_FILE_NAME, 'r') as resultsContent:

                for results in resultsContent: # Read on line for the 2024-04-19/CLIPPER 
                    SYNCED_FOLDER_NAME = results.split(",")[0].strip() # WebApps
        
                    checkFileContent(PROJECT, SYNCED_FOLDER_NAME) # checkFileContent(CLIPPER, WebApps)

                    STATUS = results.split(",")[1].strip() # Success
                    print(f"{FOLDER_NAME},{SYNCED_FOLDER_NAME},{STATUS},{PROJECT}")
                    with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
                        allStatusFile.write(f"{FOLDER_NAME},{SYNCED_FOLDER_NAME},{STATUS},{PROJECT}\n")
                    if STATUS == "Failed":
                        PROJECT_STATUS = "Failed"

            with open("DATA/" + FOLDER_NAME + "/allStatusFile.csv", 'a') as allStatusFile:
                allStatusFile.write(f"{FOLDER_NAME},{PROJECT},{PROJECT_STATUS},Summary\n")

        if os.path.isfile("/var/lib/mysql-files/allStatusFile.csv"):
            os.remove("/var/lib/mysql-files/allStatusFile.csv")
            shutil.copy("DATA/" + FOLDER_NAME + "/allStatusFile.csv", "/var/lib/mysql-files/")
        
        print("INFO: Importing data to the database.")
        addToDatabase()

    else:
        print( FOLDER_NAME + "was not found..")

if __name__ == "__main__":
    main()