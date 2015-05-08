# Manager's Review Processor

## Overview

1. [Download](https://www.python.org/downloads/) and install the latest stable release of Python 3 (on windows be sure to select the 64 bit installer)
1. [Export files from Scholar](#exporting-data-from-scholar)
    1. Export your manager's review scores, then save as *Unicode
       Text*
    1. Under gradebook be sure to create a grade item for the
       *Manager's Review 2*, if you haven't already. Make a not of the
       exact name you give this item, you will need to input it later.
    1. Export your gradebook, select "No-structure (grades only)" and "CSV"
        1. If you are on the common site, select only your section to export
1. [Download the zip archive](https://github.com/hazybluedot/manager_review/archive/master.zip)
   of this repository by clicking the button on the right side of the
   page
1. Extract the downloaded archive, open the folder that was created and double click `manager_review_gui.py`
1. For the input file click 'Browse' and select "\*.txt" as the file
   type and select the Unicode Text file you saved containing the
   manager review responses. On the GUI screen change the encoding
   type to *UTF-16* and the delimiter to *\<tab>*.
1. For the gradebook file click 'Browse' and select the CSV file containing your gradebook export
1. All subsequent input will be done through the command
   window. During data entry you may press `Ctrl+C` and then `Enter`
   to cancel and save any changes so far.
   1. If the program can't match a reveiwee's name to one in the
      gradebook (i.e. a reviewer used a nick name or made a typo) you
      will see a prompt like

       ````
       In section 2:00 Tu/Th, Team 1 who is Joe Smith?
       ````

       Simply type in the full name, first then last, of the person
       and press `Enter` to continue. See
       [Name association](#name-association) for more details about
       this phase.

    1. Once all ambiguous names have been resolved the
       [review process will start](#review-phase).
1. Back on Scholar gradebook, *Import* the gradebook csv file. Both grades and comments will be uploaded.
       
## Requirements

### Python

[Download](https://www.python.org/downloads/) and install the latest
Python 3 release (currently this program is not compatible with Python
2) for your operating system. If on Windows be sure to select the
option "Add python.exe to the search path" so that you don't need to
specify the full path to the python executable when running it from
the command line.

#### Windows Users

Things tend to go smoother if you are sure to install the 64bit
version of Python.

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

The GUI uses Tcl, if you installed the 64bit version of Python on
64bit windows you shouldn't have to install anything else to get this
to work. In the event that you're on 32bit Windows, or you installed
32bit Python you may have to install Tcl before
`manager_review_gui.py` will work. The suggested distribution is
[ActiveTcl](http://www.activestate.com/activetcl), it is free and does
not require registration to download. If this all seems too complicated,
blame Microsoft and then switch to a sensible operating system ;-)

## Usage

### Start with GUI

Double click the `manager_review_gui.py` file from your file browser.

The experimental GUI provides a convenient way for users to initialize
the program and set the desired assessment *Unicode Text* file and
gradebook CSV file. After that and pressing *Go* the GUI invokes the
command line program with the input and gradebook files set as well as
the `-i` and `-c` options. Once you have entered the final score and
comment the command line program will exit and grades and comments
will be saved to the gradebook file you selected. Import that file
into Scholar gradebook.

### Start from the command line

In the following example `assessment.txt` is the Unicode text exported
assesment data downloaded from Scholar Tests&Quizes and
`gradebook.csv` is the exported gradebook with no structure, just
grades. See the
[Exporting data from Scholar](#exporting-data-from-scholar) section
for instructions.

```
> python manager_review.py -i -g gradebook.csv assessment.txt
```

To record and include comments

```
> python manager_review.py -ic -g gradebook.csv assessment.txt
```

If reviewers made typos or spelling errors when entering reviewee names
you will be prompted for a name correction.  These corrections will be
saved in a file called `aliases.txt` in the current directory, you
can specify an alternate file using the `--aliases` command option.

```
> python3 manager_review.py -h
usage: manager_review.py [-h] [--interactive] [--gradebook GRADEBOOK]
                         [--name NAME] [--aliases ALIASES] [--comments]
                         [--submission-points SUBMISSION_POINTS]
                         [--input_file_encoding INPUT_FILE_ENCODING]
                         [--input_file_delimiter INPUT_FILE_DELIMITER]
                         [--gradebook_encoding GRADEBOOK_ENCODING]
                         [--gradebook_delimiter GRADEBOOK_DELIMITER]
                         input_file
```

Will display all available options.

### Name association

The first thing you are likely to see once the program is invoked via
either the command line or GUI is the name association prompt. This
appears when there are names entered by students that do not match
names in the gradebook. This could be due to spelling errors or
nicknames.

````
In section 2:00 Tu/Th, Team 1 who is "Joe Smith"?
````

Determine the full name of the student referenced and type it at the prompt and press `Enter`

````
In section 2:00 Tu/Th, Team 1 who is "Joe Smith"? Joseph Smith
In section 12:30 Tu/Th, Team 5 who is "Sue Lee"?
````

If the name you enter isn't found in gradebook the prompt will repeat
until you enter a name that exists. Additional prompts will continue
to appear as long as there are unmatched names. Once all names have
been matched the program will continue with the review phase. All name
associations are stored in a file called `aliases.txt` in directory in
which you ran the program. If you run the program again from the same
location you will not be prompted for name matching again. If you made
a mistake when matching names either edit the `aliases.txt` directly
in a text editor (e.g. WordPad, Notepad, Emacs, Vim, Sublime
Text... anything but MS Word, MS Word is *not* a text editor) or
delete the file and start over.

### Review phase

One all names are matched to people in the gradebook the program will enter review mode:

```
Joseph Smith (2:00 Tu/Th, Team 1)
        Interpersonal Relationships: 3.0
        Team Dynamics: 2.8
        Team Planning: 2.3
        Interdependence: 3.0

        "I came to all the meetings and I always did what I was told."

        "Joe came to all the meetings and did what he was told"

        "Joe missed many meetings and once I told him to bring
        me coffee and he didn't"

        peer subtotal: 11.1
        submission: 3
Instructor score for Joseph Smith (4.0):
```

If you see a number in parenthesis in the prompt to enter the
instructor's score this is a value that has already been recorded,
either by running the program previously or manually entering a grade
in gradebook. Pressing `Enter` will retain the original
value. Entering a new score and pressing enter will update the points
to the most recently entered value.

If no score exists you will not see any number or parenthesis and will
be required to enter a point value. The prompt will continue to appear
until you enter a valid numeric value.

```
        peer subtotal: 11.1
        submission: 3
Instructor score for Joseph Smith (4.0): 3.8
Instructor comments for Joseph Smith: Joe should have not let everyone tell him what to do
```

Currently it is not possible to enter multi-line comments, pressing
`Enter` will finish the comment and move on to the next review.

Once you enter a score and comment for the last person everything will
be recorded to the gradebook file you specified on startup:

```
Grades and comments written to ENGE__gradebook.csv, item name 'Manager's Review 2'
```

### Upload to scholar

Go to gradebook on Scholar, select *Import* and set the options to
import *No-structure (grades only)*, select the file that scores were
saved to and click *Next*.  Both scores and comments will be imported
into Gradebook under the item you created for this assignment.

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
5. Open the downloaded file in your spreadsheet program of choice and
   save to a Unicode CSV format. If using Excel select *Unicode Text*
   from the *Save as type* option. In its infinite wisdom, Microsoft
   decided that when exporting to CSV the only encoding option is
   ASCII.
