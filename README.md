# NZ-Duplicate-Verification
This project compares publisher, publication data, and edition statements in bibliographic records to verify true duplicates before merging. It uses a CSV input and JSON transformation rules, then outputs a a merge-combine.csv file that can be used with Alma's built in Merge Records and Combine Inventory job.

The CSV input file can be exported from the shared Alma Analytic:
/Shared Folders/UTON Network 01OCUL_NETWORK/Reports/NZ Duplicates - for script/NZ Duplicates - TEMPLATE


Requirements
Python: 3.8 or higher
Libraries (install via pip):
- pandas 
- openpyxl 
- xlsxwriter

Files & Folders
The project expects the following structure:
project-root/
│
├── ocul-cf_nz_duplicate_verification.py                
├── config.json              
│
├── data/                    
│   └── NZ Duplicates - TEMPLATE.csv # Exported CSV file from Alma Analytics
│
├── json/                    
│   ├── publisher.json
│   └── publicationdate.json
│
└── output/                  
    ├── updated_NZ Duplicates - TEMPLATE.csv
    ├── verified_duplicates.xlsx
    ├── updated_verified_duplicates.xlsx
    └── merge-combine.csv

Usage
- Export CSV file from the Alma Analytic 
- Create a data/ folder and an output/ folder in the same folder as the python script, json/ folder, and cong.json file.
- Place the CSV file in the data/ folder.
- Run the script: ocul-cf_nz_duplicate_verification.py
- Final mapped CSV is in the output/ folder (merge-combine.csv)

Notes
- When running the Merge Records and Combine Inventory job use the merge rule "OCUL NZ Merge - Automated merge and combine" and mark the secondary record for deletion
- If the merge-combine file contains less than 100 duplicates, you can use it directly in Alma's system. 
- If the file contains more than 100 duplicates, you will need to break it up into several files before running in Alma.
- If you want to change filenames or folders, update config.json accordingly.
