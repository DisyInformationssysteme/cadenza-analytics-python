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
BRANCHES=$(git branch -r --sort=v:refname | grep -P '^  origin/v[0-9.]+\.x$' | sed 's/origin\///' | sed 's/^[[:space:]]*//g')

# Add outer page with version picker
cp ./docs/index.html  ./${OUTPUT_DIR}/

# Loop through matching branches
for BRANCH in $BRANCHES; do
  echo "Processing branch: $BRANCH"
  
  # Checkout the version branch
  git switch "$BRANCH"

  # Create directory to store docs for this branch
  BRANCH_DIR="$OUTPUT_DIR/$BRANCH"
  mkdir -p "$BRANCH_DIR"

  # Store release version of latest non-prerelease tag matching Cadenza version of current branch
  echo "Determining last release tag..."
  #LAST_RELEASE_VERSION=$(git tag --sort=-v:refname -l | grep -m1 -P "${BRANCH:1:-1}[0-9]+$")  # does not work for v10.2.x
  LAST_RELEASE_VERSION=$(git tag --merged "${BRANCH}" --sort=-v:refname | grep -m1 -P "[0-9]+\.[0-9]+\.[0-9]+$")
  echo $LAST_RELEASE_VERSION

  # Install cadenzaanalytics from this branch
  pip install --upgrade --force-reinstall .

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
  sed -i "s/{{version}}/${LAST_RELEASE_VERSION}/" ./${BRANCH_DIR}/cadenzaanalytics.html

  # Patch links with target "_top" so that they won't open in inner page, @ as delimiter for sed, since URL contains slashes
  # logo links
  sed -i 's@<a href="'$LOGO_LINK'">@<a href="'$LOGO_LINK'" target="_top">@' ./${BRANCH_DIR}/cadenzaanalytics.html
  # github content is not allowed to be embedded into iframes
  sed -i 's@<a href="https://github.com/DisyInformationssysteme/cadenza-analytics-python">@<a href="https://github.com/DisyInformationssysteme/cadenza-analytics-python" target="_top">@' ./${BRANCH_DIR}/cadenzaanalytics.html
  # pypi content is not allowed to be embedded into iframes
  sed -i 's@<a href="https://pypi.org/project/cadenzaanalytics/">@<a href="https://pypi.org/project/cadenzaanalytics/" target="_top">@' ./${BRANCH_DIR}/cadenzaanalytics.html

  # Add branch to version picker of outer page (will result in reverse order)
  sed -i "/<!-- Branch options will be populated here -->/a <option value="${BRANCH}">${BRANCH}</option>" ./${OUTPUT_DIR}/index.html

  echo "Documentation for branch $BRANCH saved to $BRANCH_DIR"
done

echo "All branches processed."

# switch back to original branch
git switch $ORIGINAL_BRANCH
