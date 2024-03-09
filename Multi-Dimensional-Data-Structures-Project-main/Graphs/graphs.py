import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def read_csv_file(file_path: str) -> pd.DataFrame:
    """Reads a CSV file and returns a pandas DataFrame.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The data from the CSV file as a pandas DataFrame.

    """
    return pd.read_csv(file_path)

def plot_data(df: pd.DataFrame):
    """Plots the data from the DataFrame.

    Args:

        df (pd.DataFrame): The DataFrame containing the data.

    """
    trees = df['Tree'].unique()
    input_sizes = df['Input Size'].unique()

        # Custom color palette
    sns.set_palette(['#21B5C0', '#90A33E', '#E06615', '#730D0D'])

    # Add a new column for the total time
    df['Total Time'] = df['Build Time'] + df['Search Time'] + df['LSH Time']


    #Plot for each tree at input size 40000
    df_40000 = df[df['Input Size'] == 40000]
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Tree', y='Build Time', data=df_40000)
    plt.title('Build Time for different trees at Input Size 40000')
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Tree', y='Search Time', data=df_40000)
    plt.title('Search Time for different trees at Input Size 40000')
    plt.show()

    # Plot for each tree at different input sizes on the same plot
    plt.figure(figsize=(10, 6))
    for tree in trees:
        df_tree = df[df['Tree'] == tree]
        sns.lineplot(x='Input Size', y='Build Time', data=df_tree, marker='o', label=tree)
    plt.title('Build Time for different trees at different Input Sizes')
    plt.grid(True)
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 6))
    for tree in trees:
        df_tree = df[df['Tree'] == tree]
        sns.lineplot(x='Input Size', y='Search Time', data=df_tree, marker='o', label=tree)
    plt.title('Search Time for different trees at different Input Sizes')
    plt.grid(True)
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 6))
    for tree in trees:
        df_tree = df[df['Tree'] == tree]
        sns.lineplot(x='Input Size', y='Total Time', data=df_tree, marker='o', label=tree)
    plt.title('Total Time for different trees at different Input Sizes')
    plt.grid(True)
    plt.legend()
    plt.show()

        # Plot for average LSH Time for each input size
    df_avg_lsh_time = df.groupby('Input Size')['LSH Time'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Input Size', y='LSH Time', data=df_avg_lsh_time, marker='o')
    plt.title('Average LSH Time for different Input Sizes')
    plt.grid(True)
    plt.show()

# Use the functions
df = read_csv_file(r'Graphs\times.csv')
plot_data(df)