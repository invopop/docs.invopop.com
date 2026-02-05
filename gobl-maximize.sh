#!/bin/bash

# Script to build .min.mdx files using gobl
# Finds all .min.mdx files in snippets/, extracts JSON, builds with gobl, and outputs to .mdx files

SNIPPETS_DIR="snippets"
ERRORS=0
PROCESSED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Building .min.mdx files with gobl..."
echo ""

# Find all .min.mdx files and process them
while IFS= read -r min_file; do
    # Get the output filename by removing .min from the path
    output_file="${min_file%.min.mdx}.mdx"
    
    echo -n "Processing: $min_file ... "
    
    # Extract JSON from the MDX file
    # Look for JSON code block (```json ... ```)
    # First, get the title from the opening line
    title_line=$(grep -m 1 '^```json' "$min_file" || true)
    if [ -z "$title_line" ]; then
        echo -e "${YELLOW}WARNING: No JSON code block found${NC}"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # Set the title

    title="Built version"
    
    # Extract JSON content (between code block markers, excluding the markers themselves)
    json_content=$(awk '/^```json/,/^```$/ {if (!/^```/) print}' "$min_file")
    
    if [ -z "$json_content" ]; then
        echo -e "${YELLOW}WARNING: Empty JSON content${NC}"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # Create a temporary file for the JSON
    temp_json=$(mktemp)
    echo "$json_content" > "$temp_json"
    
    # Build with gobl (capture both stdout and stderr)
    gobl_output=$(gobl build -i "$temp_json" 2>&1)
    gobl_exit_code=$?
    
    if [ $gobl_exit_code -eq 0 ]; then
        # Create the output MDX file with the built JSON
        {
            echo "\`\`\`json $title"
            echo "$gobl_output"
            echo "\`\`\`"
        } > "$output_file"
        
        echo -e "${GREEN}✓${NC} -> $output_file"
        PROCESSED=$((PROCESSED + 1))
    else
        echo -e "${RED}✗ ERROR${NC}"
        echo "  Error details:"
        echo "$gobl_output" | sed 's/^/  /'
        ERRORS=$((ERRORS + 1))
    fi
    
    # Clean up
    rm -f "$temp_json"
done < <(find "$SNIPPETS_DIR" -name "*.min.mdx" -type f)

echo ""
echo "========================================="
echo "Processed: $PROCESSED files"
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Errors: $ERRORS files${NC}"
    exit 1
else
    echo -e "${GREEN}All files built successfully!${NC}"
    exit 0
fi
