# Docs

## Quickstart

To run build/run the docs locally, do the following in this `docs` folder:

 - Install docs dependencies: `pip install -r requirements.txt`
 - run `make html` to generate html files
 - in `_build/html` folder, run `python3 -m http.server`


## How does this work?

The documentation is built using Sphinx, using the Read The Docs theme, and using the Sphinx autodoc extension for the API page. It's deployed to github pages via a [github action](../.github/workflows/documentation.yaml).
