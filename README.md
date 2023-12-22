# cocktails

Static site for viewing cocktails

## To use

This repo has several python scripts which are used to grab data from Sheets and
format it before building the website. To use, install dependencies found in
`scripts/requirements.txt`.

- `scripts/download_csv.py`: downloads all sheets from specified Google
  Spreadsheet as csvs in a single directory.
    - This accepts the spreadsheet ID and path to the credentials json file as
      inputs
    - spreadsheet_id can be found in the url of the google spreadsheet, between
      `/d/` and `/edit`
    - For how to create the credentials file of a service account and give them
      access, see first two steps of:
      https://github.com/marketplace/actions/gsheet-action#setup-of-credentials
