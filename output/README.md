Output files will be saved here.

Notes
- merge-combine.csv file that can be used with Alma's built in Merge Records and Combine Inventory job.
- When running the Merge Records and Combine Inventory job use the merge rule "OCUL NZ Merge - Automated merge and combine" and mark the secondary record for deletion
- If the merge-combine file contains less than 100 duplicates, you can use it directly in Alma's system. 
- If the file contains more than 100 duplicates, you will need to break it up into several files before running in Alma.
- If you want to change filenames or folders, update config.json accordingly.
