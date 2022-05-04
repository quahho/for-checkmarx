# Imports
import streamlit as st
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from bs4 import BeautifulSoup
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
        if subfolder_path.name in campaign:
            campaign_subfolders[subfolder_path.name] = subfolder_path
    
    # Return dictionary of subfolders with campaign names
    return campaign_subfolders


def getJobs(branches, campaign_id):

    # Initialize data list
    data = []

    # Getting titles section
    titles = branches.find_all("div", class_="progressBar--1DUJJ distDomainSection--3tWJq")

    # Add each title to the data list
    for title in titles:

        # Obtain the title text
        job_title = title.contents[0].text #.split(". ")[1]

        # Obtain the stats for the title
        columns = title.contents[1].find_all("div", class_="contentProgressBar--19bPv")

        # Compile all the data for the title
        values = [campaign_id] + [job_title] + [column.contents[1].text for column in columns]

        # Append values to data list
        data.append(values)

    # Return data list  
    return data


def getData(elements, campaign_id):

    # Initialize data list
    data = []

    # Compile all the data for the element
    values = [campaign_id] + [row.get_text(strip=True).replace("View All", "").replace(" ","") for row in elements]

    # Append values to data list
    data.append(values)

    # Return data list
    return data


def extractAll(input_subfolders, folder_path, main_date, alt_date):

    # Initialize variables
    highlight_data = []
    account_data = []
    campaign_data = []
    extra_data = []
    device_data = []
    job_data = []
    campaign_id = ''
    output_results = {}
    output_results_pages = {}

    # Start main process
    # Go through each subfolder 
    for subfolder_name, subfolder_path in input_subfolders.items():

        # Initialize counter
        counter = 0

        # Go through each file in the subfolder
        for f in os.scandir(subfolder_path):

            # Check for CSV files
            if f.is_file() and f.name.endswith('html'):

                # Increment counter
                counter = counter + 1

                # Set full file name
                full_file_name = folder_path + '/' + subfolder_name + '/' + f.name
                # print(full_file_name)

                # Create parser
                with open(full_file_name) as fp:
                    soup = BeautifulSoup(fp, "lxml")

                # Obtain campaign id from the html itself instead of the file name
                campaign_id = soup.find_all("span", class_="body--3W1jh")[4].text
                # print(campaignID)

                # Get the main content
                tree = soup.select("div.section--3PBDc")
                
                # Check if tree is empty
                if len(tree) == 0:
                    return {}

                # Contains highlights, account analytics & campaign analytics
                branchOne = tree[0].contents[0]

                # Contains distribution by device type
                branchTwo = tree[1].contents[3]

                # Contains job level and function
                branchThree = tree[1].contents[4]

                # Start of scraping process
                if counter == 1:

                    """ Highlights """
                    # Store the highlight container in a variable
                    highlights = branchOne.contents[0].find("div", class_="highlights--QIliH").find_all("div", class_="row bottom-xs")

                    # Call the funtion to extract data
                    highlight_data = highlight_data + getData(highlights, campaign_id)
                    # print(highlight_data)

                    """ Account Analystics """
                    # Store the account analytics container in a variable
                    account_analytics = branchOne.contents[1].find("div", class_="accountAnalytics--2KzuA").find_all("div", class_="row bottom-xs")

                    # Call the funtion to extract data
                    account_data = account_data + getData(account_analytics, campaign_id)
                    # print(account_data)

                    """ Campaign Analytics """
                    # Store the campaign analytics container in a variable
                    campaign_analytics = branchOne.contents[2].find("div", class_="campaignAnalytics--1XqIl").find_all("div", class_="row bottom-xs")

                    # Call the funtion to extract data
                    campaign_data = campaign_data + getData(campaign_analytics, campaign_id)
                    # print(campaign_data)

                    """ Extra (eCPC) """
                    # Store the extra eCPC container in a variable
                    extra = soup.find_all("span", class_="title2--25Hv2")[3]

                    # Call the funtion to extract data
                    extra_data = extra_data + getData(extra, campaign_id)
                    # print(extra_data)

                    """ Distribution by Device """
                    # Store the device distribution container in a variable
                    device_distribution = branchTwo.contents[0].find("div", class_="highcharts-legend highcharts-no-tooltip").select("div.highcharts-legend-item.highcharts-pie-series")

                    for row in device_distribution:
                        
                        # Compile all data for a device
                        device = [campaign_id]+[row.div.get_text(strip=True)]+[row.div.next_sibling.text.replace("Accounts Reached","")]+[row.div.next_sibling.next_sibling.text.replace("Impressions", "")]+[row.div.next_sibling.next_sibling.next_sibling.text.replace("Clicks","")]
                        
                        # Append values to device list
                        device_data.append(device)

                    # print(device_data)

                    """ Job Level and Function """
                    # Call the funtion to extract data
                    job_data = job_data + getJobs(branchThree, campaign_id)

                elif counter > 1:

                    # Run only for job level and function when counter is greater than 1
                    job_data =  job_data + getJobs(branchThree, campaign_id)

        # Add total pages for a campaign to output results
        output_results_pages[subfolder_name] = str(counter) + ' page(s)'

    # Add output result pages to output results dictionary
    output_results['Extracted HTML'] = output_results_pages

    # Check if any data in a list
    # Can check any list since all list should be filled after 1 HTML file
    if (len(highlight_data) == 0):

        # Exit early without producing compiled CSVs
        return output_results
    
    else:

        # Add produced files to output result dictionary
        output_results['Compiled CSVs'] = ['Device Type Distribution', 'Job Level Function', 'Summary Data']

    # End of scraping process   
    # Start producing compiled CSVs
    # Parse the all data into dataframes (done outside the loop since we have to iterate thru all the files)
    highlight_df = pd.DataFrame(highlight_data, columns=['Campaign ID', 'Total Spent', 'Accounts Reached'])
    account_df = pd.DataFrame(account_data, columns=['Campaign ID','Account CTR', 'Account VTR', 'Avg. Increase in Account Engagement', 'Accounts Newly Engaged', 'Accounts With Increased Engagement'])
    campaign_df = pd.DataFrame(campaign_data, columns=['Campaign ID', 'CTR', 'VTR', 'Impressions', 'Clicks', 'eCPM', 'Views', 'Influenced Form Fills'])
    extra_df = pd.DataFrame(extra_data, columns=['Campaign ID', 'eCPC'])
    device_df = pd.DataFrame(device_data, columns=['Campaign ID', 'Device Type', 'Accounts Reached', 'Impressions', 'Clicks'])    
    job_df = pd.DataFrame(job_data, columns=['Campaign ID', 'Job', 'Accounts Reached', 'Impressions', 'Clicks'])
    # print(highlight_df) 
    # print(account_df) 
    # print(campaign_df) 
    # print(extra_df)
    # print(device_df)
    # print(job_df)

    # Remove account reached column
    del highlight_df['Accounts Reached'] 

    # Set a common index for these dataframes
    highlight_df = highlight_df.set_index("Campaign ID")
    account_df = account_df.set_index("Campaign ID")
    campaign_df = campaign_df.set_index("Campaign ID")
    extra_df = extra_df.set_index("Campaign ID")

    # Merge to form summary data
    summary_df = pd.concat([highlight_df, account_df, campaign_df, extra_df], axis=1)
    summary_df = summary_df.reset_index()

    # Add extract date column to all data
    job_df['Extract Date'] = main_date
    device_df['Extract Date'] = main_date
    summary_df['Extract Date'] = main_date

    # print(jobLevelDf)
    # print(deviceDistDf)
    # print(summaryDf)

    # End of main process
    # Convert dataframe to CSV
    # Common campaign code
    campaignName = 'ALL'

    new_file_name = folder_path + '/' + alt_date + '-' + campaignName + '-' + 'compiled-JobLevelFunctionData.csv'
    job_df.to_csv(new_file_name, index=False)

    new_file_name = folder_path + '/' + alt_date + '-' + campaignName + '-' + 'compiled-DeviceTypeDistributionData.csv'
    device_df.to_csv(new_file_name, index=False)

    new_file_name = folder_path + '/' + alt_date + '-' + campaignName + '-' + 'compiled-SummaryData.csv'
    summary_df.to_csv(new_file_name, index=False)

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
    if 'html_folder_path' not in st.session_state:
        st.session_state.html_folder_path = ''

    if 'main_date' not in st.session_state:
        st.session_state.main_date = ''

    if 'alt_date' not in st.session_state:
        st.session_state.alt_date = ''
    
    # Campaign
    campaign_list = [
        'NA', 
        'EMEA', 
        'APAC'
    ]

    # ==============================================================================================

    # Create title
    st.title('HTML Extraction')

    # ==============================================================================================

    # Start of Step 1
    # First instruction
    st.text('')
    st.subheader('Step 1 : Select Date')

    # Request for date
    selected_date = st.date_input("When's the date of HTML extraction")

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
    if st.button('Choose Folder Containing HTML Subfolders'):

        # Opens file explorer for selection
        st.session_state.html_folder_path = filedialog.askdirectory(master=root)

    # Check the path variable
    if len(st.session_state.html_folder_path) > 0:

        # Print folder path if selected
        st.success(st.session_state.html_folder_path)

        # List out subfolders in the folder
        st.text('')
        st.markdown('**Subfolders found in the folder:**')

        # Get subfolders in folder
        input_subfolders = getCampaignSubfolders(st.session_state.html_folder_path, campaign_list)

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
    if st.session_state.html_folder_path and len(input_subfolders) > 0:
        started = st.button('Ready, Steady, GO!')
    else:
        started = st.button('Ready, Steady, GO!', disabled = True)

    # Start of main process
    if started:

        # Obtain list of output files
        output_results = extractAll(
            input_subfolders, 
            st.session_state.html_folder_path,
            st.session_state.main_date, 
            st.session_state.alt_date, 
        )

        # Check if HTML has been updated
        if len(output_results) == 0:

            # Set warning of outdated script (Website updated its HTML)
            st.warning('No data could be extracted from the HTML files. Possible update in website source code.')
        
        else:

            # Print success message
            st.success('Extraction completed. Mission accomplished!')

            # List out CSV files enriched in the folder
            st.text('')
            st.markdown('**HTML files extracted in the folder:**')

            # Print output results
            st.write(output_results)



