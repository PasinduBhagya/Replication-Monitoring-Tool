# BCP-Grafana

The main purose of this tool is for monitor the synchronization status of two directories, which are on local server and remote server.

Initially, the tool establishes connections to both servers and retrieves the MD5 checksum values of each file within a specified folder. It then conducts an analysis of these checksum values to detect any discrepancies. Subsequently, the tool proceeds to store this analyzed data into a MySQL database for further processing.

The stored data is then utilized to generate comprehensive visualizations through a Grafana Dashboard, facilitating enhanced visibility and insight into the synchronization status.

Additionally, a command-line interface has been developed to facilitate CRUD operations on server pairs and syncing rules, thereby offering streamlined management and configuration capabilities.

[BCP Sync Monitoring Tool drawio](https://github.com/PasinduBhagya/BCP-Grafana/assets/63937160/4e2a7c8f-9137-4e29-9b7d-8e68d2db936a)

## Arechitecture of the Tool

Below is a comprehensive diagram which shows all the components of the tool.

1. Local Server and BCP Server:
    - Local Server: Responsible for initiating data synchronization to the Backup (BCP) Server.
    - BCP Server: Acts as the destination for synchronized data.
2. Application Server:
   -   
5. **The Application Server** - This is the server which will have the
   - Data Gathering tool - This is reponsible for connecting to local server and remote Server collect MD5 sum of two files on the given two directories.
   - Data Analyzign tool - This is reponsible for anaylzing data collect from server.
   - CLI - A smiple Command Line tool to manage Syncing Rules and Server Pairs
6. MySQL Database - This will store the data of Syncing rules, server pair informations and Syncing status
7. Grafana Dashboard - This will represent the data in a more visualization manner to the end user.
   
