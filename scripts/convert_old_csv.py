#!/usr/bin/env python3

import pandas as pd
from typing import List
from googleapiclient.discovery import Resource
from download_csv import connect_to_sheets


def convert_series_to_string(series: pd.Series) -> str:
    """Convert Series to string."""
    return "\n".join(series.iloc[1:].values)


def format_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Get info out of old-format csvs, into something more usable
    """
    sheet_title = df.iloc[0, 0]
    title = df.iloc[4, 0]
    description = df.iloc[5, 0]
    # Find line in first column that says "Total Ounces", as this marks the end
    # of the recipe
    first_col = df.iloc[:, 0].values.tolist()
    total_oz_line = first_col.index('Total Ounces')
    # grab the recipe and drop any empty lines
    recipe = df.iloc[7:total_oz_line, 2:5].dropna(0, 'all')
    # Find where directions start
    directions_line = first_col.index('Directions')
    # Find where notes start
    try:
        notes_line = first_col.index('NOTES:')
    except ValueError:
        # then there is no NOTES: line, so go to the end
        notes_line = -1
    directions = df.iloc[directions_line:notes_line, 0].dropna(how='all')
    if notes_line != -1:
        notes = df.iloc[notes_line:, 0].dropna(how='all')
    else:
        notes = ''
    data = pd.Series({'sheet_title': sheet_title, 'title': title,
                      'description': description,
                      'directions': convert_series_to_string(directions),
                      'notes': convert_series_to_string(notes),
                      'recipe': recipe.fillna('').values})
    return data


def create_new_sheets(titles: List[str], spreadsheet_resource: Resource,
                      spreadsheet_id: str):
    """Create new sheet on specified spreadsheet

    Pass a list of titles, and create a new sheet for each of them.

    """
    if len(titles[0]) <= 1:
        raise TypeError("titles should be a list of strings")
    add_sheet = [{'addSheet': {'properties': {"title": t}}
                  for t in titles}]
    spreadsheet_resource.batchUpdate(spreadsheetId=spreadsheet_id,
                                     body={"requests": add_sheet},
                                     ).execute()


def write_recipes_to_sheets(dfs: pd.Series, spreadsheet_resource: Resource,
                            spreadsheet_id: str):
    """Write recipes to already existing sheets
    """
    sheet_titles = [df.pop('sheet_title') for df in dfs]
    recipes = [df.pop('recipe') for df in dfs]
    indices = [{"range": f"{title}!A1",
                "values": [df.index.to_list() + ['recipe']],
                "majorDimension": "COLUMNS"}
               for df, title in zip(dfs, sheet_titles)]
    metadata = [{"range": f"{title}!B1",
                "values": [df.to_list()],
                "majorDimension": "COLUMNS"}
               for df, title in zip(dfs, sheet_titles)]
    # do each column of recipes separately
    recipes_0 = [{"range": f"{title}!B{len(df)+1}",
                "values": [rec[:, 0].tolist()],
                  "majorDimension": "COLUMNS"}
                 for df, title, rec in zip(dfs, sheet_titles, recipes)]
    recipes_1 = [{"range": f"{title}!C{len(df)+1}",
                "values": [rec[:, 1].tolist()],
                  "majorDimension": "COLUMNS"}
                 for df, title, rec in zip(dfs, sheet_titles, recipes)]
    recipes_2 = [{"range": f"{title}!D{len(df)+1}",
                "values": [rec[:, 2].tolist()],
                  "majorDimension": "COLUMNS"}
                 for df, title, rec in zip(dfs, sheet_titles, recipes)]
    body = {
        "valueInputOption": "RAW",
        "data": indices+metadata+recipes_0+recipes_1+recipes_2,
    }
    spreadsheet_resource.values().batchUpdate(spreadsheetId=spreadsheet_id,
                                              body=body,
                                              ).execute()


def main(spreadsheet_id: str, credentials_path: str):
    spreadsheet_resource = connect_to_sheets(credentials_path)
