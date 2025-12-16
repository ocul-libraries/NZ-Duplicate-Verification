Output files will be saved here.


**`verified_duplicates.csv`** is a report of the processing and contains three tabs:
* ready for step 2: This tab contains all rows that are included in the **`merge-combine.csv`**
* ready for review: This tab contains records that did not match on one or more of the key descriptors. These records require further review before merging
* no duplicate: these are records where no duplicate was found

**`merge-combine.csv`** can be used with Alma's built in Merge Records and Combine Inventory job.
- When running the Merge Records and Combine Inventory job:
  * use the merge rule "OCUL NZ Merge - Automated merge and combine"
  * mark the secondary record for deletion
- If the merge-combine file contains less than 100 duplicates, you can use it directly in Alma's system. 
- If the file contains more than 100 duplicates, you will need to break it up into several files before running in Alma.
- If you want to change filenames or folders, update config.json accordingly.
