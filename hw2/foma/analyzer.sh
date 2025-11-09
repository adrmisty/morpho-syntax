#!/bin/bash

INPUT_FILE="input-foma.txt"
OUTPUT_FILE="output-foma.txt"
FOMA_FILE="el.foma"
TEMP_FILE=$(mktemp)

if [ ! -f "$FOMA_FILE" ]; then
  echo "> Error: Foma file '$FOMA_FILE' not found!"
  exit 1
fi

# compile foma
foma -e "source $FOMA_FILE" -e "save stack el.bin" -e "quit"

# analyze each word
while read -r line; do
  for word in $line; do
    echo "$word" | flookup el.bin >> "$TEMP_FILE"    
  done
done < "$INPUT_FILE"

mv "$TEMP_FILE" "$OUTPUT_FILE"
rm el.bin

echo "> Analysis complete. Results written to '$OUTPUT_FILE'."