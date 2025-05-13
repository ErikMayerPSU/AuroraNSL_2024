import pandas as pd
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog, simpledialog

#Function to filter the data by a specific date (time_start column)
def filter_by_time_start_date(data, date_str):
    #Convert the "time_start" column to datetime
    data['time_start'] = pd.to_datetime(data['time_start'], errors='coerce')
    
    #Convert the requested date to datetime
    target_date = pd.to_datetime(date_str)
    
    #Filter and return only the rows where the "time_start" date matches the requested date
    return data[data['time_start'].dt.date == target_date.date()]

#Function to adjust the "time_start" to the nearest multiple of 4 minutes
def adjust_to_next_4_minute_increment(time_start):
    #Get the minutes part of the time
    minutes = time_start.minute
    
    #Find the remainder when divided by 4
    remainder = minutes % 4
    
    #If the minutes are not a multiple of 4, adjust to the next closest 4 minute mark
    if remainder != 0:
        minutes = minutes + (4 - remainder)
        time_start = time_start.replace(minute=minutes, second=0) #Update the time with the new minute
    return time_start

#Create a Tkinter window to use the file selection and input dialogs
root = tk.Tk()
root.withdraw()  #Hide the root window as we only want the dialog boxes

#Open a file selection dialog to choose the CSV file
file_path = filedialog.askopenfilename(title="Select a CSV file", filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))

#Open a simple input dialog to get the date for filtering (YYYY-MM-DD format)
date_input = simpledialog.askstring("Input", "Please enter the date for filtering (YYYY-MM-DD):")

#Check if the user selected a file and provided a date
if file_path and date_input:
    #Read the selected CSV file into a pandas DataFrame
    data = pd.read_csv(file_path, encoding='ISO-8859-1')  #Read the data with an encoding to handle special characters used in foreign languages
    
    #Filter the data by the given date
    filtered_data = filter_by_time_start_date(data, date_input)

    processed_entries = []  #List to store processed data entries

    #Loop through each row in the filtered data to process it
    for _, row in filtered_data.iterrows():
        #Skip rows where "see_aurora" is "f"
        if row['see_aurora'] == 'f':
            continue

        #Convert "time_start" to datetime
        time_start = pd.to_datetime(row['time_start'])
        date_only = time_start.date()  #Get only the date for the output file

        #Adjust the "time_start" to the nearest multiple of 4 minutes
        time_start = adjust_to_next_4_minute_increment(time_start)

        #If "on_going" is "f" only create one entry for the time_start
        if row['on_going'] == 'f':
            processed_entries.append({
                'date': date_only,
                'time': time_start.strftime('%H:%M:%S'),  #Convert time to 'HH:MM:SS' format
                'height_id': row['height_id'],
                'location': row['location'],
                'st_y': row['st_y'],
                'st_x': row['st_x']
            })
        #If "on_going" is "t" create multiple entries every 4 minutes until "time_end"
        elif row['on_going'] == 't':
            current_time = time_start
            while current_time <= pd.to_datetime(row['time_end']):
                processed_entries.append({
                    'date': date_only,
                    'time': current_time.strftime('%H:%M:%S'),
                    'height_id': row['height_id'],
                    'location': row['location'],
                    'st_y': row['st_y'],
                    'st_x': row['st_x']
                })
                current_time += timedelta(minutes=4)  #Increment by 4 minutes for the next entry

    #Create a DataFrame from the processed entries
    processed_data = pd.DataFrame(processed_entries)

    #Automatically generate the filename with the date included in the output file
    output_filename = f"Filtered_Aurora_Data_{date_input.replace('-', '')}.csv"
    
    #Open a file save dialog to choose the location and change the name if desired
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=output_filename, title="Save As", filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))

    #If the user selected a location save the processed data to the chosen file
    if save_path:
        processed_data.to_csv(save_path, index=False)  #Save the data to a CSV file without the index
        print(f"File saved successfully: {save_path}")
    else:
        print("No location selected for saving the file.")  #If no location was selected
else:
    print("No file selected or invalid input.")  #If no file was selected or the date was invalid

