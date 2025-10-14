#!/bin/bash

# Fail on simple errors, so that pipeline / job fails
set -e

# Define base directory where docs will be generated
OUTPUT_DIR="docs_output"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Save current branch name
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Get all remote branches that match the pattern v[0-9.]+\.x (e.g., v10.4.x, v11.1.x, etc.)
BRANCHES=$(git branch -r --sort=v:refname | grep -P '^  origin/v[0-9.]+\.x$' | sed 's/origin\///')

# Add outer page with version picker
cp ./docs/index.html  ./${OUTPUT_DIR}/

# Loop through matching branches
for BRANCH in $BRANCHES; do
  echo "Processing branch: $BRANCH"
  
  # Checkout the version branch
  git switch "$BRANCH"

  # TODO checkout latest tag instead of HEAD? Can I filter this to the current branch?
  # git tag --sort=-v:refname
  # git describe --tags --abbrev=0

  # Create directory to store docs for this branch
  BRANCH_DIR="$OUTPUT_DIR/$BRANCH"
  mkdir -p "$BRANCH_DIR"

  # Store release version
  RELEASE_VERSION=$(poetry version patch --dry-run -s)
  # TODO double check whether branch (TAG?) name and version in poetry are same?? But not for 10.2.x

  # Run pdoc to generate documentation
  LOGO_LINK="https://www.disy.net/en/products/disy-cadenza/"
  pdoc --favicon https://www.disy.net/favicon.ico \
       --logo https://www.disy.net/typo3conf/ext/contentelements/Resources/Public/dist/img/logo-disy.svg \
       --logo-link "$LOGO_LINK" \
       --output-dir "$BRANCH_DIR" \
       --no-show-source src/cadenzaanalytics 

  # Copy image assets to target folder
  cp ./docs/*.png ./${BRANCH_DIR}/

  # Write version into generated docs
  sed -i "s/{{version}}/${RELEASE_VERSION}/" ./${BRANCH_DIR}/cadenzaanalytics.html

  # Patch logo links with target "_top" so that they won't open in outer page, @ as delimiter for sed, since URL contains slashes
  sed -i 's@<a href="'$LOGO_LINK'">@<a href="'$LOGO_LINK'" target="_top">@' ./${BRANCH_DIR}/cadenzaanalytics.html

  # Add branch to version picker of outer page (will result in reverse order)
  sed -i "/<!-- Branch options will be populated here -->/a <option value="${BRANCH}">${BRANCH}</option>" ./${OUTPUT_DIR}/index.html

  echo "Documentation for branch $BRANCH saved to $BRANCH_DIR"
done

echo "All branches processed."

# switch back to original branch
git switch $ORIGINAL_BRANCH
