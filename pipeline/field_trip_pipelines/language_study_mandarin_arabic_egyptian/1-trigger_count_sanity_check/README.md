# Sanity Check for counting triggers in `combined binary mode`

The script takes as input:
- a .con MEG data recording file
- the CSV file that have the sentences that was used during the experiment for acquiring the above .con recording

and provides as output:
- a sanity check where we are counting the number of events of each type from the CSV file, then scans the .con and retrieves the events, then matches the expected count from CSV per type with the observed ones from the .con, the script is easy to use but less trivial to understand.


Pre-step before running the trigger_combined_analysis.m

- run the word_counting_script.py to add the word-count column to your CSV (as the default CSV does not have this column)


Operation:
- In `triggers_combined_analysis.m` set the path to `confile` and `csv_file_experiment` (output from word_count_script.py)
- Run the script, ensure that all non zero triggers are OK (means observed number of triggers is equal to expected number of triggers)
