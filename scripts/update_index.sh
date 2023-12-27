#!/usr/bin/env bash
set -euo pipefail

index_file=$1
sed -i '/{ #recent }/q' $index_file
echo "" >> $index_file
echo "|Cocktail| Recency (lower is newer) { data-sort-method='number' } |" >> $index_file
echo "|------|-----------|" >> $index_file
all_files="$(ls $2/*md)"
for file in ${all_files[*]}; do
    if [[ $file != *"index.md" ]]; then
        recipe_name="$(grep -h '^# ' $file)"
        # capture only the number
        order="$(grep -Po '(?<=order: )([0-9]+)' $file)"
        file=${file/docs\///}
        echo "|[${recipe_name/\# /}](${file/.md//})|$order|" >> $index_file
    fi
done
