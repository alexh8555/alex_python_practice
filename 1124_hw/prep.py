import pandas as pd

##############CONFIG################
inputFileName = './1124_hw/pairs.csv'
inputFileName2 = './1124_hw/distances.csv'
####################################

def data_preprocessing(df):
# Initialize the lists to hold rows for receiver and doner dataframes
    receiver_rows = []
    doner_rows = []

    # Loop through each row in the original DataFrame
    for index, row in df.iterrows():
        if row['type'] == 'receiver':
            # Add the relevant columns to the receiver rows list
            receiver_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'RBT': row['RBT'],
                'Rage': row['Rage'],
                'Location': row['Location']
            })

        elif row['type'] == 'doner':
            # Add the relevant columns to the doner rows list
            doner_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'DBT': row['DBT'],
                'Dage': row['Dage'],
                'Location': row['Location']
            })

        elif row['type'] == 'pair':
            # Add the relevant columns to both receiver and doner rows lists
            receiver_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'RBT': row['RBT'],
                'Rage': row['Rage'],
                'Location': row['Location']
            })

            doner_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'DBT': row['DBT'],
                'Dage': row['Dage'],
                'Location': row['Location']
            })

    # Convert the lists of rows to DataFrames
    receiver_df = pd.DataFrame(receiver_rows)
    doner_df = pd.DataFrame(doner_rows)

    # Optionally, save the separated dataframes to new CSV files
    receiver_df.to_csv('./1124_hw/receiver_data.csv', index=False)
    doner_df.to_csv('./1124_hw/doner_data.csv', index=False)

    # Display the separated dataframes
    print("Receiver Dataframe:")
    print(receiver_df.head())

    print("\nDoner Dataframe:")
    print(doner_df.head())

    return receiver_df, doner_df

if __name__ == '__main__':

    # Load the CSV into a DataFrame
    df = pd.read_csv(inputFileName)

    # Prep
    df_r, df_d = data_preprocessing(df)

    # Compare receiver and doner dataframes
    arcs_rows = []

    # Loop through each row in the DataFrame
    for index_r, row_r in df_r.iterrows():
        for index_d, row_d in df_d.iterrows():
            if (-10 <= int(row_r['Rage']) - int(row_d['Dage']) <= 10): # Rule 1
                if (-10 <= int(row_r['Rage']) - int(row_d['Dage']) <= 10): # Rule 2
                    if (-10 <= int(row_r['Rage']) - int(row_d['Dage']) <= 10): # Rule 3
                        arcs_rows.append({
                            'ID_R': row_r['ID'],
                            'ID_D': row_d['ID'],
                            'RBT': row_r['RBT'],
                            'DBT': row_d['DBT'],
                            'Rage': row_r['Rage'],
                            'Dage': row_d['Dage'],
                            'Location_r': row_r['Location'],
                            'Location_d': row_d['Location']
                        })

    # Convert the lists of rows to DataFrames
    arcs_df = pd.DataFrame(arcs_rows)

    # Optionally, save the separated dataframes to new CSV files
    arcs_df.to_csv('./1124_hw/arcs.csv', index=False)

    # Display the separated dataframes
    print("Arcs Dataframe:")
    print(arcs_df.head())


