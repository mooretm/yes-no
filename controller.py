""" Yes/No task controller. 

    Written by: Travis M. Moore
    Created: July 14, 2023
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import messagebox

# Import system packages
import os
from pathlib import Path

# Import misc packages
import webbrowser
import markdown

# Import custom modules
# Menu imports
from menus import mainmenu
# Function imports
from functions import general
# Exception imports
from exceptions import audio_exceptions
# Model imports
from models import sessionmodel
from models import audiomodel
from models import calmodel
from models import csvmodel
from models import updatermodel
# View imports
from views import mainview
from views import sessionview
from views import audioview
from views import calibrationview


#########
# BEGIN #
#########
class Application(tk.Tk):
    """ Application root window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #############
        # Constants #
        #############
        self.NAME = 'Yes-No Task Controller'
        self.VERSION = '0.0.0'
        self.EDITED = 'July 18, 2023'

        # Create menu settings dictionary
        self._app_info = {
            'name': self.NAME,
            'version': self.VERSION,
            'last_edited': self.EDITED
        }


        ######################################
        # Initialize Models, Menus and Views #
        ######################################
        # Setup main window
        self.withdraw() # Hide window during setup
        self.resizable(False, False)
        self.title(self.NAME)

        # Assign special quit function on window close
        # Used to close Vulcan session cleanly even if 
        # user closes window via "X"
        self.protocol('WM_DELETE_WINDOW', self._quit)

        # Start with an invalid response
        self.response = 999

        # Load current session parameters from file
        # Or load defaults if file does not exist yet
        self.sessionpars_model = sessionmodel.SessionParsModel(self._app_info)
        self._load_sessionpars()

        # Load CSV writer model
        self.csvmodel = csvmodel.CSVModel(self.sessionpars)

        # Load calibration model
        self.calmodel = calmodel.CalModel(self.sessionpars)

        # Load main view
        self.grid_columnconfigure(0, weight=1) # center widget
        self.grid_rowconfigure(0, weight=1) # center widget
        self.main_frame = mainview.MainFrame(self)
        self.main_frame.grid(row=0, column=0)

        # Load menus
        menu = mainmenu.MainMenu(self, self._app_info)
        self.config(menu=menu)

        # Create callback dictionary
        event_callbacks = {
            # File menu
            '<<FileSession>>': lambda _: self._show_session_dialog(),
            '<<FileStart>>': lambda _: self.start_task(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsAudioSettings>>': lambda _: self._show_audio_dialog(),
            '<<ToolsCalibration>>': lambda _: self._show_calibration_dialog(),

            # Help menu
            '<<Help>>': lambda _: self._show_help(),

            # Session dialog commands
            '<<SessionSubmit>>': lambda _: self._save_sessionpars(),

            # Calibration dialog commands
            '<<CalPlay>>': lambda _: self.play_calibration_file(),
            '<<CalStop>>': lambda _: self.stop_calibration_file(),
            '<<CalibrationSubmit>>': lambda _: self._calc_offset(),

            # Audio dialog commands
            '<<AudioDialogSubmit>>': lambda _: self._save_sessionpars(),

            # Main View commands
            '<<MainYes>>': lambda _: self._on_yes(),
            '<<MainNo>>': lambda _: self._on_no(),
            '<<MainSubmit>>': lambda _: self._on_submit()
        }

        # Bind callbacks to sequences
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        # Center main window
        self.center_window()

        # Check for updates
        if self.sessionpars['check_for_updates'].get() == 'yes':
            _filepath = self.sessionpars['version_lib_path'].get()
            u = updatermodel.VersionChecker(_filepath, self.NAME, self.VERSION)
            if not u.current:
                self.destroy()


    #####################
    # General Functions #
    #####################
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


    def _quit(self):
        """ Exit the application.
        """
        self.destroy()


    ###################
    # Audio Functions #
    ###################
    def _play(self):
        """ Format channel routing, present audio and catch 
            exceptions.
        """
        # Attempt to present audio
        try:
            self.a.play(
                level=self.sessionpars['scaling_factor'].get(),
                device_id=self.sessionpars['audio_device'].get(),
                routing=self._format_routing(
                    self.sessionpars['channel_routing'].get())
            )
        except audio_exceptions.InvalidAudioDevice as e:
            print(e)
            messagebox.showerror(
                title="Invalid Device",
                message="Invalid audio device! Go to Tools>Audio Settings " +
                    "to select a valid audio device.",
                detail = e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except audio_exceptions.InvalidRouting as e:
            print(e)
            messagebox.showerror(
                title="Invalid Routing",
                message="Speaker routing must correspond with the " +
                    "number of channels in the audio file! Go to " +
                    "Tools>Audio Settings to update the routing.",
                detail=e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except audio_exceptions.Clipping:
            print("controller: Clipping has occurred! Aborting!")
            messagebox.showerror(
                title="Clipping",
                message="The level is too high and caused clipping.",
                detail="The waveform will be plotted when this message is " +
                    "closed for visual inspection."
            )
            self.a.plot_waveform("Clipped Waveform")


    def _format_routing(self, routing):
        """ Convert space-separated string to list of ints.
        """
        routing = routing.split()
        routing = [int(x) for x in routing]

        return routing


    ###################
    # File Menu Funcs #
    ###################
    def start_task(self):
        # Calculate level based on SLM offset
        self._calc_level(90)

        # Create audio object
        _path = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\stim2.wav'
        try:
            self.a = audiomodel.Audio(Path(_path))
        except FileNotFoundError:
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find the audio file!",
                detail="Go to File>Session to specify a valid audio path."
            )
            self._show_session_dialog()
            return

        # Present audio
        self._play()


    ########################
    # Main View Functions #
    ########################
    def _on_yes(self):
        """ Set response value to 1 (yes).
        """
        self.response = 1


    def _on_no(self):
        """ Set response value to 0 (no).
        """
        self.response = 0


    def _on_submit(self):
        """ Assign response value and save to file.
        """
        if self.response == 0:
            print(f"\ncontroller: You answered: no")
        elif self.response == 1:
            print(f"\ncontroller: You answered: yes")
        else: 
            print("Unrecognized response!")
            messagebox.showerror(
                title="Invalid Response",
                message="The response type is invalid!",
                detail=f'Response was {self.response}, but expected 0 or 1'
            )


    def _on_save(self):
        """ Format values and send to csv model.
        """
        # Get tk variable values
        data = dict()
        for key in self.sessionpars:
            data[key] = self.sessionpars[key].get()

        # Save data
        print('controller: Calling save record function...')
        self.csvmodel.save_record(data)


    ############################
    # Session Dialog Functions #
    ############################
    def _show_session_dialog(self):
        """ Show session parameter dialog
        """
        print("\ncontroller: Calling session dialog...")
        sessionview.SessionDialog(self, self.sessionpars)


    def _load_sessionpars(self):
        """ Load parameters into self.sessionpars dict 
        """
        vartypes = {
        'bool': tk.BooleanVar,
        'str': tk.StringVar,
        'int': tk.IntVar,
        'float': tk.DoubleVar
        }

        # Create runtime dict from session model fields
        self.sessionpars = dict()
        for key, data in self.sessionpars_model.fields.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.sessionpars[key] = vartype(value=data['value'])
        print("\ncontroller: Loaded sessionpars model fields into " +
            "running sessionpars dict")


    def _save_sessionpars(self, *_):
        """ Save current runtime parameters to file 
        """
        print("\ncontroller: Calling sessionpar model set and save funcs...")
        for key, variable in self.sessionpars.items():
            self.sessionpars_model.set(key, variable.get())
            self.sessionpars_model.save()


    ########################
    # Tools Menu Functions #
    ########################
    def _show_audio_dialog(self):
        """ Show audio settings dialog
        """
        print("\ncontroller: Calling audio dialog...")
        audioview.AudioDialog(self, self.sessionpars)

    def _show_calibration_dialog(self):
        """ Display the calibration dialog window
        """
        print("\ncontroller: Calling calibration dialog...")
        calibrationview.CalibrationDialog(self, self.sessionpars)


    ################################
    # Calibration Dialog Functions #
    ################################
    def play_calibration_file(self):
        """ Load calibration file and present
        """
        # Get calibration file
        self.calmodel.get_cal_file()

        # Play calibration file
        self.calmodel.play_cal()


    def stop_calibration_file(self):
        """ Stop playback of calibration file
        """
        # Stop calibration playback
        self.calmodel.stop_cal()


    def _calc_offset(self):
        """ Calculate offset based on SLM reading.
        """
        # Calculate new presentation level
        self.calmodel.calc_offset()
        # Save level - this must be called here!
        self._save_sessionpars()


    def _calc_level(self, desired_spl):
        """ Calculate new dB FS level using slm_offset.
        """
        # Calculate new presentation level
        self.calmodel.calc_level(desired_spl)

        # Save level - this must be called here!
        self._save_sessionpars()


    #######################
    # Help Menu Functions #
    #######################
    def _show_help(self):
        """ Create html help file and display in default browser
        """
        print("controller: Looking for help file in compiled " +
            "version temp location...")
        help_file = general.resource_path('README\\README.html')
        file_exists = os.access(help_file, os.F_OK)
        if not file_exists:
            print('controller: Not found!\nChecking for help file in ' +
                'local script version location')
            # Read markdown file and convert to html
            with open('README.md', 'r') as f:
                text = f.read()
                html = markdown.markdown(text)

            # Create html file for display
            with open('.\\assets\\README\\README.html', 'w') as f:
                f.write(html)

            # Open README in default web browser
            webbrowser.open('.\\assets\\README\\README.html')
        else:
            webbrowser.open(help_file)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
