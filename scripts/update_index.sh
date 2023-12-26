#!/usr/bin/env bash
set -euo pipefail

sed -i '/{ #recent }/q' docs/cocktails/index.md
echo "" >> docs/index.md
echo "|Cocktail| Recency (lower is newer) { data-sort-method='number' } |" >> docs/index.md
echo "|------|-----------|" >> docs/index.md
all_files="$(ls docs/cocktails/*md)"
for file in ${all_files[*]}; do
    if [[ $file != *"index.md" ]]; then
        recipe_name="$(grep -h '^# ' $file)"
        # capture only the number
        order="$(grep -Po '(?<=order: )([0-9]+)' $file)"
        file=${file/docs\///}
        echo "|[${recipe_name/\# /}](${file/.md//})|$order|" >> docs/index.md
    fi
done
