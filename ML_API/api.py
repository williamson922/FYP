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

def get_model_for_date(date, cursor,version):
    if date.weekday() < 5:
        return load_lstm_model()
    elif date.weekday() >= 5:
        return load_svr_model("SVR_weekend",version)
    elif is_holiday(date, cursor):
        return load_svr_model("SVR_holiday",version)
    else:
        return load_lstm_model()


def is_holiday(date, cursor):
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

def predict_data(model, preprocessed_data):
    # Predict the day-ahead load profile
    X_test = preprocessed_data.drop(columns=["Date/Time", "date", "Total Power"]).values
    y_pred = model.predict(X_test)

    # Convert predictions to a list
    predictions = y_pred.flatten().tolist()

    return predictions

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
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
            if json_data is None or "data" not in json_data:
                return jsonify({"error": "Invalid JSON data"}), 400
            
            # Extract the actual data from the "data" key and create a DataFrame
            input_data = json_data["data"]
            data = pd.DataFrame(input_data)
            
            # Preprocess the data
            preprocessed_data = preprocess_data(data)

        # Extract the date from the timestamp and convert to datetime object
        preprocessed_data["Date/Time"] = pd.to_datetime(preprocessed_data["Date/Time"])
        preprocessed_data["date"] = preprocessed_data["Date/Time"].dt.date
        
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
            model_to_use = get_model_for_date(preprocessed_data["Date/Time"].iloc[0], cursor,version)
        print(model_to_use)
        
        # Predict the day-ahead load profile
        predictions = predict_data(model_to_use, preprocessed_data)

        # Return the predictions as a JSON response
        return jsonify({"predictions": predictions}), 200

    except Exception as e:
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





if __name__ == "__main__":
    app.run(debug=True)

@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    connection.close()