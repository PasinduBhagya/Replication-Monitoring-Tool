# BCP-Grafana

This tool is designed for monitoring the synchronization status of two directories, whether they reside on the same server or on different servers.

Initially, the tool establishes connections to both servers and retrieves the MD5 checksum values of each file within a specified folder. It then conducts an analysis of these checksum values to detect any discrepancies. Subsequently, the tool proceeds to store this analyzed data into a MySQL database for further processing.

The stored data is then utilized to generate comprehensive visualizations through a Grafana Dashboard, facilitating enhanced visibility and insight into the synchronization status.

Additionally, a command-line interface has been developed to facilitate CRUD operations on server pairs and syncing rules, thereby offering streamlined management and configuration capabilities.

![BCP Sync Monitoring Tool drawio](https://github.com/PasinduBhagya/BCP-Grafana/assets/63937160/4e2a7c8f-9137-4e29-9b7d-8e68d2db936a)

## Arechitecture of the Tool

Below is a comprehensive diagram which shows all the components of the tool.

1. **Local Server and BCP Server** -  Local server is the server which is reponsible to syncing data to BCP Server.
2. **The Application Server** - This is the server which will have the 
