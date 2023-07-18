""" Session parameters dialog
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# Import system packages
import os


#########
# BEGIN #
#########
class SessionDialog(tk.Toplevel):
    """ Dialog for setting session parameters
    """
    def __init__(self, parent, sessionpars, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.sessionpars = sessionpars

        self.withdraw()
        self.title("Session Parameters")
        self.grab_set()


        #################
        # Create Frames #
        #################
        # Shared frame settings
        frame_options = {'padx': 10, 'pady': 10}
        widget_options = {'padx': 5, 'pady': 5}

        # Session info frame
        frm_session = ttk.Labelframe(self, text='Session Information')
        frm_session.grid(row=5, column=5, **frame_options, sticky='nsew')

        # Session options frame
        frm_options = ttk.Labelframe(self, text='Stimulus Options')
        frm_options.grid(row=10, column=5, **frame_options, sticky='nsew')

        # Audio file browser frame
        frm_audiopath = ttk.Labelframe(self, text="Audio File Directory")
        frm_audiopath.grid(row=15, column=5, **frame_options, ipadx=5, ipady=5)

        # Sentence file browser frame
        frm_matrixpath = ttk.Labelframe(self, text='Matrix File Path')
        frm_matrixpath.grid(row=20, column=5, **frame_options, ipadx=5, ipady=5)


        #######################
        # Create view widgets #
        #######################
        # Subject
        ttk.Label(frm_session, text="Subject:"
            ).grid(row=5, column=5, sticky='e', **widget_options)
        ttk.Entry(frm_session, width=20, 
            textvariable=self.sessionpars['subject']
            ).grid(row=5, column=10, sticky='w')

        # Condition
        ttk.Label(frm_session, text="Condition:"
            ).grid(row=10, column=5, sticky='e', **widget_options)
        ttk.Entry(frm_session, width=20, 
            textvariable=self.sessionpars['condition']
            ).grid(row=10, column=10, sticky='w')

        # Randomize
        #self.random_var = tk.IntVar(value=self.sessionpars['randomize'])
        chk_random = ttk.Checkbutton(frm_options, text="Randomize",
            takefocus=0, variable=self.sessionpars['randomize'])
        chk_random.grid(row=5, column=5,  columnspan=20, sticky='w', **widget_options)

        # Repetitions
        ttk.Label(frm_options, text="Presentation(s):"
            ).grid(row=10, column=5, sticky='e', **widget_options)
        ttk.Entry(frm_options, width=20, 
            textvariable=self.sessionpars['repetitions']
            ).grid(row=10, column=10, sticky='w')

        # Audio directory
        ttk.Label(frm_audiopath, text="Path:"
            ).grid(row=20, column=5, sticky='e', **widget_options)
        # Get audio directory from sessionpars dict
        full_audio_path = self.sessionpars['audio_files_path'].get()
        # Truncate to fit in label
        short_audio_path = self._truncate_path(full_audio_path)
        # Create textvariable
        self.audio_var = tk.StringVar(value=short_audio_path)
        ttk.Label(frm_audiopath, textvariable=self.audio_var, 
            borderwidth=2, relief="solid", width=60
            ).grid(row=20, column=10, sticky='w')
        ttk.Button(frm_audiopath, text="Browse", command=self._get_audio_directory, state='disabled'
            ).grid(row=25, column=10, sticky='w', pady=(0, 10))

        # Matrix directory
        ttk.Label(frm_matrixpath, text="Path:"
            ).grid(row=30, column=5, sticky='e', **widget_options)
        # Get audio directory from sessionpars dict
        full_matrix_path = self.sessionpars['matrix_file_path'].get()
        # Truncate to fit in label
        short_matrix_path = self._truncate_path(full_matrix_path)
        # Create textvariable
        self.matrix_var = tk.StringVar(value=short_matrix_path)
        ttk.Label(frm_matrixpath, textvariable=self.matrix_var, 
            borderwidth=2, relief="solid", width=60
            ).grid(row=30, column=10, sticky='w')
        ttk.Button(frm_matrixpath, text="Browse", command=self._get_matrix_file
            ).grid(row=35, column=10, sticky='w', pady=(0, 10))

        # Submit button
        btn_submit = ttk.Button(self, text="Submit", command=self._on_submit)
        btn_submit.grid(row=40, column=5, columnspan=2, pady=(0, 10))

        # Center the session dialog window
        self.center_window()


    #############
    # Functions #
    #############
    def center_window(self):
        """ Center the root window 
        """
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        self.geometry("+%d+%d" % (x, y))
        self.deiconify()


    def _truncate_path(self, long_path):
        """ Truncate path (if necessary) and return value
        """
        if len(long_path) > 60:
            short = '...' + long_path[-60:]
            return short
        else:
            if long_path == "":
                return 'Please provide a path'
            else:
                return long_path


    def _get_audio_directory(self):
        """ Get path to audio files
        """
        self.sessionpars['audio_files_path'].set(
            filedialog.askdirectory(title="Audio File Directory"))


    def _get_matrix_file(self):
        """ Get path to matrix file
        """
        # Get file from dialog
        filename = filedialog.askopenfilename(title="Matrix File", filetypes=[("CSV", "*.csv")])
        # Set file plus path to sessionpars
        self.sessionpars['matrix_file_path'].set(filename)

        # Get directory based on matrix file folder
        directory = os.path.split(self.sessionpars['matrix_file_path'].get())[0]
        # Set audio directory to sessionpars
        self.sessionpars['audio_files_path'].set(directory)


    def _check_presentations(self):
        if self.sessionpars['repetitions'].get() == 0:
            self.sessionpars['repetitions'].set(1)
            messagebox.showwarning(title="Seriously?",
                message="Invalid number of presentations!",
                detail="You must have at least 1 round of presentations! " +
                    "Updating to 1 presentation."
            )


    def _on_submit(self):
        """ Check number of presentations != 0.
            Send submit event to controller.
        """
        # Make sure the number of presentations isn't 0
        self._check_presentations()

        print("\nviews_sessiondialog: Sending save event...")
        self.parent.event_generate('<<SessionSubmit>>')
        self.destroy()
