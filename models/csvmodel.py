""" Model to write data to .csv
"""

############
# IMPORTS  #
############
# Import system packages
import csv
from pathlib import Path
from datetime import datetime
import os


#########
# MODEL #
#########
class CSVModel:
    """ Write provided dictionary to .csv
    """
    def __init__(self, sessionpars):
        self.sessionpars = sessionpars

        # Generate date stamp
        self.datestamp = datetime.now().strftime("%Y_%b_%d_%H%M")

    
    def save_record(self, data):
        """ Save a dictionary of data to .csv file 
        """
        # Check for existing data folder
        data_directory = "Data"
        data_dir_exists = os.access(data_directory, os.F_OK)
        if not data_dir_exists:
            print(f"\ncsvmodel: {data_directory} directory not found! " + 
                "Creating it...")
            os.mkdir(data_directory)
            print(f"csvmodel: Successfully created {data_directory} " +
                  "directory!")
        
        # Create file name and path
        filename = f"{self.sessionpars['subject'].get()}_{self.sessionpars['condition'].get()}_{self.datestamp}.csv"
        self.file = Path(os.path.join(data_directory, filename))

        # Check for write access to store csv
        file_exists = os.access(self.file, os.F_OK)
        parent_writable = os.access(self.file.parent, os.W_OK)
        file_writable = os.access(self.file, os.W_OK)
        if (
            (not file_exists and not parent_writable) or
            (file_exists and not file_writable)
        ):
            msg = f"\ncsvmodel: Permission denied accessing file: {filename}"
            raise PermissionError(msg)

        # Write file
        newfile = not self.file.exists()
        with open(self.file, 'a', newline='') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(data)
        print("\ncsvmodel: Record successfully saved!")
