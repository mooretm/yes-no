""" Class for importing matrix file and preparing trials.
"""

# Import data science packages
import pandas as pd

# Import system packages
import random
import os
from pathlib import Path

import tkinter as tk
from tkinter import messagebox

#########
# BEGIN #
#########
class StimulusModel:
    def __init__(self, sessionpars):
        
        # Assign variables
        self.sessionpars = sessionpars

        #####################
        # Sequence of Funcs #
        #####################
        # Import matrix file
        self._load_matrix()

        # Add full audio paths to matrix file df
        self._add_full_audio_paths()

        # Create trial repetitions
        self._do_reps()

        # If specified, randomize trials
        if self.sessionpars['randomize'].get() == 1:
            self._randomize()


    def _load_matrix(self):
        try:
            print('\nstimulusmodel: Reading matrix file')
            # Create private attribute of raw matrix file
            self._matrix_file = pd.read_csv(
                self.sessionpars['matrix_file_path'].get()
            )
        except FileNotFoundError:
            print('stimulusmodel: File not found!')
            raise


    def _add_full_audio_paths(self):
        """ Add the audiodir from sessionpars to audio file 
            names in raw matrix file.
        """
        # Get audio files directory
        audio_dir = Path(self.sessionpars['audio_files_dir'].get())

        for row in self._matrix_file.index:
            # Create full path to audio file
            full_path = os.path.join(
                audio_dir, self._matrix_file.iloc[row,0]
            )

            # Update name in _matrix_file df
            self._matrix_file.iloc[row,0] = full_path


    def _do_reps(self):
        """ Repeat matrix file trials according to the number 
            specified in File>Session.
        """
        # Create a copy of private raw matrix import
        # to preserve it and avoid multiple versions issues
        self.matrix = self._matrix_file.copy()

        # Create repeated trials
        print('stimulusmodel: Creating trial repetitions')
        self.matrix = pd.concat(
            [self.matrix] * self.sessionpars['repetitions'].get(), 
            ignore_index=True
        )


    def _randomize(self):
        """ Randomize trials in self.matrix.
        """
        print('stimulusmodel: Randomizing trials')
        # Get trial numbers from matrix df index
        trials = list(self.matrix.index)

        # Shuffle (in place)
        random.shuffle(trials)

        # Create new df column with shuffled trial order
        self.matrix['order'] = trials

        # Sort by new order column
        self.matrix.sort_values(by='order', inplace=True)

        # Remove order column
        self.matrix.drop('order', axis=1, inplace=True)

        # Reset index
        self.matrix.reset_index(drop=True, inplace=True)


    def prep_data(self, current_trial, response, save_list):
        """ Select data to save and send to csv model.
            This is tricky because I'm using a dictionary to hold all 
            the data, and the order that values are entered into the 
            dict matters.
        """
        # Avoid conflicts and save memory by deleting previous trial data
        try:
            del self.trial_data
        except AttributeError:
            pass

        # Dictionary to hold extracted tk variables (with .get())
        temp = dict()

        # Enter the trial number first so it appears first in the 
        # output file
        temp['trial'] = current_trial + 1

        # Add audio stimulus .wav file name
        temp['stimulus'] = os.path.basename(
            self.matrix.iloc[current_trial,0])

        # Get tk variable values and populate temp dict
        for key in self.sessionpars:
            temp[key] = self.sessionpars[key].get()

        # Create new dict with only desired items
        try:
            self.trial_data = dict((k, temp[k]) for k in save_list)
        except KeyError as e:
            print('\nstimulusmodel: Unexpected variable when attempting ' +
                  f'to save: {e}')
            raise

        # Add additional data to be written to file
        try:
            # Get expected response from matrix file
            self.trial_data['expected_resp'] = self.matrix.iloc[current_trial, 2]
            # Categorize responses as signal detection theory proportions
            if (self.trial_data['expected_resp']=='yes') and (response==1):
                self.trial_data['resp_type'] = 'H'
            elif (self.trial_data['expected_resp']=='yes') and (response==0):
                self.trial_data['resp_type'] = 'M'
            elif (self.trial_data['expected_resp']=='no') and (response==1):
                self.trial_data['resp_type'] = 'FA'
            elif (self.trial_data['expected_resp']=='no') and (response==0):
                self.trial_data['resp_type'] = 'CR'

            # Determine whether response was correct or incorrect
            if (self.trial_data['resp_type'] == 'H') or \
            (self.trial_data['resp_type'] == 'CR'):
                msg = "Correct"
            else:
                msg = "Incorrect"

            # Display feedback
            messagebox.showinfo(
                title="Feedback",
                message=msg
            )
        except IndexError:
            print("\nstimulusmodel: No expected response column in " +
                  "matrix file.")
            print("stimulusmodel: Unable to calculate SDT proportions.")

        # Add actual response
        self.trial_data['actual_resp'] = response
