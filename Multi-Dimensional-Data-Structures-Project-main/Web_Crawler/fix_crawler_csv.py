import pandas as pd

# Read the CSV file
df = pd.read_csv("Data/computer_scientists_data.csv")

# Delete rows where the third column is NaN
df.dropna(subset=[df.columns[2]], inplace=True)

# Write the DataFrame back to CSV
df.to_csv("Data/new_computer_scientists_data", index=False)
