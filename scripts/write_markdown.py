#!/usr/bin/env python3

import os
import re
import os.path as op
import click
import pandas as pd
from typing import Dict, List
from googleapiclient.discovery import Resource
import download_csv

TEMPLATE = """{tags}
# {title}

## Description

{description}

## Recipe

- Drinks: 1
{{ #serves }}

{recipe}

{directions}

## Notes

{notes}

"""


def create_table(recipe: List[List[str]]) -> str:
    """Create 3-column table from recipe.
    """
    tbl = ["|Units | Measure | Ingredient |"]
    tbl.append("|-----|------|-----------|")
    for r in recipe:
        while len(r) < 3:
            r.append('')
        if r[0]:
            r[0] += ' {.ingredient-num} '
        # put an empty string before and after the recipe, so the '|'.join adds
        # a pip before and after the rest of the text
        tbl.append('|'.join(['']+r+['']))
    return '\n'.join(tbl)


def json_from_sheet(returned: Dict, title: str) -> Dict:
    """Turn returned value into dict that we can write to md
    """
    vals = returned['values']
    recipe = {}
    for v in vals[:5]:
        k = v[0]
        try:
            v = v[1:]
        except IndexError:
            # then there's no values, it's empty
            v = []
        if k == 'tags':
            # make a single list of tags
            v = [v_ for i in v for v_ in i.split(',')]
            v = '\n-'.join(v)
            if len(v) >= 1:
                v = '---\ntags:\n-' + v + "\n---"
        elif k in ['directions', 'notes']:
            # if there's a single newline, add a dash to the beginning of the
            # line
            v = [re.sub(r"(.)\n(.)", r'\1\n- \2', v_) for v_ in v]
            v = '- ' + '\n- '.join(v)
        else:
            v = '\n'.join(v)
        recipe[k] = v
    # the first column is empty
    recipe['recipe'] = create_table([v[1:] for v in vals[6:]])
    return recipe


def write_markdown(recipe: Dict, filename: str):
    """Write markdown file for single processed recipe Dict.
    """
    rec = TEMPLATE.format(**recipe)
    with open(filename, 'w') as f:
        f.write(rec)


@click.command()
@click.argument('spreadsheet_id')
@click.argument("credentials_path")
@click.argument("output_dir")
@click.argument("sheets_to_skip", nargs=-1)
def main(spreadsheet_id: str, credentials_path: str, output_dir: str,
         sheets_to_skip: List[str] = ['Recipe template']):
    """Write all sheets from private Google spreadsheet as markdown recipes.

    - Each sheet will be written to a separate .md file in output_dir
      (which may exist or not).

    - Sheets whose titles are found in `sheets_to_skip` will not be written to
      .md files

    - credentials_path is the path to the json giving credentials to a service
      account with read access to the spreadsheet (see first two steps
      https://github.com/marketplace/actions/gsheet-action#setup-of-credentials
      for how to create the credentials and give them access).

    - spreadsheet_id can be found in the url of the google spreadsheet, between
      `/d/` and `/edit`

    """
    os.makedirs(output_dir, exist_ok=True)
    spreadsheet_resource = download_csv.connect_to_sheets(credentials_path)
    sheet_titles = download_csv.get_all_sheet_names(spreadsheet_resource, spreadsheet_id)
    contents = download_csv.get_all_sheets_contents(spreadsheet_resource, spreadsheet_id,
                                                    sheet_titles)
    for i, (t, c) in enumerate(zip(sheet_titles, contents)):
        if t in sheets_to_skip:
            continue
        recipe = json_from_sheet(c, t)
        slug = download_csv.sanitize_title(t)
        write_markdown(recipe, op.join(output_dir, f'{i:03d}_{slug}.md'))


if __name__ == '__main__':
    main()
