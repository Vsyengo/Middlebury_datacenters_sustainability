from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def model_grid_dependence(filepath, output_dir="visualizations"):
    """
    Uses regression to model and interpret which subsystems influence grid energy use.
    """
    df = pd.read_csv(filepath)

    # Prepare feature matrix and target
    features = ["IT_Equipment_kWh", "Cooling_kWh", "Lighting_KWh", "Dedicated_Solar_Output_kWh"]
    X = df[features]
    y = df["Grid_Energy_Use_kWh"]

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predictions and metrics
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))

    # Coefficients
    coef_df = pd.DataFrame({
        "Feature": features,
        "Coefficient": model.coef_
    }).sort_values(by="Coefficient", ascending=False)

    # Plot coefficients
    plt.figure(figsize=(10, 5))
    sns.barplot(data=coef_df, x="Feature", y="Coefficient", palette="crest")
    plt.title("Linear Regression Coefficients for Grid Energy Use")
    plt.ylabel("Influence on Grid Energy Use (kWh)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "regression_coefficients.png"))
    plt.close()

    # Residual plot
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x=y_pred, y=y - y_pred, color="teal")
    plt.axhline(0, color="black", linestyle="--")
    plt.title("Residual Plot")
    plt.xlabel("Predicted Grid Energy Use")
    plt.ylabel("Residuals")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "residual_plot.png"))
    plt.close()

    print(f"Regression R² score: {r2:.4f}, RMSE: {rmse:.2f}")
    return coef_df, r2, rmse


if __name__ == "__main__":
    data_path = os.path.join("Data", "Data.csv")
    output_path = "visualizations"
    if os.path.exists(data_path):
        coef_df, r2, rmse = model_grid_dependence(data_path, output_path)
        print("\nRegression Coefficients:")
        print(coef_df)
        print(f"\nR²: {r2:.4f} | RMSE: {rmse:.2f}")
        