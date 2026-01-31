def format_data(data):
    # Function to format data for display
    formatted_data = []
    for row in data:
        formatted_row = {key: str(value) for key, value in row.items()}
        formatted_data.append(formatted_row)
    return formatted_data

def save_to_csv(data, file_path):
    # Function to save data to a CSV file
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

def load_from_csv(file_path):
    # Function to load data from a CSV file
    import pandas as pd
    return pd.read_csv(file_path).to_dict(orient='records')