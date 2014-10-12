.. Sphinx IPython Notebook readme

Adding IPython Notebooks to Sphinx Docs
---------------------------------------

#. Place IPython notebook in this directory
#. Create a RST file with the same name as the notebook (convention, doesn't have to be the same)
#. Use the ".. notebook:: thenameofyournotebook.ipynb" directive to tell Sphinx to execute and insert the notebook
#. Reference thenameofyournotebook.rst file from some higher level Sphinx RST file
