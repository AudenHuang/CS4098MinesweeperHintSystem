import pandas as pd

# Load the CSV data
file_path = '../../test/smart_output.csv'
data = pd.read_csv(file_path)
data = data.sort_values(by='Probability')
# Define the bins and labels for categorization
bins = [0, 10, 20, 30, 40, 50, 50.001, 60, 70, 80, 90, 100]
labels = ['0.01-9.99', '10.00-19.99', '20.00-29.99', '30.00-39.99', '40.00-49.99','50.00','50.01-59.99', '60.00-69.99', '70.00-79.99', '80.00-89.99', '90.00-99.99']

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
    actual_prob = round(actual_prob * 100, 2)

    # Append to summary DataFrame
    summary = summary.append({
        'Predicted Probability': label,
        'Mine': mine_count,
        'Not Mine': not_mine_count,
        'Actual Probability': actual_prob
    }, ignore_index=True)

# Print or save the summary DataFrame
print(summary)