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
from sklearn.preprocessing import MinMaxScaler
import datetime
import keras
import sklearn
from db_connector import get_database_connection

app = Flask(__name__)
CORS(app)
connection = get_database_connection()
cursor = connection.cursor()

# Define the required features for the model
required_features = ["Date/Time", "Voltage Ph-A Avg", "Voltage Ph-B Avg", "Voltage Ph-C Avg", "Current Ph-A Avg", "Current Ph-B Avg", "Current Ph-C Avg"
                     ,"Power Factor Total","Power Ph-A","Power Ph-B","Power Ph-C", "Total Power","Unix Timestamp","predicted power"]

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
        svr_model_folder = latest_version
    
    # Load the model using joblib
    model = joblib.load(svr_model_folder)
    return model


def save_data_database(data, is_first=True, is_prediction=False):
    try:
        if not is_prediction:
            if is_first:
                # Create date range
                datetime_start = data['Date/Time'].iloc[0]  # Get the first datetime value
                today = pd.date_range(datetime_start, periods=48, freq='30T')

                # Convert the datetime values to the MySQL DATETIME format
                formatted_dates = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in today]

                # Prepare the data for insertion (formatted datetime values)
                insertion_data = [(formatted_date,) for formatted_date in formatted_dates]

                # Define the INSERT query for inserting interval datetimes
                insert_query = "INSERT INTO testing (`Date/Time`) VALUES (%s)"

                # Execute the INSERT query to insert interval datetimes
                cursor.executemany(insert_query, insertion_data)
                connection.commit()
            update_query = """
            UPDATE testing 
            SET `Voltage Ph-A Avg`= %s,
                `Voltage Ph-B Avg`= %s,
                `Voltage Ph-C Avg`= %s,
                `Current Ph-A Avg`= %s,
                `Current Ph-B Avg`= %s,
                `Current Ph-C Avg`= %s,
                `Power Factor Total`= %s,
                `Power Ph-A`= %s,
                `Power Ph-B`= %s,
                `Power Ph-C`= %s,
                `Total Power`= %s,
                `Unix Timestamp` = %s 
            WHERE `Date/Time` = %s
            """

            # Assuming 'data' contains the features and datetime value
            for _, row in data.iterrows():
                update_data = (
                    row['Voltage Ph-A Avg'], row['Voltage Ph-B Avg'], row['Voltage Ph-C Avg'],
                    row['Current Ph-A Avg'], row['Current Ph-B Avg'], row['Current Ph-C Avg'],
                    row['Power Factor Total'], row['Power Ph-A'], row['Power Ph-B'],
                    row['Power Ph-C'], row['Total Power'],row['Unix Timestamp'], row['Date/Time']
                )
            
            cursor.execute(update_query, update_data)
            connection.commit()
                
            # Update the prediction data based on DateTime
        if is_prediction:
            # Update query for predicted values
            update_query = f"UPDATE testing SET `predicted power` = %s WHERE `Date/Time` = %s"
            
            # Prepare data for updating
            update_data = [(row['Predicted Load'], pd.to_datetime(row['Date/Time'])) for _, row in data.iterrows()]

            # Execute the UPDATE query to update predicted power values
            cursor.executemany(update_query, update_data)
            connection.commit()
    except Exception as e:
        connection.rollback()
        raise ValueError("Error saving data to database: " + str(e))
    
def load_data(date):
    try:
        date_only = date[0].date()  # Get the date part using the .date() method
        print("Date Only:", date_only)

        query = """
                SELECT
                    `Date/Time`, `Voltage Ph-A Avg`, `Voltage Ph-B Avg`, `Voltage Ph-C Avg`,
                    `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`,
                    `Power Factor Total`, `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power`, `predicted power`
                FROM testing WHERE DATE(`Date/Time`) = %s ORDER BY `Date/Time` ASC
                """
        cursor.execute(query, (date_only,))
        
        data = cursor.fetchall()
        print("Data:", data)
        if data:
            actual_dict = {}
            predicted_dict = {}
            for row in data:
                actual_dict[str(row[0])] = {  # Convert datetime object to string
                    "Voltage Ph-A Avg": row[1],
                    "Voltage Ph-B Avg": row[2],
                    "Voltage Ph-C Avg": row[3],
                    "Current Ph-A Avg": row[4],
                    "Current Ph-B Avg": row[5],
                    "Current Ph-C Avg": row[6],
                    "Power Factor Total": row[7],
                    "Power Ph-A": row[8],
                    "Power Ph-B": row[9],
                    "Power Ph-C": row[10],
                    "Total Power": row[11],
                }
                predicted_dict[str(row[0])] = {  # Convert datetime object to string
                    "predicted": row[12],
                }

            return actual_dict, predicted_dict  # Return separate dictionaries for actual and predicted data

        return {}, {}  # Return empty dictionaries if no data found for the specified date

    except Exception as e:
        print("Error loading data:", e)
        return {}, {}

def get_model_for_date(date, version):
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
    data['Date/Time'] = pd.to_datetime(data['Date/Time'])
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
    data['Unix Timestamp'] = data['Date/Time'].apply(lambda dt: (dt - pd.Timestamp("2020-01-01")) // pd.Timedelta('1s'))
    return data

def get_data_for_model(date):
    column_features = ["Date/Time", "Voltage Ph-A Avg", "Voltage Ph-B Avg", "Voltage Ph-C Avg", "Current Ph-A Avg", "Current Ph-B Avg", "Current Ph-C Avg"
                     ,"Power Factor Total","Power Ph-A","Power Ph-B","Power Ph-C", "Total Power","Unix Timestamp"]

    if date.weekday() >=5:
        query = "SELECT `Date/Time`, `Voltage Ph-A Avg`, `Voltage Ph-B Avg`, `Voltage Ph-C Avg`, `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`, `Power Factor Total`, `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power`,`Unix Timestamp` FROM Energy_Data WHERE `Date/Time` BETWEEN (SELECT MAX(`Date/Time`) FROM Energy_Data WHERE WEEKDAY(`Date/Time`) = 5) AND (SELECT MAX(`Date/Time`) FROM Energy_Data WHERE WEEKDAY(`Date/Time`) = 6) ORDER BY `Date/Time` DESC LIMIT 48"
    elif date.weekday() < 5:
        query = "SELECT `Date/Time`, `Voltage Ph-A Avg`, `Voltage Ph-B Avg`, `Voltage Ph-C Avg`, `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`, `Power Factor Total`, `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power`,`Unix Timestamp` FROM Energy_Data WHERE `Date/Time` BETWEEN (SELECT MAX(`Date/Time`) FROM Energy_Data WHERE WEEKDAY(`Date/Time`) = 5) AND (SELECT MAX(`Date/Time`) FROM Energy_Data WHERE WEEKDAY(`Date/Time`) = 6) ORDER BY `Date/Time` DESC LIMIT 48"
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) >= 48:
        # Since the query results are in descending order, reverse the data list to get the earliest date first
        data.reverse()
        return pd.DataFrame(data, columns=column_features)
    else:
        return None
    
def predict_next_48_points(model, historical_data, datetime, look_back=48):
    # Extract the last date in the historical_data to create the datetime index for predictions
    historical_data = historical_data.drop(columns=['Date/Time', 'Total Power'])

    # Use the last 'look_back' data points from the historical_data as the seed for prediction
    seed_data = historical_data[-look_back:]
    
    # Initialize an empty list to store the predicted data points
    predicted_array = []

    # Generate the datetime index for the next 48 data points (1 day ahead)
    today = pd.date_range(datetime.iloc[0], periods=48, freq='30T').strftime('%d-%m-%Y %H:%M')

    # Call the appropriate prediction method based on the model type
    if isinstance(model, keras.models.Sequential):
        scaler_x_path = './scaler/LSTM/lstm_scaler_x.pkl'
        scaler_y_path = './scaler/LSTM/lstm_scaler_y.pkl'
        predicted_array = predict_lstm_model(model, seed_data, scaler_x_path, scaler_y_path)
    elif isinstance(model, svm.SVR):
        scaler_x_path = './scaler/SVR/svr_scaler_x.pkl'
        scaler_y_path = './scaler/SVR/svr_scaler_y.pkl'
        predicted_array = predict_svr_model(model, seed_data, scaler_x_path, scaler_y_path)
    else:
        raise ValueError('Invalid model type: %s', model)

    # Convert the list of predicted data points into a numpy array
    predicted_array = np.array(predicted_array)
    if len(predicted_array) == len(today):
        # Create a DataFrame to hold the predicted data for the entire day
        predicted_df = pd.DataFrame({"Date/Time": today, "Predicted Load": predicted_array})
    else:
        raise ValueError("Length of predicted_array does not match length of today")

    return predicted_df

def predict_lstm_model(model, seed_data, scaler_x_path, scaler_y_path):
    predicted_list = []
    scaler_x=joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)
    seed_data_scaled = scaler_x.transform(seed_data)
    
    for data in seed_data_scaled:
        print(data.shape)
        data_reshaped = data.reshape((1, 1, 11))
        predicted_data = model.predict(data_reshaped)
        predicted_data = scaler_y.inverse_transform(predicted_data)
        predicted_list.append(predicted_data[0][0])
    print(predicted_list)
    return np.array(predicted_list)

def predict_svr_model(model, seed_data, scaler_x_path, scaler_y_path):
    predicted_list = []
    scaler_x =joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)
    seed_data_scaled = scaler_x.transform(seed_data)
    for data in seed_data_scaled:
        data_reshaped = data.reshape(1, -1)
        predicted_data = model.predict(data_reshaped)
        predicted_data = predicted_data.reshape(-1, 1)
        predicted_data = scaler_y.inverse_transform(predicted_data)
        predicted_list.append(predicted_data[0][0])
    
    return np.array(predicted_list)

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
            print(input_data)
            if len(input_data) > 0 :
            # 'data' key exists and is not empty
                data = pd.DataFrame(input_data,columns=required_features)
                
            else:
                # Return a response or error message as needed
                return jsonify({"error": "No data"}), 200
            print("DF:", data)
            # Preprocess the data
            preprocessed_data = preprocess_data(data)
            print('Preprocessed data:', preprocessed_data)
            # Extract the date from the timestamp and convert to datetime object
            preprocessed_data["Date/Time"] = pd.to_datetime(preprocessed_data["Date/Time"])
            first_data = True
            if (preprocessed_data['Date/Time'].dt.time != pd.Timestamp("00:00:00").time()).any():
                first_data =False
                save_data_database(preprocessed_data,is_first=False)
            else:
                save_data_database(preprocessed_data)
                
        if first_data:        
            # Extract the date from the timestamp and convert to datetime object
            preprocessed_data["Date/Time"] = pd.to_datetime(preprocessed_data["Date/Time"])
        
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
                model_to_use = get_model_for_date(preprocessed_data["Date/Time"].iloc[0], version)
        
            
            # Get the last weekend's data from the database
            last_48_data = get_data_for_model(preprocessed_data["Date/Time"].iloc[0])
            preprocessed_df = pd.DataFrame(last_48_data)
            #Change the format of the date of actual preprocessed_data)
            preprocessed_data['Date/Time'] = pd.to_datetime(preprocessed_data['Date/Time']).dt.strftime("%d-%m-%Y %H:%M")
            # Use the predict_next_48_points method to make predictions
            predictions_df = predict_next_48_points(model_to_use, preprocessed_df,preprocessed_data['Date/Time'])
            print( predictions_df)
            save_data_database(predictions_df,is_prediction=True)
            print(preprocessed_data.to_dict(orient='records'))
            # Return the predicted data and actual in the JSON response
            return jsonify({"predicted_data": predictions_df.to_dict(orient="records"),
                            'actual_data':preprocessed_data.to_dict(orient='records')}), 200
        else:
            actual_dict, predicted_dict = load_data(preprocessed_data['Date/Time'])
            print("Actual data:", actual_dict)
            print("Predicted data:", predicted_dict)
            # Return the predicted data and actual in the JSON response
            return jsonify({"predicted_data": predicted_dict,
                            'actual_data':actual_dict}), 200

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




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

    app.run(debug=True)

