# Commvault-Jobs-2-SQL

# Description
Quick and dirty Python script to insert Commvault backup job data into an SQL database as a source for Grafana. 

Commvault does not provide a good way to track client/subclient backup growth over time. By logging the backup data size to an SQL database, backup client size can be graphed in Grafana. This can be used to quickly identify backup job growth in a per client/subclient level. Be it a small growth over a year, or a sudden 5TB of data added at once. 

 

# How it works:
A small Python script accesses the Commvault API to retrieve a list of all Commvault backup jobs and inserts them into an SQL database.  Backup time, client, subclient, application side and disk size for all backup jobs are logged into SQL on each run. This script is designed to run each day (from cron) or as often as needed. It can be run as many times as needed without putting duplicates into the SQL database. 


# Notes on Grafana and incremental/full backup jobs.
For a “client growth over time” style graph, assuming there is a weekly full backup, the best type of graph is to sum all the backups of the entire week. This smooths out the once a week large full backups from the daily incremental. This provides the best viability to sudden and long term growth, at the cost of partial weeks being unless, along with the total data backed up being pointless.  Example Grafana SQL query below. Set the time picker to at least 30 days if not longer. 

SELECT
  $__timeGroupAlias(timestamp,$__interval),
  host AS metric,
  sum(sizeOfApplication) AS "size"
FROM backup_jobs
WHERE
  $__timeFilter(timestamp)
GROUP BY WEEK(timestamp),host
ORDER BY $__timeGroup(timestamp,$__interval)


SELECT
  $__timeGroupAlias(timestamp,$__interval),
  subclient AS metric, 
  sum(sizeOfApplication) AS "size"
FROM backup_jobs
WHERE
  $__timeFilter(timestamp) and appTypeName = "SQL Server"
GROUP BY WEEK(timestamp),subclient
ORDER BY $__timeGroup(timestamp,$__interval)

![Commvault-SQL1](https://user-images.githubusercontent.com/107140997/173424146-2b77b8b4-5184-42ee-9bff-dce543e2ab51.png)
![Commvault-SQL2](https://user-images.githubusercontent.com/107140997/173424160-143619ef-eda7-46fd-a7ab-35573a74cedc.png)

# Install
See the python script for details. It needs account access to the Commvault Webserver. This is not the Commvault Console unless you installed the Webserver component on the Commvault Console server. It also needs access to a MySQL/Maria SQL server. Create a database and load in the sql file to create the table. Assuming everything is correct, run the python script. It should access the Commvault API and update the SQL database. 
Connect your Grafana install to the SQL database and graph away. See the json files for example panels. For best result, set the time picker for 30 days or more. 

