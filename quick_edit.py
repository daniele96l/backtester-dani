import pandas as pd

# Load the CSV file
df = pd.read_csv('/Users/danieleligato/PycharmProjects/DaniBacktester/data/Index_list.csv')

# Ensure that we handle NaN values before applying str.contains
if 'Index' in df.columns:
    df = df[df['Index'].notna()]  # Exclude rows with NaN in the 'Index' column
    df = df[~df['Index'].str.contains('/')]

# Save the cleaned DataFrame to a new file
df.to_csv('/Users/danieleligato/PycharmProjects/DaniBacktester/data/Index_list_cleaned.csv', index=False)

print("File cleaned and saved successfully!")
