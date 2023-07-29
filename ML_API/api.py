# api.py
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import glob
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename
import traceback
import logging

import datetime
from db_connector import get_database_connection

app = Flask(__name__)
CORS(app)
connection = get_database_connection()
cursor = connection.cursor()

# Define the required features for the model
required_features = ["Date/Time", "Voltage Ph-A Avg", "Voltage Ph-B Avg", "Voltage Ph-C Avg", "Current Ph-A Avg", "Current Ph-B Avg", "Current Ph-C Avg"
                     ,"Power Factor Total","Power Ph-A","Power Ph-B","Power Ph-C", "Total Power"]

def load_lstm_model(version):
    # weekday model folder path
    lstm_model_folder = f"models/LSTM/{version}"
    
    # Check if the specified version exists
    if not os.path.exists(lstm_model_folder):
        # If the version does not exist, get the latest version available
        model_versions = glob.glob(f"models/LSTM/*")
        if not model_versions:
            raise ValueError("No LSTM model versions found.")
        model_versions.sort(reverse=True)
        latest_version = model_versions[0]
        print(f"Warning: Version {version} not found. Using the latest available version: {latest_version}")
        lstm_model_folder = latest_version
    
    # Load the model
    model = load_model(lstm_model_folder)
    return model


# load the weekend/holiday model version
def load_svr_model(model_type, version):
    # SVR model folder path
    svr_model_folder = f"models/SVR/{model_type}/{version}"
    
    # Check if the specified version exists
    if not os.path.exists(svr_model_folder):
        # If the version does not exist, get the latest version available
        model_versions = glob.glob(f"models/SVR/{model_type}/*")
        if not model_versions:
            raise ValueError(f"No {model_type} model versions found.")
        model_versions.sort(reverse=True)
        latest_version = model_versions[0]
        print(f"Warning: Version {version} not found. Using the latest available version: {latest_version}")
        svr_model_folder = latest_version
    
    # Load the model using joblib
    model = joblib.load(svr_model_folder)
    return model


def save_data_database(data):
    try:
        preprocessed_data = preprocess_data(data)

        # Convert the "Date/Time" column to the desired MySQL datetime format
        preprocessed_data["Date/Time"] = pd.to_datetime(preprocessed_data["Date/Time"], infer_datetime_format=True)
        preprocessed_data["Date/Time"] = preprocessed_data["Date/Time"].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Iterate over the rows of the DataFrame and insert each row into the database
        for index, row in preprocessed_data.iterrows():
            values = tuple(row[required_features])
            query = "INSERT INTO Energy_Data (`Date/Time`, `Voltage Ph-A Avg`, `Voltage Ph-B Avg`, `Voltage Ph-C Avg`, `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`, `Power Factor Total`, `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power`) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)"
            cursor.execute(query, values)

        connection.commit()

    except Exception as e:
        connection.rollback()
        raise ValueError("Error saving data to database: " + str(e))
    finally:
        cursor.close()
        connection.close()

def get_model_for_date(date, cursor, version):
    if date.weekday() < 5:
        return load_lstm_model(version)
    elif date.weekday() >= 5:
        return load_svr_model("SVR_weekend", version)
    elif is_holiday(date):
        return load_svr_model("SVR_holiday", version)
    else:
        return load_lstm_model(version)


def is_holiday(date):
    try:
        query = "SELECT date FROM holidays"
        cursor.execute(query)
        holiday_dates = [row[0] for row in cursor.fetchall()]
        if date in holiday_dates:
            return True
        else:
            return False
    # Check if the current_date is in the list of holiday_dates
    except Exception as e:
            raise ValueError("Error getting holidays from database: " + str(e))
    

def preprocess_data(data, method='locf'):
    
    try:
        # Handle missing values
        if method == 'locf' and data.isnull().any().any():
            # Fill missing values with the last observed value
            data.fillna(method='ffill', inplace=True)
        elif method == 'bocf' and data.isnull().any().any():
            # Fill missing values with the next observed value
            data.fillna(method='bfill', inplace=True)
        
        # Add features
        data = add_features(data)

        return data

    except Exception as e:
        raise ValueError("Error preprocessing data: " + str(e))


def add_features(data):
    data['Power Ph-A'] = data['Voltage Ph-A Avg'] * \
        data['Current Ph-A Avg'] * abs(data['Power Factor Total'])
    data['Power Ph-B'] = data['Voltage Ph-B Avg'] * \
        data['Current Ph-B Avg'] * abs(data['Power Factor Total'])
    data['Power Ph-C'] = data['Voltage Ph-C Avg'] * \
        data['Current Ph-C Avg'] * abs(data['Power Factor Total'])
    data['Total Power'] = data['Power Ph-A'] + data['Power Ph-B'] + data['Power Ph-C']
    return data

def get_last_weekend():
    query = "SELECT `Date/Time`, `Voltage Ph-A Avg`, `Voltage Ph-B Avg`, `Voltage Ph-C Avg`, `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`, `Power Factor Total`, `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power` FROM Energy_Data WHERE `Date/Time` BETWEEN (SELECT MAX(`Date/Time`) FROM Energy_Data WHERE WEEKDAY(`Date/Time`) = 5) AND (SELECT MAX(`Date/Time`) FROM Energy_Data WHERE WEEKDAY(`Date/Time`) = 6) ORDER BY `Date/Time` DESC LIMIT 48"
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) >= 48:
        # Since the query results are in descending order, reverse the data list to get the earliest date first
        data.reverse()
        return pd.DataFrame(data, columns=required_features)
    else:
        return None

def predict_day_ahead_load(preprocessed_data, model_to_use):
    try:
        # Debug: Print the contents of the preprocessed_data DataFrame
        print("Contents of preprocessed_data:")
        print(preprocessed_data)

        # Extract the date of the first data point
        first_date = preprocessed_data["Date/Time"].iloc[0]

        # Generate the datetime index for the entire day (48 data points)
        datetime_index = pd.date_range(first_date, periods=48, freq="30T")
        
         # Debug: Print the length of the datetime_index and the number of rows in preprocessed_data
        print("Length of datetime_index in predict_day_ahead_load:", len(datetime_index))
        print("Number of rows in preprocessed_data in predict_day_ahead_load:", len(preprocessed_data))


        # Create an empty list to store the predictions
        y_pred_list = []

        # Predict for each data point in the datetime index
        for timestamp in datetime_index:
            # Find the row index corresponding to the current timestamp
            row_index = preprocessed_data.index[preprocessed_data["Date/Time"] == timestamp].tolist()
            # Debug: Print the current timestamp and the corresponding row_index
            print("Timestamp:", timestamp)
            print("Row Index:", row_index)
            if not row_index:
                # Handle the case when row_index is empty
                # You can decide to skip the prediction or use a default value for prediction
                # For now, we'll skip the prediction and continue to the next timestamp
                continue
            # if row_index:
            # Extract the relevant features for prediction
            feature_order = ["Voltage Ph-A Avg", "Voltage Ph-B Avg", "Voltage Ph-C Avg",
                            "Current Ph-A Avg", "Current Ph-B Avg", "Current Ph-C Avg",
                            "Power Factor Total", "Power Ph-A", "Power Ph-B", "Power Ph-C"]
            X_test_single = preprocessed_data[feature_order].iloc[row_index].values

            # Predict for the current data point
            y_pred_single = model_to_use.predict(X_test_single)
            # Append the predicted value to the y_pred_list
            y_pred_list.append(y_pred_single)

            # Debug: Print the length of the y_pred_list at each iteration
            print("Length of y_pred_list:", len(y_pred_list))

        # Check if the predictions list has exactly 48 elements
        if len(y_pred_list) != 48:
            raise ValueError("Prediction list does not have 48 elements")

        # Create a DataFrame to hold the predicted data for the entire day
        predicted_data_df = pd.DataFrame({"Date/Time": datetime_index, "Total Power": y_pred_list})

        # Debug: Print the shape of the predictions DataFrame
        print("Shape of predicted_data_df:", predicted_data_df.shape)

        return predicted_data_df

    except Exception as e:
        logging.error("Error during prediction: %s", e)
        raise e


@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        print("Received request data:", request.get_json())  # Add this line for debug logging
        if "file" in request.files:
            # If the file is provided, process it
            file = request.files["file"]

            # Check if the file has a name
            if file.filename == "":
                return jsonify({"error": "No selected file"}), 400

            # Check if the file is in CSV format
            if file.filename.split(".")[-1].lower() != "csv":
                return jsonify({"error": "Only CSV files are allowed"}), 400

            # Save the file to a temporary location
            file_path = os.path.join("uploads", secure_filename(file.filename))
            file.save(file_path)

            # Load the data from the file
            data = pd.read_csv(file_path)

            # Check if the DataFrame contains all the required features
            if all(feature in data.columns for feature in required_features):
                # DataFrame already contains the required features, skip preprocessing
                preprocessed_data = data
            else:
                # DataFrame is missing some required features, preprocess the data
                preprocessed_data = preprocess_data(data, method="locf")
                preprocessed_data = preprocess_data(preprocessed_data, method="bocf")

        else:
            # If the file is not provided, use JSON data
            json_data = request.get_json()
            if json_data is None:
                return jsonify({"error": "Invalid JSON data"}), 400

            # Extract the actual data from the nested "data" key and create a DataFrame
            input_data = json_data.get("data")
            if input_data is None or not isinstance(input_data, list) or len(input_data) == 0:
                return jsonify({"error": "Invalid JSON data"}), 400

            # Create a list to hold the DataFrames
            data_list = []
            # Iterate through the list and extract the nested dictionary data
            for item in input_data:
                nested_data = item.get("data")
                if nested_data is not None and isinstance(nested_data, list) and len(nested_data) > 0:
                    df = pd.DataFrame(nested_data[0])
                    data_list.append(df)

            if not data_list:
                return jsonify({"error": "Invalid JSON data"}), 400

            # Concatenate all the DataFrames into a single DataFrame
            data = pd.concat(data_list, ignore_index=True)
            # Extract the nested dictionary
            nested_data = data['data'][0]

            # Create a DataFrame from the extracted data
            data = pd.DataFrame([nested_data])
            # Preprocess the data
            preprocessed_data = preprocess_data(data)
        
        # Extract the date from the timestamp and convert to datetime object
        preprocessed_data["Date/Time"] = pd.to_datetime(preprocessed_data["Date/Time"])
        
        # Get the last weekend's data from the database
        last_weekend_data = get_last_weekend()
        
        if last_weekend_data is None:
            return jsonify({"error": "Not enough historical data available for extrapolation"}), 400

        # Debug: Print the shape of the last weekend's data DataFrame
        print("Shape of last_weekend_data:", last_weekend_data.shape)


        # Perform rolling window prediction for the day-ahead load profile (48 data points)
        predictions = []

        # Define the window size (number of past data points to use for prediction)
        window_size = 48
        
        # Select the window of data from the last weekend's data
        window_data = preprocessed_data.iloc[-window_size:]

        # Get the desired model version from the request parameters
        version = request.args.get("version")

        # Load the appropriate model based on the specified version
        if version:
            if version.startswith("lstm"):
                model_to_use = load_lstm_model(version)
            elif version.startswith("svr_weekend"):
                model_to_use = load_svr_model("weekend", version)
            elif version.startswith("svr_holiday"):
                model_to_use = load_svr_model("holiday", version)
            else:
                return jsonify({"error": "Invalid model version"}), 400
        else:
            # If no version specified, use the default models
            model_to_use = get_model_for_date(preprocessed_data["Date/Time"].iloc[0], cursor, version)
        print(model_to_use)

        # Predict the next 48 data points using extrapolation
        predictions = predict_day_ahead_load(last_weekend_data, model_to_use)

        # Assuming predictions is a pandas Series or numpy array containing the predicted values
        predicted_data_df = pd.DataFrame(predictions, columns=["Total Power"])
        predicted_data_df.reset_index(inplace=True)
        predicted_data_df.rename(columns={"index": "Date/Time"}, inplace=True)
        # Convert the predicted_data_df["Total Power"] column from a Series of single-element lists to a simple list
        predicted_data_df["Total Power"] = predicted_data_df["Total Power"].apply(lambda x: x[0])
        # Now, create a dictionary with the "predictions" key
        predictions_dict = {
            "predictions": predicted_data_df["Total Power"].tolist(),
            "preprocessed_data": preprocessed_data.to_dict(orient="records")
        }

        # Return the predictions as a JSON response
        return jsonify({"data": [predictions_dict]}), 200



    except Exception as e:
        # Log the full traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/api/uploads/<filename>", methods=["GET"])
def serve_uploaded_file(filename):
    try:
        # Check if the file exists
        file_path = os.path.join("uploads", filename)
        if not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404

        # Serve the file for download
        return send_file(file_path)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.before_first_request
def open_database_connection():
    app.connection, app.cursor = get_database_connection()
    

@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    connection.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

    app.run(debug=True)

