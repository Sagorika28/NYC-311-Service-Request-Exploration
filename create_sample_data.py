import pandas as pd
from pathlib import Path

def create_sample_data():
    base_dir = Path(r"d:\UW\Q4\HCDS\Final Project\A7")
    input_path = base_dir / "data" / "processed" / "nyc311_2024_cleaned.parquet"
    output_dir = base_dir / "data" / "sample"
    output_path = output_dir / "nyc311_2024_sample.parquet"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading full dataset from: {input_path}")
    try:
        df = pd.read_parquet(input_path)
        print(f"Full dataset shape: {df.shape}")

        # Sample 1000 rows
        sample_size = 1000
        if len(df) > sample_size:
            df_sample = df.sample(n=sample_size, random_state=42)
        else:
            df_sample = df
            
        print(f"Sample dataset shape: {df_sample.shape}")

        df_sample.to_parquet(output_path)
        print(f"Sample dataset saved to: {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_sample_data()