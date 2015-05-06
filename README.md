# Managers Review Processor

## Usage

In the following example `assessment.csv` is the csv exported
assesment data downloaded from Scholar Tests&Quizes and
`gradebook.csv` is the exported gradebook with no structure, just
grades.

```
> python3 manager_review.py -i -g gradebook.csv Assessment-Project#2_Team_Eval.csv
```

To record and include comments

```
> python3 manager_review.py -ic -g gradebook.csv Assessment-Project#2_Team_Eval.csv
```

If reviewers made typoes or missspellings when entering reviewee names
you will be prompted for a name correction.  These correctons will be saved in a file called `alieases.txt` in the current directory, you can specify an alternate file using the `--aliases` command option.

```
> python3 manager_review.py -h
```

Will display all available options
