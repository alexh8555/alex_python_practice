import pandas as pd
import gurobipy as gp
from gurobipy import GRB

##############CONFIG################
inputFileName = './1124_hw/pairs.csv'
distanceFileName = './1124_hw/distances.csv'
age_threshold = 10
dist_threshold = 300
####################################

def data_seprate(df):
    # Initialize the lists to hold rows for receiver and donor dataframes
    receiver_rows = []
    donor_rows = []

    # Loop through each row in the original DataFrame
    for _, row in df.iterrows():
        if row['type'] == 'receiver':
            # Add the relevant columns to the receiver rows list
            receiver_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'RBT': row['RBT'],
                'Rage': row['Rage'],
                'Location': row['Location']
            })

        elif row['type'] == 'donor':
            # Add the relevant columns to the donor rows list
            donor_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'DBT': row['DBT'],
                'Dage': row['Dage'],
                'Location': row['Location']
            })

        elif row['type'] == 'pair':
            # Add the relevant columns to both receiver and donor rows lists
            receiver_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'RBT': row['RBT'],
                'Rage': row['Rage'],
                'Location': row['Location']
            })

            donor_rows.append({
                'ID': row['ID'],
                'type': row['type'],
                'DBT': row['DBT'],
                'Dage': row['Dage'],
                'Location': row['Location']
            })

    # Convert the lists of rows to DataFrames
    receiver_df = pd.DataFrame(receiver_rows)
    doner_df = pd.DataFrame(donor_rows)

    # Optionally, save the separated dataframes to new CSV files
    receiver_df.to_csv('./1124_hw/receiver_data.csv', index=False)
    doner_df.to_csv('./1124_hw/donor_data.csv', index=False)

    # Display the separated dataframes
    print("Receiver Dataframe:")
    print(receiver_df.head())

    print("\nDoner Dataframe:")
    print(doner_df.head())

    return receiver_df, doner_df

def data_make_arcs(df_r, df_d, df_dist):
    # Compare receiver and doner dataframes
    arcs_rows = []

    # Loop through each row in the DataFrame
    for _, row_r in df_r.iterrows():
        for _, row_d in df_d.iterrows():
            age_diff = int(row_r['Rage']) - int(row_d['Dage'])
            if (abs(age_diff) <= age_threshold): # Rule 1
                dist = get_dist(df_dist, row_r['Location'], row_d['Location'])
                if (dist <= dist_threshold): # Rule 2
                    bt_ok = check_blood_type(row_r['RBT'], row_d['DBT'])
                    if (bt_ok): # Rule 3
                        arcs_rows.append({
                            'ID_R': row_r['ID'],
                            'ID_D': row_d['ID'],
                            # 'RBT': row_r['RBT'],
                            # 'DBT': row_d['DBT'],
                            # 'Rage': row_r['Rage'],
                            # 'Dage': row_d['Dage'],
                            'Rtype': row_r['type'],
                            'Dtype': row_d['type'],
                            # 'Location_r': row_r['Location'],
                            # 'Location_d': row_d['Location'],
                            # 'Dist': dist
                        })

    # Convert the lists of rows to DataFrames
    arcs_df = pd.DataFrame(arcs_rows)

    # Optionally, save the separated dataframes to new CSV files
    arcs_df.to_csv('./1124_hw/arcs.csv', index=False)

    # Display the separated dataframes
    print("Arcs Dataframe:")
    print(arcs_df.head())

    return arcs_df

def get_dist(df_dist, loc1, loc2):

    dist = 0

    if loc1 == loc2:
        return dist

    # Loop through each row in the DataFrame
    for _, row in df_dist.iterrows():
        if (loc1 == row['city1'] and loc2 == row['city2']):
            dist = row['distance']
            break

    # print(f'[DEBUG] loc1:{loc1}, loc2:{loc2}, dist:{dist}')

    return dist

def check_blood_type(rbt, dbt):

    blood_compatibility = {
        'O': ['O', 'A', 'B', 'AB'],
        'A': ['A', 'AB'],
        'B': ['B', 'AB'],
        'AB': ['AB']
    }

    if rbt in blood_compatibility[dbt]:
        return True
    else:
        return False

def run_model(df_arcs):
    # Extract unique nodes
    nodes = set(df_arcs['ID_R']).union(set(df_arcs['ID_D']))
    arcs = [(row['ID_D'], row['ID_R']) for _, row in df_arcs.iterrows()]

    # Create subsets based on types
    pair_donors = set(df_arcs.loc[df_arcs['Dtype'] == 'pair', 'ID_D'])
    pair_receivers = set(df_arcs.loc[df_arcs['Rtype'] == 'pair', 'ID_R'])
    donors = set(df_arcs.loc[df_arcs['Dtype'] == 'donor', 'ID_D'])
    receivers = set(df_arcs.loc[df_arcs['Rtype'] == 'receiver', 'ID_R'])

    # Initialize the model
    model = gp.Model("Kidney_Exchange")

    # Decision variables: x[i, j] = 1 if donor i donates to receiver j
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")

    # Objective: Maximize the number of donations
    model.setObjective(gp.quicksum(x[i, j] for i, j in arcs), GRB.MAXIMIZE)

    # Constraints

    # 1. Each donor can only donate once
    for donor in nodes:
        out_arcs = [(donor, j) for j in nodes if (donor, j) in arcs]
        model.addConstr(gp.quicksum(x[i, j] for i, j in out_arcs) <= 1)

    # 2. Each receiver can only receive once
    for receiver in nodes:
        in_arcs = [(i, receiver) for i in nodes if (i, receiver) in arcs]
        model.addConstr(gp.quicksum(x[i, j] for i, j in in_arcs) <= 1)

    # 3. Pair donors can only donate if they receive a kidney
    for pair in pair_donors:
        in_arcs = [(i, pair) for i in nodes if (i, pair) in arcs]
        out_arcs = [(pair, j) for j in nodes if (pair, j) in arcs]
        model.addConstr(gp.quicksum(x[i, j] for i, j in in_arcs) >= gp.quicksum(x[i, j] for i, j in out_arcs))

    # 4. Pair receivers must receive a kidney before donating
    for pair in pair_receivers:
        in_arcs = [(i, pair) for i in nodes if (i, pair) in arcs]
        out_arcs = [(pair, j) for j in nodes if (pair, j) in arcs]
        model.addConstr(gp.quicksum(x[i, j] for i, j in in_arcs) >= gp.quicksum(x[i, j] for i, j in out_arcs))

    # Optimize the model
    model.optimize()

    # Extract results
    if model.Status == GRB.OPTIMAL:
        solution = [(i, j) for i, j in arcs if x[i, j].X > 0.5]
        print("Optimal Kidney Exchanges:", solution)
    else:
        print("No optimal solution found.")

if __name__ == '__main__':

    # Load the CSV into a DataFrame
    df = pd.read_csv(inputFileName)
    df_dist = pd.read_csv(distanceFileName)

    # Prep
    df_r, df_d = data_seprate(df)

    # Compare receiver and doner dataframes
    df_arcs = data_make_arcs(df_r, df_d, df_dist)

    run_model(df_arcs)



    # I love jocelyn