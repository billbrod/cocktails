#!/usr/bin/env python3

import os
import json
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

<!-- order: {order} -->

{recipe}

- Scale up to
{{ #scale }}

{directions}

## Notes

{notes}

"""


def create_table(recipe: List[List[str]]) -> str:
    """Create 3-column table from recipe.
    """
    tbl = ["|Units | Measure | Ingredient | Price |"]
    tbl.append("|-----|------|-----------|-----|")
    non_oz_ingredients = False
    for r in recipe:
        while len(r) < 3:
            r.append('')
        classes = []
        if r[0]:
            classes.append('.ingredient-num')
        if r[1] and r[1] == 'oz':
            classes.append('.ingredient-oz')
        elif r[1] and r[1] != 'Garnish':
            non_oz_ingredients = True
        if r[2]:
            # any additional columns are comments, which we want separated within an <a>
            # tag
            r[2] += "<a>" + ' '.join(r[3:]) + "</a>"
            r[2] += ' {.ingredient}'
        if len(classes) > 0:
            classes = ' '.join(classes)
            r[0] += f' {{ {classes} }}'
        # put an empty string before and after the recipe, so the '|'.join adds
        # a pip before and after the rest of the text
        tbl.append('|'.join(['']+r[:3]+['0 {.ingredient-price}','']))
    tbl.append("|0 {#total_vol_oz}|oz|**TOTAL VOLUME (oz ingredients only)**| ")
    if non_oz_ingredients:
        tbl[-1] += "|"
        tbl.append("|0 {#total_vol_all}|oz|**TOTAL VOLUME (oz + other ingredients)**| 0 {#total-price} |")
    else:
        tbl[-1] += " 0 {#total-price} |"
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
        if k == 'tags' and v:
            # make a single list of tags
            tags = []
            # for each column of tags
            for v_ in v:
                # split by comma
                for i in v_.split(','):
                    tags.append(':'.join([i_.strip() for i_ in i.split(':')]))
            v = '\n- '.join(tags)
            v = '---\ntags:\n- ' + v + "\n---"
        elif k in ['directions', 'notes']:
            # if there's a single newline, replace it with a double newline
            v = [re.sub(r"(.)\n(.)", r'\1\n\n\2', v_) for v_ in v]
            v = '\n\n'.join(v)
        else:
            v = '\n\n'.join(v)
        recipe[k] = v
    # the first column is empty
    recipe['recipe'] = create_table([v[1:] for v in vals[6:]])
    return recipe


@click.command()
@click.argument('spreadsheet_id')
@click.argument("credentials_path")
@click.argument("output_dir")
@click.option("--sheets_to_skip", "-s", multiple=True)
@click.option("--sheets_to_leave", "-l", multiple=True)
@click.option("--dictionary_sheets", "-d", multiple=True)
def main(spreadsheet_id: str, credentials_path: str, output_dir: str,
         sheets_to_skip: List[str] = ['Recipe template', 'Instructions'],
         sheets_to_leave: List[str] = ['Simple Syrups'],
         dictionary_sheets: List[str] = ['Ingredients', 'Prices']):
    """Write all sheets from private Google spreadsheet as markdown recipes.

    - Each sheet will be written to a separate .md file in output_dir
      (which may exist or not).

    - Sheets whose titles are found in `sheets_to_skip` will not be written to
      .md files

    - Sheets whose titles are found in `sheets_to_leave` will not be parsed as
      recipes, and will just be written to .md files as is.

    - Sheets whose titles are found in `dictionary_sheets` will not be parsed
      as recipes, and will just be written to .json files as is.

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
        # so that we start at 1
        i = i - len(sheets_to_skip) - len(sheets_to_leave) - len(dictionary_sheets) + 1
        ext = 'md'
        write_func = lambda f, rec: f.write(rec)
        if t in sheets_to_skip:
            continue
        elif t in sheets_to_leave:
            recipe = [' '.join(v) for v in c['values']]
            # if there's a single newline, replace it with a double newline
            recipe = [re.sub(r"(.)\n(.)", r'\1\n\n\2', v) for v in recipe]
            recipe = '\n\n'.join(recipe)
        elif t in dictionary_sheets:
            ext = 'json'
            recipe = {}
            for v in c['values']:
                recipe[v[0].lower().strip()] = [v_.lower().strip() for v_ in v[1:]]
            write_func = lambda f, rec: json.dump(rec, f)
        else:
            recipe = json_from_sheet(c, t)
            recipe['order'] = i
            recipe = TEMPLATE.format(**recipe)
        slug = download_csv.sanitize_title(t)
        with open(op.join(output_dir, f'{slug}.{ext}'), 'w') as f:
            write_func(f, recipe)


if __name__ == '__main__':
    main()
