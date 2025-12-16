import pandas as pd
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent  # folder where this script lives

def edit_csv_based_on_json(csv_file_path, json_publisher_path, json_publicationdate_path):
    """
    Function to edit a CSV file based on publisher and publication date JSON operations.
    """
    df_csv = pd.read_csv(csv_file_path, dtype=str, encoding='utf-8')
    df_csv["Network Id"] = df_csv["Network Id"].astype(str)

    # Publisher edits
    with open(json_publisher_path, 'r', encoding='utf-8') as json_file:
        publisher_data = json.load(json_file)
        for operation in publisher_data:
            if operation.get("op") == "core/mass-edit":
                column_name = operation.get("columnName")
                edits = operation.get("edits", [])
                for edit in edits:
                    from_values = [str(v) for v in edit.get("from", [])]
                    to_value = edit.get("to")
                    df_csv.loc[df_csv[column_name].isin(from_values), column_name] = to_value

    # Publication date edits
    with open(json_publicationdate_path, 'r', encoding='utf-8') as json_file:
        publication_date_data = json.load(json_file)
        for operation in publication_date_data:
            if operation.get("op") == "core/mass-edit":
                column_name = operation.get("columnName")
                edits = operation.get("edits", [])
                for edit in edits:
                    from_values = [str(v) for v in edit.get("from", [])]
                    to_value = edit.get("to")
                    df_csv.loc[df_csv[column_name].isin(from_values), column_name] = to_value

    # Save updated CSV next to input
    output_file_path = csv_file_path.parent / f'updated_{csv_file_path.name}'
    df_csv.to_csv(output_file_path, index=False)
    print(f" Updated CSV saved at: {output_file_path}")
    return output_file_path


def update_preferred_merge_column(excel_file_path, sheet_name):
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, dtype=str)
    df["Bibliographic Rank"] = pd.to_numeric(df["Bibliographic Rank"], errors="coerce")
    df.sort_values(by=["OCLC Control Number (035a)", "Bibliographic Rank"],
                   ascending=[True, False], inplace=True)
    df["Preferred_Merge"] = ""

    for ocn, group in df.groupby("OCLC Control Number (035a)"):
        group_indices = group.index
        if len(group_indices) > 0:
            df.loc[group_indices[0], "Preferred_Merge"] = "preferred"
            for idx in group_indices[1:]:
                df.loc[idx, "Preferred_Merge"] = "merge"

    updated_excel_file_path = excel_file_path.parent / f'updated_{excel_file_path.name}'
    with pd.ExcelWriter(updated_excel_file_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    print(f" Updated Excel file saved at: {updated_excel_file_path}")
    return updated_excel_file_path


if __name__ == "__main__":
    # Load config.json safely
    config_path = BASE_DIR / "config.json"
    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    # Resolve paths relative to script folder
    csv_file_path = BASE_DIR / config["Paths"]["csv_file_path"]
    json_publisher_path = BASE_DIR / config["Paths"]["json_publisher_path"]
    json_publicationdate_path = BASE_DIR / config["Paths"]["json_publicationdate_path"]
    updated_file_path = BASE_DIR / config["Paths"]["updated_file_path"]

    # Step 1: Edit CSV
    updated_csv = edit_csv_based_on_json(csv_file_path, json_publisher_path, json_publicationdate_path)

    # Step 2: Transform data
    data = pd.read_csv(updated_file_path, dtype=str, encoding='utf-8')
    data.columns = [
        'OCLC Control Number (035a)', 'Network Id',
        'Resource Type', 'Edition Simplified (Num)', 'Edition Simplified (Text)',
        'Material Type', 'Brief Level', 'Bibliographic Rank', 'Held By',
        'Title', 'Publication Date', 'Publisher', 'Publication Place', 'Edition',
        'Language Of Cataloging', 'Language Code',
    ]
    df = pd.DataFrame(data).fillna('no data')
    df['freq_count'] = df.groupby('OCLC Control Number (035a)')['OCLC Control Number (035a)'].transform('count')

    df_multiples = df.query('freq_count >= 2')
    df_singles = df.query('freq_count == 1')

    df_multiples_ready_for_step_2 = df_multiples[
        df_multiples.duplicated(
            subset=['OCLC Control Number (035a)', 'Material Type', 'Language Code',
                    'Language Of Cataloging', 'Publisher', 'Publication Date',
                    'Edition Simplified (Num)', 'Edition Simplified (Text)'],
            keep=False)
    ]
    df_multiples_for_review = df_multiples[
        ~df_multiples.duplicated(
            subset=['OCLC Control Number (035a)', 'Material Type', 'Language Code',
                    'Language Of Cataloging', 'Publisher', 'Publication Date',
                    'Edition Simplified (Num)', 'Edition Simplified (Text)'],
            keep=False)
    ]

    # Step 3: Save Excel
    excel_file_path = BASE_DIR / "output/verified_duplicates.xlsx"
    with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
        df_multiples_ready_for_step_2.to_excel(writer, index=False, sheet_name='ready for step 2')
        df_multiples_for_review.to_excel(writer, index=False, sheet_name='ready for review')
        df_singles.to_excel(writer, index=False, sheet_name='no duplicate')
    print(f" Excel file saved at: {excel_file_path}")

    # Step 4: Update Preferred/Merge
    updated_excel_file_path = update_preferred_merge_column(excel_file_path, "ready for step 2")

    # Step 5: Map to final CSV
    df = pd.read_excel(updated_excel_file_path)
    headers = [
        "Group Number", "MMSID", "Identifier", "Records In Group", "Operation",
        "Material Type", "Brief Level", "Resource Type", "Held By", "Title"
    ]
    mapped_df = pd.DataFrame(columns=headers)
    mapped_df["Group Number"] = df.groupby('OCLC Control Number (035a)').ngroup() + 1
    mapped_df["MMSID"] = df["Network Id"]
    mapped_df["Identifier"] = df["OCLC Control Number (035a)"]
    mapped_df["Records In Group"] = df.groupby('OCLC Control Number (035a)')['OCLC Control Number (035a)'].transform('count')
    mapped_df["Operation"] = df["Preferred_Merge"]
    mapped_df["Material Type"] = df["Material Type"]
    mapped_df["Brief Level"] = df["Brief Level"]
    mapped_df["Resource Type"] = df["Resource Type"]
    mapped_df["Held By"] = df["Held By"]
    mapped_df["Title"] = df["Title"]

    for header in headers:
        if header not in mapped_df.columns:
            mapped_df[header] = ""

    merge_csv_path = BASE_DIR / "output/merge-combine.csv"
    mapped_df.to_csv(merge_csv_path, index=False)
    print(f" Final CSV created at: {merge_csv_path}")
