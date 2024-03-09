import pandas as pd

# Define the CSV file path
csv_file_path = './Data/computer_scientists_data.csv'

# Define column data types and handle missing values
dtypes = {'Surname': str, 'Awards': str, 'Education': str, 'DBLP Info': str}

# Read the CSV file using pandas and handle missing values
df = pd.read_csv(csv_file_path, dtype=dtypes, na_values='NA')

# Display the first row of the DataFrame
print("Original DataFrame size:")
print(df.shape)

# Remove rows where 'Education' field is empty
df = df.dropna(subset=['Education'])

# Print the new size of the DataFrame
print("\nDataFrame after removing rows with no education size:")
print(df.shape)
