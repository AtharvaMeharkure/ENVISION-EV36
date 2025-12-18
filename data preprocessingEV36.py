


import pandas as pd

df = pd.read_csv("fake_news_analysis.csv")

print(df.head())

print(df.info())
import pandas as pd
import matplotlib.pyplot as plt

# ===============================
# 1. Load Dataset
# ===============================
def load_data(filepath):
    df = pd.read_csv(filepath)
    print("Dataset Loaded:", df.shape)
    return df


# ===============================
# 2. Preprocessing Function
# ===============================
def preprocess_data(df):
    # Drop critical missing values
    df.dropna(subset=["title", "source", "domain"], inplace=True)
    df.fillna(0, inplace=True)

    # Convert date columns
    df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")
    df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")

    # Convert boolean columns
    bool_cols = [
        "is_credible_source",
        "has_suspicious_tld",
        "has_suspicious_pattern",
        "has_excessive_caps",
        "has_clickbait_pattern",
        "has_unattributed_claims",
        "has_citation",
        "has_statistics"
    ]

    for col in bool_cols:
        df[col] = df[col].astype(str).map({"TRUE": 1, "FALSE": 0})

    # Feature engineering
    df["risk_category"] = df["risk_score"].apply(
        lambda x: "High Risk" if x >= 0.6 else "Medium Risk" if x >= 0.3 else "Low Risk"
    )

    df["content_intensity"] = (
        df["emotional_score"] +
        df["sensational_count"] +
        df["bias_count"]
    )

    # Remove duplicates
    df.drop_duplicates(subset=["title", "source"], inplace=True)

    print("Preprocessing Completed:", df.shape)
    return df


# ===============================
# 3. Save Preprocessed Data
# ===============================
def save_preprocessed_data(df, filename="preprocessed_data.csv"):
    df.to_csv(filename, index=False)
    print(f"Preprocessed data saved as '{filename}'")


# ===============================
# 4. Visualization (EDA)
# ===============================
def generate_visualizations(df):
    # Risk Category Distribution
    plt.figure()
    df["risk_category"].value_counts().plot(kind="bar")
    plt.title("Risk Category Distribution")
    plt.xlabel("Risk Category")
    plt.ylabel("Number of Articles")
    plt.show()

    # Credibility vs Emotional Score
    plt.figure()
    plt.scatter(df["credibility_score"], df["emotional_score"])
    plt.title("Credibility vs Emotional Score")
    plt.xlabel("Credibility Score")
    plt.ylabel("Emotional Score")
    plt.show()


# ===============================
# 5. Main Execution
# ===============================
if __name__ == "__main__":
    df_raw = load_data("fake_news_analysis.csv")
    df_clean = preprocess_data(df_raw)
    save_preprocessed_data(df_clean)
    generate_visualizations(df_clean)
