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
>`--help`

> `--list-projects`

> `--list-rules`

> `--list-servers`

> `--add-rule`

> `--add-new-server`

> `--remove-rule-with-id`

> `--remove-server`

> `--run-rules`

































