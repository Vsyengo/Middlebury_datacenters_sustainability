import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def check_data_quality(filepath):
    """
    Load a dataset and perform basic data quality checks:
    - Missing values
    - Summary statistics
    - Boxplots to detect outliers
    """

    # Load data
    df = pd.read_csv(filepath)


    # Summary statistics for selected columns 
    key_columns = [
        'Grid_Energy_Use_kWh',
        'Dedicated_Solar_Output_kWh',
        'Total_Energy_Use_kWh',
        'Battery_Storage_Used_kWh',
        'PUE'
    ]
    
    print("Summary Statistics:")
    print(df[key_columns].describe())
    print("\n" + "-"*50 + "\n")

    # Boxplots to check for outliers 
    plt.figure(figsize=(15, 6))
    for i, col in enumerate(key_columns, 1):
        plt.subplot(1, len(key_columns), i)
        sns.boxplot(y=df[col])
        plt.title(col)
    plt.tight_layout()
    plt.suptitle("Outlier Detection via Boxplots", y=1.05)
    plt.show()

    return df

# (when running this script directly):
if __name__ == "__main__":
    # data file
    filepath = "Data/Data.csv"
    df_cleaned = check_data_quality(filepath)



