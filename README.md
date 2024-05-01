# BCP-Grafana

This is a tool that can be used to monitor the status of two synced. First the tool will connect to the both servers and collect the md5 value of each file within a given folder. Then it will analyze the md5sum value if there is mistmatch between thoses collected data, and then feed the data into the MySQL database. A command line tool was developed to perform CRUD on Server Pairs and Syncing Rules.
   

![BCP Sync Monitoring Tool drawio](https://github.com/PasinduBhagya/BCP-Grafana/assets/63937160/153797ab-c9aa-477b-be6b-16421573ebfe)
