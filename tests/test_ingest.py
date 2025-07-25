import pandas as pd

# Step 1: Create test DataFrame
df = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "score": [85.5, 92.0, 78.3]
})

# Step 2: Save to CSV
output_path = "test_data.csv"
df.to_csv(output_path, index=False)

print(f"Test CSV saved to: {output_path}")
