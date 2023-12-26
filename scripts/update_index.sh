#!/usr/bin/env bash
set -euo pipefail

sed -i '/{ #recent }/q' docs/cocktails/index.md
echo "" >> docs/cocktails/index.md
echo "|Cocktail| Recency (lower is newer) { data-sort-method='number' } |" >> docs/cocktails/index.md
echo "|------|-----------|" >> docs/cocktails/index.md
all_files="$(ls $1/*md)"
for file in ${all_files[*]}; do
    if [[ $file != *"index.md" ]]; then
        recipe_name="$(grep -h '^# ' $file)"
        # capture only the number
        order="$(grep -Po '(?<=order: )([0-9]+)' $file)"
        file=${file/\/\//\//}
        echo "|[${recipe_name/\# /}](${file/.md//})|$order|" >> docs/cocktails/index.md
    fi
done
