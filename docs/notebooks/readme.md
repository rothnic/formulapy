# Adding IPython Notebooks to Sphinx Docs
1. Place IPython notebook in this directory
2. Create a RST file with the same name as the notebook (convention, doesn't have to be the same)
3. Use the ".. notebook:: thenameofyournotebook.ipynb" directive to tell Sphinx to execute and insert the notebook
4. Reference thenameofyournotebook.rst file from some higher level Sphinx RST file