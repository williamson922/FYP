# api.py
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename
import traceback
import logging
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import keras
import sklearn
from db_connector import get_database_connection
from model_manager import load_lstm_model, load_svr_model

app = Flask(__name__)
CORS(app)
connection = get_database_connection()
cursor = connection.cursor()

# Define the required features for the model
required_features = ["Date/Time", "Voltage Ph-A Avg", "Voltage Ph-B Avg", "Voltage Ph-C Avg", "Current Ph-A Avg", "Current Ph-B Avg", "Current Ph-C Avg"
                     ,"Power Factor Total","Power Ph-A","Power Ph-B","Power Ph-C", "Total Power","Unix Timestamp","predicted power"]

def get_model_for_date(date, version):
    if date.weekday() < 5:
        return load_lstm_model(version)
    elif date.weekday() >= 5:
        return load_svr_model("SVR_weekend", version)
    elif is_holiday(date):
        return load_svr_model("SVR_holiday", version)
    else:
        return load_lstm_model(version)
    
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
                model_to_use = get_model_for_date(preprocessed_data["Date/Time"].iloc[0], version)
            else:
                model_to_use = get_model_for_date(preprocessed_data["Date/Time"].iloc[0], "default")  # Or specify a default version
        
            
            # Get the last weekend's data from the database
            last_48_data = get_data_for_model(preprocessed_data["Date/Time"].iloc[0])
            preprocessed_df = pd.DataFrame(last_48_data)
            #Change the format of the date of actual preprocessed_data)
            preprocessed_data['Date/Time'] = pd.to_datetime(preprocessed_data['Date/Time']).dt.strftime("%d-%m-%Y %H:%M")
            # Use the predict_next_48_points method to make predictions
            predictions_df = predict_next_48_points(model_to_use, preprocessed_df,preprocessed_data['Date/Time'])
            print( predictions_df)
            # Save the predicted data to the database
            save_data_database(predictions_df, is_prediction=True)

            # Convert the preprocessed data to dictionary format
            actual_data_records = preprocessed_data.drop(columns=['predicted power']).to_dict(orient='records')
            print( actual_data_records)
            # Construct the JSON response with predicted and actual data
            response_data = {
                "actual_data": actual_data_records,
            }

            # Return the JSON response with a 200 status code
            return jsonify(response_data), 200
        else:
            # Return the predicted data and actual in the JSON response
            return jsonify({'actual_data':preprocessed_data.drop(columns=['predicted power']).to_dict(orient ='records')}), 200

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


@app.route("/api/training_model",methods=["POST"])
def model_training():
    try:
        date = request.json.get('date')
        version = request.args.get('version')
        # Parse the date string into a datetime object, ignoring time and timezone
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        # Get the current timestamp as the dynamic version
        dynamic_version = get_dynamic_version()
        model=get_model_for_date(parsed_date,version)
        message = ""

        print(parsed_date)
            # Call the appropriate prediction method based on the model type
        if isinstance(model, keras.models.Sequential):
            data = get_training_data_for_date(parsed_date)
            preprocessed_data = preprocess_data(data)
            scaler_x_path = './scaler/LSTM/lstm_scaler_x.pkl'
            scaler_y_path = './scaler/LSTM/lstm_scaler_y.pkl'
            message = training_lstm_model(model, preprocessed_data, scaler_x_path, scaler_y_path, dynamic_version)
        elif isinstance(model, svm.SVR):
            data = get_data_for_model(parsed_date)
            scaler_x_path = './scaler/SVR/svr_scaler_x.pkl'
            scaler_y_path = './scaler/SVR/svr_scaler_y.pkl'
            if is_holiday(parsed_date):
                message = training_svr_model(model, preprocessed_data, scaler_x_path, scaler_y_path, dynamic_version,isHoliday=True)
            else:
                message = training_svr_model(model, preprocessed_data, scaler_x_path, scaler_y_path, dynamic_version)
                
        else:
            raise ValueError('Invalid model type: %s', model)
        print("Message:",message)
        return jsonify({"message": message})
    except Exception as e:
        # Log the full traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return jsonify({"error": str(e)}), 500
# Helper function to get a dynamic version based on current timestamp
def get_dynamic_version():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"v{timestamp}"

def training_lstm_model(model, data, scaler_x_path, scaler_y_path, version):
    try:
        print("Model:", model)
        print("Data:", data)
        
        # Load scalers
        scaler_x = joblib.load(scaler_x_path)
        scaler_y = joblib.load(scaler_y_path)
        print(scaler_x, scaler_y)
        # Preprocess data
        X_data = data.drop(columns=['Date/Time', 'Total Power'])
        y = data['Total Power']
        print("X_data:", X_data)
        print("y:", y)
        X_scaled = scaler_x.transform(X_data)
        print("X_scaled:", X_scaled)
        y_reshaped = y.values.reshape(-1, 1)
        y_scaled = scaler_y.transform(y_reshaped)
        print("y_scaled:", y_scaled)
 
        X_reshaped = X_scaled.reshape(-1, 1, X_data.shape[1])
        
        print("X_reshaped:", X_reshaped)
        print("y_reshaped:", y_reshaped)
        
        # Train the model
        model.fit(X_reshaped, y_scaled)
        
        # Save the trained model with the dynamic version
        model_path = f"models/LSTM/{version}.keras"
        model.save(model_path)
        
        # Save the model version into the database
        save_model_version("LSTM", version)
        
        return "LSTM model training completed successfully"
    except Exception as e:
        return 'error:' + str(e)
        
def training_svr_model(model, data, scaler_x_path, scaler_y_path,version,isHoliday=False):
    try:
        scaler_x = joblib.load(scaler_x_path)
        scaler_y = joblib.load(scaler_y_path)
        X_data = data.drop(columns=['Date/Time', 'Total Power', 'predicted power'])
        y = data['Total Power']
        X_scaled = scaler_x.transform(X_data)
        y_scaled = scaler_y.transform(y)
        model.fit(X_scaled,y_scaled)
        if isHoliday:
            # Save the trained model with the dynamic version
            model_path = f"models/SVR/SVR_holiday/{version}"
        else:
            model_path = f"models/SVR/SVR_weekend/{version}"
        joblib.dump(model, model_path)
        # Save the model version into the database
        model_type = "SVR_holiday" if isHoliday else "SVR_weekend"
        save_model_version(model_type, version)
        return "SVR model training completed successfully"
    except Exception as e:
        return str(e)
    
def save_model_version(model_type, version):
    try:
        insert_query = "INSERT INTO model_versions (model_type, version) VALUES (%s, %s)"
        values = (model_type, version)

        cursor.execute(insert_query,values)
        
    except Exception as e:
        print("Error saving model version:", e)
        
def get_training_data_for_date(date):
    try:
        query = "SELECT `Date/Time`, `Voltage Ph-A Avg`, `Voltage Ph-B Avg`, `Voltage Ph-C Avg`, `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`, `Power Factor Total`, `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power`,`Unix Timestamp` FROM Energy_Data WHERE DATE(`Date/Time`) = %s ORDER BY `Date/Time`"
        values = (date,)

        cursor.execute(query, values)
        result = cursor.fetchall()

        # Convert the result to a pandas DataFrame
        columns = ['Date/Time', 'Voltage Ph-A Avg', 'Voltage Ph-B Avg', 'Voltage Ph-C Avg', 'Current Ph-A Avg', 'Current Ph-B Avg', 'Current Ph-C Avg', 'Power Factor Total', 'Power Ph-A', 'Power Ph-B', 'Power Ph-C', 'Total Power', 'Unix Timestamp']
        data = pd.DataFrame(result, columns=columns)

        return data
    except Exception as e:
        print("Error fetching training data for date:", e)
        return None

    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

    app.run(debug=True)

