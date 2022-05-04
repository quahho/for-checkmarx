# Imports
import streamlit as st
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# ==============================================================================================

def getCampaignSubfolders(folder_path, campaign):

    # Get immediate subfolders in the folder
    subfolders = [f for f in os.scandir(folder_path) if f.is_dir()]

    # Initialize dictionary of subfolders with campaign names
    campaign_subfolders = {}

    # Get subfolders with campaign names
    for subfolder_path in subfolders:

        # Add to dictionary if name matches
        if subfolder_path.name in campaign.keys():
            campaign_subfolders[subfolder_path.name] = subfolder_path
    
    # Return dictionary of subfolders with campaign names
    return campaign_subfolders


def checkUnwantedTopRows(file):
    # The max column count a line in the file could have
    trigger_column_count = 2

    # Loop the data lines
    with open(file, 'r', encoding='utf-8-sig') as temp_f:
        # Read the first line
        line = temp_f.readline()
        # print(line)

        # Count the column count for the line
        column_count = len(line.split(','))
        # print(column_count)

        # Label file as perfect table or not
        if column_count == trigger_column_count:
            return False
        else:
            return True


def adjustUnwantedTopRows(file):
    # The max column count a line in the file could have
    largest_column_count = 0
    
    row_count = 0

    with open(file, 'r', encoding='utf-8-sig') as temp_f:
        # Read the lines
        lines = temp_f.readlines()
        # print(line)

        for l in lines:
            row_count = row_count + 1

            # Stop iteration after reaching table data
            if row_count == 8: break

            # Count the column count for the current line
            column_count = len(l.split(','))
            # print(column_count)

            # Set the new most column count
            largest_column_count = column_count if largest_column_count < column_count else largest_column_count

    # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)
    column_names = [i for i in range(0, largest_column_count)]

    return column_names


def enrichAdsOverview(df, main_date, campaign_id):
    # Remove the first 4 rows
    df = df.iloc[4:]
    # print(df)

    # Set first row as header
    df.columns = df.iloc[0]
    
    # Remove first row from table
    df = df[1:]
    # print(df)

    # Remove unwanted column
    del df['Campaign Name']
    del df['Data Type']
    del df['Accounts Newly Engaged (Lifetime)'] 
    del df['Accounts With Increased Engagement (Lifetime)'] 
    del df['Avg. Increase in Account Engagement (Lifetime)'] 
    # print(df.columns)

    # Rename columns
    df = df.rename(columns = {'AdGroup': 'Ad Group', 'Ad': 'Ad Name'}, inplace = False)
    # print(df.columns)

    # Remove rows without ads
    df = df[df['Ad Name'] != '-']
    # print(df.to_string())

    # Add necessary columns
    df['Extract Date'] = main_date
    df['Campaign ID'] = campaign_id
    # print(df.to_string())

    # Return cleaned datafram
    return df


def enrichBuyingStageAccounts(df, main_date, campaign_id):
    # Add necessary columns
    df['Extract Date'] = main_date
    df['Campaign ID'] = campaign_id
    # print(df.to_string())

    # Return cleaned datafram
    return df


def enrichBuyingStage(df, main_date, campaign_id):
    # Add necessary columns
    df['Extract Date'] = main_date
    df['Campaign ID'] = campaign_id
    # print(df.to_string())

    # Remove last 5 rows
    df = df[:-5]
    # print(df)

    # Return cleaned datafram
    return df


def enrichComparisonChart(df, main_date, campaign_id):
    # Remove the first 4 rows
    df = df.iloc[3:]
    # print(df)

    # Set first row as header
    df.columns = df.iloc[0]
    
    # Remove first row from table
    df = df[1:]
    # print(df)

    # Add necessary columns
    df['Extract Date'] = main_date
    df['Campaign ID'] = campaign_id
    # print(df.to_string())

    # Return cleaned datafram
    return df


def enrichReachedAccounts(df, main_date, campaign_id):
    # Remove the first 4 rows
    df = df.iloc[4:]
    # print(df)

    # Set first row as header
    df.columns = df.iloc[0]
    
    # Remove first row from table
    df = df[1:]
    # print(df)

    # Add necessary columns
    df['Extract Date'] = main_date
    df['Campaign ID'] = campaign_id
    # print(df.to_string())

    # Return cleaned datafram
    return df


def enrichTargetAccounts(df, main_date, campaign_id):
    # Add necessary columns
    df['Extract Date'] = main_date
    df['Campaign ID'] = campaign_id
    # print(df.to_string())

    # Return cleaned datafram
    return df


def enrichAll(input_subfolders, campaign_lookup, folder_path, main_date, alt_date):

    # Initialize variables
    file_name = ''
    is_perfect_table = ''
    raw_data = ''
    clean_data = ''
    category_name = ''
    output_results = {}

    # Start main process
    # Go through each subfolder 
    for subfolder_name, subfolder_path in input_subfolders.items():

        # Obtain campaign id by matching folder name with campaign
        campaign_id = campaign_lookup[subfolder_name]

        # Obtain campaign name as well
        campaign_name = subfolder_name

        # Initialize list of completed category for each campaign
        completed = []

        # Go through each file in the subfolder
        for f in os.scandir(subfolder_path):

            # Check for CSV files
            if f.is_file() and f.name.endswith('csv'):

                # Rename file name if too long
                if len(f.name) > 200:

                    # Set error text
                    error_text = 'There is a CSV file in ' + subfolder_name + ' subfolder whose name is too long. Rename the file and try again.'

                    # Print error text
                    st.warning(error_text)

                    # Skip process for this file
                    continue

                else:
                    file_name = f.name

                # Set full file name
                full_file_name = folder_path + '/' + subfolder_name + '/' + file_name
                # print(full_file_name)

                # Check if data is a perfect table
                is_perfect_table = checkUnwantedTopRows(full_file_name)
                # print('Perfect Table:', is_perfect_table)

                if not is_perfect_table:
                    # Obtain temporary column names
                    column_names = adjustUnwantedTopRows(full_file_name)

                    # Convert data into DataFrame
                    raw_data = pd.read_csv(full_file_name, header=None, names=column_names)
                    # print(raw_data)

                    # Check the type of file
                    if raw_data.iat[4, 0] == 'Campaign Name':

                        # Set category file name
                        category_name = 'enriched-Ads-Overview-Data.csv'

                        # Add to completed list
                        completed.append('Ads Overview')

                        # Run cleaning for Ads Overview
                        clean_data = enrichAdsOverview(raw_data, main_date, campaign_id)

                    elif raw_data.iat[3, 0] == 'Date':

                        # Set category
                        category_name = 'enriched-Comparison-Chart-Data.csv'

                        # Add to completed list
                        completed.append('Comparison Chart')

                        # Run cleaning for Comparison Chart
                        clean_data = enrichComparisonChart(raw_data, main_date, campaign_id)

                    elif raw_data.iat[4, 6] == 'Website Engagement':

                        # Set category
                        category_name = 'enriched-Reached-Accounts-Data.csv'

                        # Add to completed list
                        completed.append('Reached Accounts')

                        # Run cleaning for Reached Accounts
                        clean_data = enrichReachedAccounts(raw_data, main_date, campaign_id)

                else:
                    # Convert data into DataFrame
                    raw_data = pd.read_csv(full_file_name)
                    # print(raw_data)

                    # Check if file has been enriched
                    if 'Extract Date' in raw_data.columns:
                        continue

                    # Check the type of file
                    if raw_data.columns[3] == 'Buying Stage: Start':

                        # Set category
                        category_name = 'enriched-Buying-Stage-Accounts-Data.csv'

                        # Add to completed list
                        completed.append('Buying Stage Accounts')

                        # Run cleaning for Buying Stage Accounts
                        clean_data = enrichBuyingStageAccounts(raw_data, main_date, campaign_id)

                    elif raw_data.columns[0] == 'Timeframe':

                        # Set category
                        category_name = 'enriched-Buying-Stage-Data.csv'

                        # Add to completed list
                        completed.append('Buying Stage')

                        # Run cleaning for Buying Stage
                        clean_data = enrichBuyingStage(raw_data, main_date, campaign_id)

                    elif raw_data.columns[3] == '6sense Revenue Range':

                        # Set category
                        category_name = 'enriched-Target-Accounts-Data.csv'

                        # Add to completed list
                        completed.append('Target Accounts')

                        # Run cleaning for Target Accounts
                        clean_data = enrichTargetAccounts(raw_data, main_date, campaign_id)

                # Set file name
                new_file_name = folder_path + '/' + subfolder_name + '/' + alt_date + '-' + campaign_name + '-' + category_name
                # print(new_file_name)

                # Convert dataframe to CSV
                clean_data.to_csv(new_file_name, index=False, encoding='utf-8-sig')

        # Add list of completed category for a campaign to output results
        output_results[campaign_name] = completed

    # Return list of output files
    return output_results

# ==============================================================================================


def app():
    # ==============================================================================================

    # Set up tkinter
    root = tk.Tk()

    # Hide tkinter window
    root.withdraw()

    # Make folder picker dialog appear on top of other windows
    root.wm_attributes('-topmost', 1)

    # ==============================================================================================

    # Initialize key variables
    # Session
    if 'csv_folder_path' not in st.session_state:
        st.session_state.csv_folder_path = ''

    if 'main_date' not in st.session_state:
        st.session_state.main_date = ''

    if 'alt_date' not in st.session_state:
        st.session_state.alt_date = ''

    # Campaign
    campaign_lookup = {
        'NA' : 62242,
        'EMEA' : 62244,
        'APAC' : 62246
    }

    # ==============================================================================================

    # Create title
    st.title('CSV Enrichment')

    # ==============================================================================================

    # Start of Step 1
    # First instruction
    st.text('')
    st.subheader('Step 1 : Select Date')

    # Request for date
    selected_date = st.date_input("When's the date of CSV extraction")

    # Convert date format
    st.session_state.main_date = '{dt.day}/{dt.month}/{dt.year}'.format(dt = selected_date)
    st.session_state.alt_date = '[{dt.day}-{dt.month}-{dt.year}]'.format(dt = selected_date)
    # st.write(st.session_state.main_date)
    # st.write(st.session_state.alt_date)

    # ==============================================================================================

    # Start of Step 2
    # Second instruction
    st.text('')
    st.subheader('Step 2 : Select Folder')

    # Create folder selector button
    if st.button('Choose Folder Containing CSV Subfolders'):

        # Opens file explorer for selection
        st.session_state.csv_folder_path = filedialog.askdirectory(master=root)

    # Check the path variable
    if len(st.session_state.csv_folder_path) > 0:

        # Print folder path if selected
        st.success(st.session_state.csv_folder_path)

        # List out subfolders in the folder
        st.text('')
        st.markdown('**Subfolders found in the folder:**')

        # Get subfolders in folder
        input_subfolders = getCampaignSubfolders(st.session_state.csv_folder_path, campaign_lookup)
        
        if len(input_subfolders) > 0:

            # Create dictionary for print
            found_subfolders = {'Subfolder': list(input_subfolders.keys())}

            # Print found subfolders
            st.write(found_subfolders)

        else:
            st.info('No subfolders with campaign name found in this folder...')

    else:
        # Informs if cancel selection
        st.info('No folder has been selected yet...')

    # ==============================================================================================

    # Start of Step 3
    # Third instruction
    st.text('')
    st.subheader('Step 3 : Start Process')
    
    # Create run button
    if st.session_state.csv_folder_path and len(input_subfolders) > 0:
        started = st.button('Ready, Set, GO!')
    else:
        started = st.button('Ready, Set, GO!', disabled = True)

    # Start of main process
    if started:

        # Obtain list of output files
        output_results = enrichAll(
            input_subfolders, 
            campaign_lookup,
            st.session_state.csv_folder_path,
            st.session_state.main_date, 
            st.session_state.alt_date, 
        )
        
        # Print success message
        st.success('Enrichment completed. Mission accomplished!')

        # List out CSV files enriched in the folder
        st.text('')
        st.markdown('**CSV files enriched in the folder:**')

        # Print output results
        st.write(output_results)


        