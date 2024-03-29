# cocktails

Static site for viewing cocktails

TODO:
- simple syrup and recipe pages, ignore others
- scale up, price out
- create "events pages" with certain recipes: I think just have events in tags
- have page mapping generic spirits to brands
- allow recipes to specify generic spirits or lists of spirits (with default)
- public and private recipes (with tags)

Comments: can use [utterances](https://utteranc.es/), but any of the "bot
automatically creates issue" options for how to match issue and page will have
the bot post the link to the specific page, which defeats the purpose of having
the site behind the password. works fine if we create issues, but then if issue
doesn't exist, the comment thing just doesn't load, so we'd need to manually
create issues for every page. could probably do that using github api but ...
doesn't seem ideal.

looking on the issues, it looks like it's possible to get it working with a
private repo, but then the bot and everyone who wants to post needs to be added
as contributors (so one extra step involved).

## To use

This repo has several python scripts which are used to grab data from Sheets and
format it before building the website. To use, install dependencies found in
`scripts/requirements.txt`.

`download_csv.py` and `convert_old_csv.py` are only used to get the data into
the proper format and don't need to be run regularly, while `write_markdown.py`
is used to get the data ready for the website and so needs to be run everytime
the site is built.

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
    `download_csv.py`!
  - spreadsheet_id can be found in the url of the google spreadsheet, between
    `/d/` and `/edit`
  - For how to create the credentials file of a service account and give them
    access, see first two steps of:
    https://github.com/marketplace/actions/gsheet-action#setup-of-credentials
- `scripts/write_markdown.py`: download all sheets from Google Spreadsheet as
  markdown files in a single directory. Unlike `download_csv.py`, this makes
  assumptions about how they're formatted.
  - This accepts the spreadsheet ID and path to the credentials json file as
    inputs. The spreadsheet ID should be the same as from `convet_old_csv.py`
  - spreadsheet_id can be found in the url of the google spreadsheet, between
    `/d/` and `/edit`
  - For how to create the credentials file of a service account and give them
    access, see first two steps of:
    https://github.com/marketplace/actions/gsheet-action#setup-of-credentials
