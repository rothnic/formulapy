.. Sphinx IPython Notebook readme

Working with IPython Notebooks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Running IPython Notebooks
*************************

#. Open command line
#. ``CD`` to the directory where the notebook exists
#. Execute ``ipython notebook``
#. Click on the notebook when the browser has loaded


Adding IPython Notebooks to Sphinx Docs
***************************************

#. Place IPython notebook in the docs/notebooks directory
#. Create a RST file with the same name as the notebook (convention, doesn't have to be the same)
#. Use the ``.. notebook:: thenameofyournotebook.ipynb`` rst directive within the notebook's rst file to tell Sphinx to execute and insert the notebook
#. Reference thenameofyournotebook.rst file from some higher level Sphinx RST file

