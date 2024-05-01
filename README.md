# BCP-Grafana

The main purose of this tool is for monitor the synchronization status of two directories, which are on local server and remote server.

Initially, the tool establishes connections to both servers and retrieves the MD5 checksum values of each file within a specified folder. It then conducts an analysis of these checksum values to detect any discrepancies. Subsequently, the tool proceeds to store this analyzed data into a MySQL database for further processing.

The stored data is then utilized to generate comprehensive visualizations through a Grafana Dashboard, facilitating enhanced visibility and insight into the synchronization status.

Additionally, a command-line interface has been developed to facilitate CRUD operations on server pairs and syncing rules, thereby offering streamlined management and configuration capabilities.

## Arechitecture of the Tool

Below is a comprehensive diagram which shows all the components of the tool.

<img src="https://github.com/PasinduBhagya/BCP-Grafana/assets/63937160/4e2a7c8f-9137-4e29-9b7d-8e68d2db936a" width="600">

1. **Local Server and BCP Server:**
    - Local Server: Responsible for initiating data synchronization to the Backup (BCP) Server.
    - BCP Server: Acts as the destination for synchronized data.
2. **Application Server:**
    - Data Gathering Tool: Collects MD5 checksums of files within specified directories from both the local and remote servers
    - Data Analyzing Tool: Analyzes collected checksums to identify discrepancies between the directories.
    - CLI (Command Line Interface): Offers a user-friendly command-line interface for managing syncing rules and server pairs.
3. **MySQL Database:** Stores syncing rules, server pair information, and synchronization status data.
4. **Grafana Dashboard:** Visualizes stored data, providing users with intuitive insights into synchronization status and any detected discrepancies.


## Grafana Dashboard Overview

## Installation of the tool

## Database Architecture

## Configuring Monitoring with CLI

To use the CLI of the tool, please use the command called `bcpsyn` with the required flags. You can list down all the possible commands by using the below commands. 
`bcpsyn --help`
Below all the all possible flags comes with this tool.
>`--help` - Displays the help menu.

> `--list-projects` - Lists all available projects along with their details.

> `--list-rules` - Displays a comprehensive list of rules associated with the projects.

> `--list-servers` - Shows all registered Local BCP server pairs.

> `--add-rule` - Adds a new rule to specify synchronization criteria.

> `--add-new-server` - Registers a new Local BCP server pair.

> `--remove-rule-with-id` - Removes a specific rule identified by its unique ID.

> `--remove-server` - Deletes a Local BCP server pair (will remove all rules associated with that pair).

> `--run-rules` - Manually runs the rules.

### Add a New Server Pair
To add  new Server Pair please type `bcpsyn --add-new-servers` and then press enter. Then it will request for the required information. 

@ Image here

Once you enter the server username and the password, it is prompt for the password of the user on the given IP Address. Once you enter the password the tool will copy its public key to that user authorized keys files to enable the key based authentication later which will be used to connect to the server.
> [!IMPORTANT]
> In case the above public key copy phase fail you need to manualy add the public key will be prompt by the tool after it fails.

To veriy the server Pair was added you can use `bcpsyn --list-servers` command. It will list down all available servers.

To remove a server please enter `bcpsyn --remove-server` and press enter. Then you need to add the serverID that required to be removed. 

> [!WARNING]
> When you remove a server pair it will remove all the Rules associated with it.

## How the tool works?
The tools use rules to check the synchronization status of the to folder reside on two diffrent servers. You can list down all the rules by using `bcpsyn --list-rules` command.



Column Name  | Description
------------- | -------------
ID  | Rule ID which will be created automaticaly.
Project Name  | Name of the Project.
Local Server Path  | Absoulte path to the directory on the local server. 
BCP Server Path  | Absoulte path to the directory on the BCP server. 
serversID | The ID of the Servers pair which will be added using `bcpsyn --add-new-server`.
Alias  | The name that will be visible on the Grafana Dashboard.

Each rule has an ServerID which will consits of data of the Local and BCP Server. You can list the server information by using `bcpsyn --list-servers`

