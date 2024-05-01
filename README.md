# BCP-Grafana

This tool is designed for monitoring the synchronization status of two directories, whether they reside on the same server or on different servers.

Initially, the tool establishes connections to both servers and retrieves the MD5 checksum values of each file within a specified folder. It then conducts an analysis of these checksum values to detect any discrepancies. Subsequently, the tool proceeds to store this analyzed data into a MySQL database for further processing.

The stored data is then utilized to generate comprehensive visualizations through a Grafana Dashboard, facilitating enhanced visibility and insight into the synchronization status.

Additionally, a command-line interface has been developed to facilitate CRUD operations on server pairs and syncing rules, thereby offering streamlined management and configuration capabilities.
   

![BCP Sync Monitoring Tool drawio](https://github.com/PasinduBhagya/BCP-Grafana/assets/63937160/153797ab-c9aa-477b-be6b-16421573ebfe)
