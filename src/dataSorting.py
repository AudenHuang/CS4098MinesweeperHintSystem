import pandas as pd

# Load the CSV data
file_path = '../../data/output.csv'
data = pd.read_csv(file_path)
data = data.sort_values(by='Probability')

# Specific values you're interested in
values = [10.00, 11.11, 12.50, 14.29, 16.67, 20.00, 25.00, 33.33, 50.00]
# Convert to string for labeling purposes
labels = [str(value) for value in values]

# Function to categorize each probability
def categorize_probability(prob, values):
    # Find the closest value
    closest_value = min(values, key=lambda x:abs(x-prob))
    return str(closest_value)

# Categorize probabilities based on specific values
data['Range'] = data['Probability'].apply(lambda x: categorize_probability(x, values))

# Initialize the summary DataFrame
summary = pd.DataFrame(columns=['Predicted Probability', 'Mine', 'Total', 'Actual Probability'])

for value in labels:
    # Subset data for the current value
    range_data = data[data['Range'] == value]
    
    # Count mines and not mines
    mine_count = range_data['IsAMine'].sum()
    total_count = len(range_data)
    
    # Calculate actual probability
    actual_prob = mine_count / total_count if  total_count > 0 else 0
    actual_prob = round(actual_prob * 100, 2)

    # Append to summary DataFrame
    summary = summary.append({
        'Predicted Probability': value,
        'Mine': mine_count,
        'Total': total_count,
        'Actual Probability': actual_prob
    }, ignore_index=True)

# Print or save the summary DataFrame
print(summary)
