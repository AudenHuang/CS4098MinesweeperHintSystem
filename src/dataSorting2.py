import pandas as pd

# Load the CSV data
file_path = '../../test/smart_output.csv'

data = pd.read_csv(file_path)
bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
labels = ['1-4', '4-9', '10-14', '15-19', '20-24','25-29', '30-34', '35-39', '40-44', '45-49', '50-54','55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99']
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