import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_monthly_averages(filepath, output_dir="visualizations"):
    """
    Performs monthly aggregation and saves plots:
    - Avg grid use per month
    - Avg solar output per month
    - Avg percent renewable per month
    - Avg CO2 emissions per month
    """
    # Load the data
    df = pd.read_csv(filepath)

    # Aggregate data by month
    monthly_agg = df.groupby("Month").agg({
        "Grid_Energy_Use_kWh": "mean",
        "Dedicated_Solar_Output_kWh": "mean",
        "CO2_Emissions_US_avg": "mean",
        "CO2_Emissions_VT_avg": "mean"
    }).reset_index()

    # Ensure months are in the correct order
    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    monthly_agg["Month"] = pd.Categorical(monthly_agg["Month"], categories=month_order, ordered=True)
    monthly_agg = monthly_agg.sort_values("Month")

    # Set plot style and color palette
    sns.set(style="whitegrid")
    palette = sns.color_palette("viridis", len(month_order))

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Plot definitions
    plots = {
        "Grid_Energy_Use_kWh": "Average Grid Energy Use per Month (kWh)",
        "Dedicated_Solar_Output_kWh": "Average Solar Output per Month (kWh)",
        "CO2_Emissions_US_avg": "Average CO2 Emissions per Month (US Avg)",
        "CO2_Emissions_VT_avg": "Average CO2 Emissions per Month (VT Avg)"
    }

    for col, title in plots.items():
        plt.figure(figsize=(12, 6))
        sns.barplot(data=monthly_agg, x="Month", y=col, palette=palette)
        plt.title(title)
        plt.ylabel(col.replace("_", " "))
        plt.xticks(rotation=45)
        plt.tight_layout()
        output_path = os.path.join(output_dir, f"{col}.png")
        plt.savefig(output_path)
        plt.close()
    
    # Monthly comparison heatmap
    heatmap_data = monthly_agg.set_index("Month")
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data.T, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Avg Value'})
    plt.title("Monthly Comparison of Key Energy Metrics")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "monthly_variable_comparison_heatmap.png"))
    plt.close()

    # Correlation heatmap
    corr = heatmap_data.corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, fmt=".2f", cbar_kws={'label': 'Correlation'})
    plt.title("Correlation Between Monthly Averages")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"))
    plt.close()

    print(f"Plots saved to: {output_dir}")
    return monthly_agg

def calculate_cumulative_impact(filepath, output_dir="visualizations"):
    """
    Calculates and plots cumulative:
    - Grid energy avoided
    - Emissions avoided
    - Cost savings
    """
    df = pd.read_csv(filepath)

    # Sort chronologically by Month and Day
    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
    df = df.sort_values(["Month", "Day"]).reset_index(drop=True)

    # Calculations
    df["Grid_Energy_Avoided"] = df["Total_Energy_Use_kWh"] - df["Grid_Energy_Use_kWh"]

    # Emissions avoided (approximate, based on if all energy came from grid)
    df["Emissions_If_All_Grid"] = (df["Total_Energy_Use_kWh"] / df["Grid_Energy_Use_kWh"]) * df["CO2_Emissions_US_avg"]
    df["Emissions_Avoided"] = df["Emissions_If_All_Grid"] - df["CO2_Emissions_US_avg"]

    # Cost savings (approximate, if all energy came from grid)
    df["Cost_If_All_Grid"] = (df["Total_Energy_Use_kWh"] / df["Grid_Energy_Use_kWh"]) * df["Cost_from_Grid_$"]
    df["Cost_Savings"] = df["Cost_If_All_Grid"] - df["Cost_from_Grid_$"]

    # Cumulative sums
    df["Cumulative_Grid_Avoided"] = df["Grid_Energy_Avoided"].cumsum()
    df["Cumulative_Emissions_Avoided"] = df["Emissions_Avoided"].cumsum()
    df["Cumulative_Cost_Savings"] = df["Cost_Savings"].cumsum()

    # Plotting
    os.makedirs(output_dir, exist_ok=True)
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 6))
    plt.plot(df["Cumulative_Grid_Avoided"], label="Grid Energy Avoided (kWh)")
    plt.plot(df["Cumulative_Emissions_Avoided"], label="Emissions Avoided (kg CO2)")
    plt.plot(df["Cumulative_Cost_Savings"], label="Cost Savings ($)")
    plt.title("Cumulative Impact Over the Year")
    plt.xlabel("Day of Year")
    plt.ylabel("Cumulative Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cumulative_impact.png"))
    plt.close()

    print("Cumulative impact plot saved.")
    return df[["Cumulative_Grid_Avoided", "Cumulative_Emissions_Avoided", "Cumulative_Cost_Savings"]]

def highlight_key_threshold_days(filepath, output_dir="visualizations"):
    """
    Identifies and visualizes:
    - 100% renewable days
    - Very high grid use days
    - PUE spike days
    """
    df = pd.read_csv(filepath)

    # Create Day-of-Year column for time axis
    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
    df = df.sort_values(["Month", "Day"]).reset_index(drop=True)
    df["Day_of_Year"] = range(1, len(df) + 1)

    # Thresholds
    high_grid_threshold = df["Grid_Energy_Use_kWh"].quantile(0.95)
    pue_spike_threshold = df["PUE"].quantile(0.95)

    # Flagging days
    df["Is_100pct_Renewable"] = df["Percent_Renewable"] == 1.0
    df["Is_High_Grid"] = df["Grid_Energy_Use_kWh"] > high_grid_threshold
    df["Is_PUE_Spike"] = df["PUE"] > pue_spike_threshold

    # Plotting
    os.makedirs(output_dir, exist_ok=True)
    sns.set(style="whitegrid")

    # Grid Use Scatter
    plt.figure(figsize=(12, 5))
    sns.scatterplot(x="Day_of_Year", y="Grid_Energy_Use_kWh", data=df, label="Normal", color="gray")
    sns.scatterplot(x="Day_of_Year", y="Grid_Energy_Use_kWh", data=df[df["Is_High_Grid"]],
                    label="High Grid Use", color="red")
    plt.title("Grid Energy Use with High-Use Days Highlighted")
    plt.xlabel("Day of Year")
    plt.ylabel("Grid Energy Use (kWh)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "high_grid_use_days.png"))
    plt.close()

    # Renewable Coverage
    plt.figure(figsize=(12, 5))
    sns.scatterplot(x="Day_of_Year", y="Percent_Renewable", data=df, color="gray", label="Normal")
    sns.scatterplot(x="Day_of_Year", y="Percent_Renewable", data=df[df["Is_100pct_Renewable"]],
                    color="green", label="100% Renewable")
    plt.title("Days with 100% Renewable Energy Use")
    plt.xlabel("Day of Year")
    plt.ylabel("Percent Renewable")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "100pct_renewable_days.png"))
    plt.close()

    # PUE Spikes
    plt.figure(figsize=(12, 5))
    sns.scatterplot(x="Day_of_Year", y="PUE", data=df, color="gray", label="Normal")
    sns.scatterplot(x="Day_of_Year", y="PUE", data=df[df["Is_PUE_Spike"]],
                    color="purple", label="PUE Spike")
    plt.title("PUE Over Time with Spike Days Highlighted")
    plt.xlabel("Day of Year")
    plt.ylabel("Power Usage Effectiveness (PUE)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "pue_spike_days.png"))
    plt.close()

    print("Threshold plots saved.")
    return df[df["Is_100pct_Renewable"] | df["Is_High_Grid"] | df["Is_PUE_Spike"]][
        ["Month", "Day", "Percent_Renewable", "Grid_Energy_Use_kWh", "PUE"]
    ]


# Example usage
if __name__ == "__main__":
    data_path = os.path.join("Data", "Data.csv")
    output_path = "visualizations"
    if os.path.exists(data_path):
        df_summary = analyze_monthly_averages(data_path, output_path)
        print(df_summary)
        cumulative_df = calculate_cumulative_impact(data_path, output_path)
        print(cumulative_df.tail())
        threshold_days = highlight_key_threshold_days(data_path, output_path)
        print(threshold_days.head())
    else:
        print(f"File not found: {data_path}")
