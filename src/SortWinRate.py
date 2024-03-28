import pandas as pd

def process_winrate_file(difficulty):
    # Define the file path based on the difficulty
    file_path = f'../../test/winrate_{difficulty}.csv'
    
    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return
    
    # Calculate total wins and total games played
    total_wins = df['won'].sum()
    total_games = len(df['won'])
    
    # Calculate win rate
    win_rate = (total_wins / total_games) * 100
    
    # Create a table for display
    table = pd.DataFrame({
        "Total Win": [total_wins],
        "Game Played": [total_games],
        "Win Rate (%)": [win_rate]
    })
    
    print(table)

if __name__ == "__main__":
    difficulty = input("Enter difficulty (Easy, Intermediate, Expert): ").capitalize()
    if difficulty in ["Easy", "Intermediate", "Expert"]:
        process_winrate_file(difficulty)
    else:
        print("Invalid difficulty. Please choose from Easy, Intermediate, or Expert.")
