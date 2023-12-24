#!/usr/bin/env python3

import pandas as pd
from typing import Dict, List
from googleapiclient.discovery import Resource
from download_csv import connect_to_sheets, sanitize_title

def json_from_sheet(returned: List[Dict], titles: List[str]) -> List[Dict]:
    """Turn the list of returned values into list of dicts that we can write to md
    """
    recipes = []
    for vals, title in zip(returned, titles):
        vals = vals['values']
        recipe = {v[0]: v[1] for v in vals[:4]}
        recipe['filename'] = sanitize_title(title)
        recipe['recipe'] = [' '.join(v[1:]) for v in vals[5:]]
        recipes.append(recipe)
    return recipes
