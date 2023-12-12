""" Class to analyze categorization data for FBC DiQ TRL 6 study.

    Written by: Travis M. Moore
"""

###########
# Imports #
###########
# Import data science packages
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import system packages
import glob
import os


#########
# Begin #
#########
def categorize_data(datapath):
    """ Import and analyze categorization data.
    """
    # Create Results directory if it does not exist
    _check_dir("Results")

    # Get all .csv file names from provided directory
    all_files = glob.glob(os.path.join(datapath, "*.csv"))

    # Create single dataframe
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)
    data = pd.concat(li)

    # Get response counts for each stimulus
    counts = data.groupby("stimulus")["actual_resp"].sum()
    print("\nResponse counts for each stimulus:")
    print(counts)
    counts.to_csv(r'Results\all_responses.csv')

    # Get response counts for each stimulus by response type
    # counts2 = data.groupby(['stimulus', 'actual_resp'])['actual_resp'].sum()
    # print("\nResponse counts for each stimulus by response type:")
    # print(counts2)

    # Print results to console
    df = pd.DataFrame(counts)
    print("\nChirp Detected:")
    print(df[df['actual_resp']==max(data.stimulus.value_counts())])
    print("\nChirp NOT Detected:")
    print(df[df['actual_resp']==0])

    # Write results to .csv file
    df[df['actual_resp']==max(data.stimulus.value_counts())].to_csv(
        r'Results\chirp_detected.csv'
    )
    df[df['actual_resp']==0].to_csv(r"Results\chirp_not_detected.csv")


    # Display plot
    #plt.bar(counts.index, counts.values) # No index in counts so this doesn't work
    plt.bar(list(range(0, len(counts))), counts.values)
    plt.tick_params(
        axis='x',
        which='both', 
        labelbottom=False
    )
    plt.title("Number of 'Yes' Responses per Stimulus\n" +
            f"Yes Criterion={max(data.stimulus.value_counts())}, No Criterion=0"
    )
    plt.ylabel("Yes Responses")
    plt.xlabel("Stimulus")
    plt.show()


def _check_dir(dir_name):
    """ Check for existing Results directory.
        Create Results directory if it doesn't exist.
    """
    # Name directory
    results_directory = dir_name

    # Check for directory 
    # Create if != exist
    data_dir_exists = os.access(results_directory, os.F_OK)
    if not data_dir_exists:
        print(f"\ncsvmodel: {results_directory} directory not found! " +
            "Creating it...")
        os.mkdir(results_directory)
        print(f"csvmodel: Successfully created {results_directory} " +
                "directory!")
