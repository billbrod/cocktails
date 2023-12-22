#!/usr/bin/env python3

from google.oauth2 import service_account
import googleapiclient.discovery
from googleapiclient.discovery import Resource
from typing import List, Dict
import pandas as pd
import click
import time
import os
import os.path as op


def connect_to_sheets(credentials_path: str) -> Resource:
    """Connect to the Google Sheets service

    Accepts the path to the json file containing the service account
    credentials and returns the spreadsheets resource

    """
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    return googleapiclient.discovery.build('sheets', 'v4',
                                           credentials=credentials).spreadsheets()


def get_all_sheet_names(spreadsheet_resource: Resource,
                        spreadsheet_id: str) -> List[str]:
    """Get the names of all sheets in the cocktails spreadsheet
    """
    sheet_metadata = spreadsheet_resource.get(spreadsheetId=spreadsheet_id).execute()
    titles = [s['properties']['title'] for s in sheet_metadata['sheets']]
    return titles


def get_all_sheets_contents(spreadsheet_resource: Resource,
                            spreadsheet_id: str, titles: List[str]) -> List[Dict]:
    """Get contents from all sheets

    This returns a list of dictionaries, each of which is formatted like the
    return of the get command
    (https://developers.google.com/sheets/api/guides/values#python_4). Should
    be interpreted as follows:

    >>> res = get_all_sheet_contents(...)
    >>> df = pd.DataFrame(res[0]['values'])

    """
    res = spreadsheet_resource.values().batchGet(spreadsheetId=spreadsheet_id,
                                                 ranges=titles).execute()
    return res['valueRanges']


def sanitize_title(title: str) -> str:
    """Sanitize title so we can use it as a filename

    - Convert to lowercase
    - Convert to ascii and back (to remove accents)
    - Convert spaces to underscores
    - Remove parentheses, ampersands, and single quotes/apostrophes

    """
    to_replace = [(' ', '_'), ('(', ''), (')', ''), ('&', ''), ("'", '')]
    # make title lowercase and ascii (throw away accents)
    title = title.lower().encode('ascii', 'ignore').decode('utf-8')
    for i, j in to_replace:
        title = title.replace(i, j)
    return title



@click.command()
@click.argument('spreadsheet_id')
@click.argument("credentials_path")
@click.argument("output_dir")
def main(spreadsheet_id: str, credentials_path: str, output_dir: str):
    """Download all sheets from a private Google spreadsheet

    - Each sheet will be downloaded as a separate .csv file in output_dir
      (which may exist or not).

    - credentials_path is the path to the json giving credentials to a service
      account with read access to the spreadsheet (see first two steps
      https://github.com/marketplace/actions/gsheet-action#setup-of-credentials
      for how to create the credentials and give them access).

    - spreadsheet_id can be found in the url of the google spreadsheet, between
      `/d/` and `/edit`

    """
    os.makedirs(output_dir, exist_ok=True)
    spreadsheet_resource = connect_to_sheets(credentials_path)
    sheet_titles = get_all_sheet_names(spreadsheet_resource, spreadsheet_id)
    contents = get_all_sheets_contents(spreadsheet_resource, spreadsheet_id, sheet_titles)
    for i, (t, c) in enumerate(zip(sheet_titles, contents)):
        # make title lowercase and ascii (throw away accents)
        t = sanitize_title(t)
        try:
            df = pd.DataFrame(c['values'])
        except KeyError:
            df = pd.DataFrame([])
        filename = op.join(output_dir, f'{i:02d}_{t}.csv')
        df.to_csv(filename, index=False)


if __name__ == '__main__':
    main()
