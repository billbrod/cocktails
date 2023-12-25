# cocktails

Static site for viewing cocktails

TODO:
- simple syrup and recipe pages, ignore others
- scale up, price out
- create "events pages" with certain recipes
- have page mapping generic spirits to brands
- allow recipes to specify generic spirits or lists of spirits (with default)
- public and private recipes (with tags)


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
- `scripts/convert_old_csv.py`: convert old csvs (as created by
  `download_csv.py`) into new format and upload them to a new spreadsheet.
  - Getting this to run on the outputs of the above required some manual
    editing.
  - Each csv file has a `sheet_title` field; we will clear any sheet found with
    this name in the target spreadsheet and then write the new contents.
  - This accepts the spreadsheet ID and path to the credentials json file as
    inputs. Note that the spreadsheet ID should be to a different sheet than
    above!
  - spreadsheet_id can be found in the url of the google spreadsheet, between
    `/d/` and `/edit`
  - For how to create the credentials file of a service account and give them
    access, see first two steps of:
    https://github.com/marketplace/actions/gsheet-action#setup-of-credentials
