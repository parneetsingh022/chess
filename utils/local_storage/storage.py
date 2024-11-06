import pickle

def store_data(data, filename):
    """Store data to a file using pickle."""
    with open(filename, 'wb') as file:
        pickle.dump(data, file)

def retrieve_data(filename):
    """Retrieve data from a file using pickle. Return None if the file does not exist."""
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        return data
    except FileNotFoundError:
        return None