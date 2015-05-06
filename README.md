# Managers Review Processor

## Requirements

### Python

[Download](https://www.python.org/downloads/) and install the latest
Python 3 release (currently this program is not compatible with Python
2) for your operating system. If on Windows be sure to select the
option "Add python.exe to the search path" so that you don't need to
specify the full path to the python executable when running it from
the command line.

### This program

Download the zip archive by clicking the *Download ZIP* button to the
right. Unpack the archive into a convenient directory, navigate to the
directory containing `manager_review.py` at the command
prompt. (Windows users, open a command prompt, type `cd` followed by a
space, and then drag and drop the folder name containing
`manager_review.py` into the command window and press `Enter`)

### Experimental GUI

If you aren't feeling up for working from the command line try the
experimental gui by running `manager_review_gui.py`. Yes, I know it
looks really bad, if you want to make it pretty feel free to submit a
pull request. Note, this is not a full GUI implementation, the bulk of
the program still runs from the command prompt, the GUI is just used
to set the input and gradebook files.

The GUI uses Tcl which you will have to install for your respective
operating system before running `manager_review_gui.py`. I have tested
the [ActiveTcl](http://www.activestate.com/activetcl) distribution of
Tcl on Windows.

## Windows users

If you added *python.exe* to the search path when installing Python
you should be able to run the following command (`>` denotes the
command prompt, don't type that):

```
> python.exe manager_review.py
```

If all is working you should see the help text for the program

```
usage: manager_review.py [-h] [--interactive] [--gradebook GRADEBOOK]
                         [--name NAME] [--aliases ALIASES] [--comments]
                         [--submission-points SUBMISSION_POINTS]
                         input_file
```

If you did not add *python.exe* to the search path when you installed
Python you will have to specify the full path to the python executable
when running python programs for the command line. For the latest
released of Python 3 this should be `C:\Python34\python.exe`. If the
above command results in an error replace `python.exe` with the
`C:\Python34\python.exe` and try again.

## Usage

In the following example `assessment.csv` is the csv exported
assesment data downloaded from Scholar Tests&Quizes and
`gradebook.csv` is the exported gradebook with no structure, just
grades. See the
[Exporting data from Scholar](#exporting-data-from-scholar) section
for instructions.

```
> python manager_review.py -i -g gradebook.csv Assessment-Project#2_Team_Eval.csv
```

To record and include comments

```
> python manager_review.py -ic -g gradebook.csv Assessment-Project#2_Team_Eval.csv
```

If reviewers made typoes or missspellings when entering reviewee names
you will be prompted for a name correction.  These correctons will be saved in a file called `alieases.txt` in the current directory, you can specify an alternate file using the `--aliases` command option.

```
> python3 manager_review.py -h
```

Will display all available options

## Exporting data from Scholar

### Gradebook

1. Navigate to *Gradebook* on your Scholar site
2. From the 'Import/Export' menu select 'Export'
3. Change the *Export Format* to "No-Struture Gradebook (Only Grades)
4. If you are using a common scholar site change *Sections* to select your sections only
5. Change *Export As* to "CSV (.csv)"
6. Click *Export*

### Tests & Quizzes

1. Navigate to *Tests & Quizzes* on your Scholar site
2. Select *Published Copies*
3. From the *Action* drop down to the left of the quiz for the manager review select "Scores"
4. Once the scores page loads click the *Export* link and then the *Export* button
5. Open the downloaded file in your spreadsheet program of choice and save as a CSV file.
