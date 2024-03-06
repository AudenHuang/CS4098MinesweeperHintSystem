import pandas as pd

# Load the CSV data
file_path = '../../test/smart_output.csv'
data = pd.read_csv(file_path)

# Define the bins and labels for categorization
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
labels = ['1-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99']

# Categorize probabilities
data['Range'] = pd.cut(data['Probability'], bins=bins, labels=labels, right=False)

# Initialize the summary DataFrame
summary = pd.DataFrame(columns=['Predicted Probability', 'Mine', 'Not Mine', 'Actual Probability'])

for label in labels:
    # Subset data for the current range
    range_data = data[data['Range'] == label]
    
    # Count mines and not mines
    mine_count = range_data['IsAMine'].sum()
    not_mine_count = len(range_data) - mine_count
    
    # Calculate actual probability
    actual_prob = mine_count / (mine_count + not_mine_count) if (mine_count + not_mine_count) > 0 else 0
    
    # Append to summary DataFrame
    summary = summary.append({
        'Predicted Probability': label,
        'Mine': mine_count,
        'Not Mine': not_mine_count,
        'Actual Probability': actual_prob *100
    }, ignore_index=True)

# Print or save the summary DataFrame
print(summary)
