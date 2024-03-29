# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import traceback
import logging
from datetime import datetime,timedelta
import keras
from sklearn import svm
from db_connector import get_database_connection
from model_manager import load_lstm_model, load_svr_model

app = Flask(__name__)
CORS(app)
connection = get_database_connection()
cursor = connection.cursor()

# Define the required features for the model
required_features = ["Date/Time", "Voltage Ph-A Avg", "Voltage Ph-B Avg", "Voltage Ph-C Avg", "Current Ph-A Avg", "Current Ph-B Avg", "Current Ph-C Avg"
                     ,"Power Factor Total","Power Ph-A","Power Ph-B","Power Ph-C", "Total Power","Unix Timestamp","predicted power"]

def get_model(model_version):
    model_type = model_version[1]
    version = model_version[2]
    model = None
    
    if model_type == 'lstm':
        model = load_lstm_model(version)
    elif model_type in ['svr_weekend', 'svr_holiday']:
        model = load_svr_model(model_type, version)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
        
    return model
        
def load_version_by_date(date):
    if is_holiday(date):
        query = "SELECT * FROM model_versions WHERE model_type = 'svr_holiday' AND is_selected = 1"
    elif date.weekday() < 5:
        query = "SELECT * FROM model_versions WHERE model_type = 'lstm' AND is_selected = 1"
    elif date.weekday()>=5:
        query = "SELECT * FROM model_versions WHERE model_type = 'svr_weekend' AND is_selected = 1"
    
    cursor.execute(query)
    model_version = cursor.fetchone() 
    return model_version
        
def insert_initial_data(connection, cursor, formatted_dates):
    try:
        select_query = "SELECT COUNT(*) FROM energy_data WHERE `Date/Time` = %s"
        insert_query = "INSERT INTO energy_data (`Date/Time`) VALUES (%s)"

        for formatted_date in formatted_dates:
            cursor.execute(select_query, (formatted_date,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute(insert_query, (formatted_date,))
        
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise ValueError("Error inserting initial data: " + str(e))

    
def update_data(connection, cursor, data):
    try:
        update_query = """
            UPDATE energy_data 
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
    except Exception as e:
        connection.rollback()
        raise ValueError("Error updating data: " + str(e))
    
def update_predicted_data(connection, cursor, data):
    try:
        update_query = "UPDATE energy_data SET `predicted power` = %s WHERE `Date/Time` = %s"
        update_data = [(row['Predicted Load'], pd.to_datetime(row['Date/Time'])) for _, row in data.iterrows()]
        cursor.executemany(update_query, update_data)
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise ValueError("Error updating predicted data: " + str(e))

def save_data_database(data, is_first=True, is_prediction=False):
    try:
        # Create date range and insert initial data
        datetime_start = data['Date/Time'].iloc[0]
        today = pd.date_range(datetime_start, periods=48, freq='30T')
        formatted_dates = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in today]
        if not is_prediction:
            if is_first:
                insert_initial_data(connection, cursor, formatted_dates)
                
            # Update regular data
            update_data(connection, cursor, data)
        elif is_prediction:
            insert_initial_data(connection, cursor, formatted_dates)
            update_predicted_data(connection, cursor, data)
    except Exception as e:
        connection.rollback()
        raise ValueError("Error saving data to database: " + str(e))
    
def is_holiday(date):
    try:
        if isinstance(date,datetime):
            date = date.date()
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
    query = """
    SELECT `Date/Time`, `Voltage Ph-A Avg`, `Voltage Ph-B Avg`, `Voltage Ph-C Avg`,
           `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`, `Power Factor Total`,
           `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power`, `Unix Timestamp`
    FROM Energy_Data 
    """    
    if is_holiday(date):
        query += """INNER JOIN holidays ON Date(`Energy_Data`.`Date/Time`) = `holidays`.`date` WHERE DATE(`Energy_Data`.`Date/Time`) <> %s"""
    
    elif date.weekday() >= 5:
        query += "WHERE WEEKDAY(`Date/Time`) >= 5 AND DATE(`Date/Time`) <> %s"
        
    elif date.weekday() <5:
        query += "WHERE WEEKDAY(`Date/Time`) < 5 AND DATE(`Date/Time`) <> %s"
        
    # Add a condition to filter data where the date is not larger than the given date
    query += " AND DATE(`Energy_Data`.`Date/Time`) <= %s"
 
        
    query += " ORDER BY `Energy_Data`.`Date/Time` DESC LIMIT 48"
    date = date.date()
    cursor.execute(query, (date,date))
    data = cursor.fetchall()
    
    if len(data) >= 48:
        # Since the query results are in descending order, reverse the data list to get the earliest date first
        data.reverse()
        return pd.DataFrame(data, columns=column_features)
    else:
        return None
    
def removeNegativeSign(data):
    data['Power Factor Total']= abs(data['Power Factor Total'])
    return data
    
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
    scaler_x=joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)
    seed_data_scaled = scaler_x.transform(seed_data)
    
    # Reshape seed_data_scaled to match the model's input shape
    seed_data_reshaped = seed_data_scaled.reshape((seed_data_scaled.shape[0], 1, seed_data_scaled.shape[1]))
    
    # Predict all data points at once
    predicted_data = model.predict(seed_data_reshaped)
    
    # Inverse transform the predictions
    predicted_data = scaler_y.inverse_transform(predicted_data)
    
    # Flatten the predictions if needed
    predicted_data = predicted_data.flatten()
    
    return predicted_data

def predict_svr_model(model, seed_data, scaler_x_path, scaler_y_path):
    scaler_x =joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)
    seed_data_scaled = scaler_x.transform(seed_data)

    # Predict all data points at once
    predicted_data = model.predict(seed_data_scaled)

    # Reshape the predicted_data if needed
    predicted_data = predicted_data.reshape(-1, 1)

    # Inverse transform the predictions
    predicted_data = scaler_y.inverse_transform(predicted_data)

    # Flatten the predictions if needed
    predicted_data = predicted_data.flatten()

    return predicted_data

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        json_data = request.get_json()
        if json_data is None:
            return jsonify({"error": "Invalid JSON data"}), 400

        # Extract the actual data from the nested "data" key and create a DataFrame
        input_data = json_data.get("data")
        if input_data is None or not isinstance(input_data, list) or len(input_data) == 0:
            return jsonify({"error": "Invalid JSON data"}), 400
        if len(input_data) > 0 :
            # Convert 'Date/Time' to proper datetime format
            for entry in input_data:
                entry['Date/Time'] = datetime.strptime(entry['Date/Time'], "%d/%m/%Y %I:%M:%S %p").strftime("%Y-%m-%d %H:%M:%S")
        # 'data' key exists and is not empty
            data = pd.DataFrame(input_data,columns=required_features)
        else:
            # Return a response or error message as needed
            return jsonify({"error": "No data"}), 500
        # Preprocess the data
        preprocessed_data = preprocess_data(data)
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
        
            model_version = load_version_by_date(preprocessed_data["Date/Time"].iloc[0])

           # Load the appropriate model based on the specified version
            if model_version:
                model_to_use = get_model(model_version)
            else:
               return jsonify({"error": "Missing model"}), 400
            # Get the last weekend's data from the database
            last_48_data = get_data_for_model(preprocessed_data["Date/Time"].iloc[0])
            historical_df = pd.DataFrame(last_48_data)
            historical_preprocessed_df=removeNegativeSign(historical_df)
            #Change the format of the date of actual preprocessed_data)
            preprocessed_data['Date/Time'] = pd.to_datetime(preprocessed_data['Date/Time']).dt.strftime("%d-%m-%Y %H:%M")
            # Use the predict_next_48_points method to make predictions
            predictions_df = predict_next_48_points(model_to_use, historical_preprocessed_df,preprocessed_data['Date/Time'])
            # Save the predicted data to the database
            save_data_database(predictions_df, is_prediction=True)
            # Convert the preprocessed data to dictionary format
            actual_data_records = preprocessed_data.drop(columns=['predicted power']).to_dict(orient='records')
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

@app.route("/api/training_model",methods=["POST"])
def model_training():
    try:
        date = request.json.get('date')
        # Parse the date string into a datetime object, ignoring time and timezone
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        model_version = load_version_by_date(parsed_date)

        # Get the current timestamp as the dynamic version
        dynamic_version = get_dynamic_version()
        model=get_model(model_version)
        message = ""
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
        # Load scalers
        scaler_x = joblib.load(scaler_x_path)
        scaler_y = joblib.load(scaler_y_path)
        # Preprocess data
        X_data = data.drop(columns=['Date/Time', 'Total Power'])
        y = data['Total Power']
        X_scaled = scaler_x.transform(X_data)
        y_reshaped = y.values.reshape(-1, 1)
        y_scaled = scaler_y.transform(y_reshaped)
        X_reshaped = X_scaled.reshape(-1, 1, X_data.shape[1])
        # Train the model
        model.fit(X_reshaped, y_scaled)
        # Save the trained model with the dynamic version
        model_path = f"models/LSTM/{version}_lstm.keras"
        model.save(model_path)
        # Save the model version into the database
        save_model_version("lstm", version)
        
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
        model_type = "svr_holiday" if isHoliday else "svr_weekend"
        save_model_version(model_type, version)
        return "SVR model training completed successfully"
    except Exception as e:
        return str(e)
    
def save_model_version(model_type, version):
    try:
        insert_query = "INSERT INTO model_versions (model_type, version,created_at) VALUES (%s, %s,%s)"
        values = (model_type, version, datetime.now())

        cursor.execute(insert_query,values)
        
        updated_model_version(model_type,version)
        
    except Exception as e:
        print("Error saving model version:", e)

def updated_model_version(model_type,version):
    try:
        reset_query = "UPDATE model_versions SET is_selected = 0 WHERE model_type = %s"
        cursor.execute(reset_query,(model_type,))
        
        update_query = "UPDATE model_versions SET is_selected = 1 WHERE model_type = %s AND version = %s"
        cursor.execute(update_query,(model_type,version))
        
    except Exception as e:
        print("Error updating selected model")
        
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
    
    # Define a function to remove units from a column
def remove_units(column):
    # Extract numeric part (assuming the numeric part is always at the beginning)
    numeric_part = column.split(' ')[0]
    return numeric_part

@app.route('/api/file-upload', methods=['POST'])
def file_upload():
    try:
        # Check if a file was sent in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file:
            filename = file.filename

            # Process the file here, for example, save it to a directory
            file.save(f"uploads/{filename}")
            df = pd.read_csv(f"uploads/{filename}", parse_dates=['Date/Time'], date_parser=lambda x: pd.to_datetime(x, format='%d/%m/%Y %I:%M:%S %p'))
                # Remove units from specific columns
            columns_to_clean = ['Voltage Ph-A Avg', 'Voltage Ph-B Avg', 'Voltage Ph-C Avg', 'Current Ph-A Avg', 'Current Ph-B Avg', 'Current Ph-C Avg','Power Factor Total']
            for col in columns_to_clean:
                df[col] = df[col].apply(remove_units)
                df[col] = df[col].astype(float)

                
            historical_df = preprocess_data(df)
            historical_df['Date/Time'] = pd.to_datetime(historical_df['Date/Time']).dt.strftime("%Y-%m-%d %H:%M:%S")
            historical_df['Date/Time'] = pd.to_datetime(historical_df['Date/Time'])
            save_data_database(historical_df)
            save_data_database(historical_df,is_first=False)
            # Convert the last date in historical_df to a datetime object
            last_date = pd.to_datetime(historical_df['Date/Time'].iloc[0])
            # Calculate the next day
            next_day = last_date + timedelta(days=1)
            # Create a new DataFrame with the next day as the starting point
            next_day_df = pd.DataFrame({'Date/Time': pd.date_range(next_day, periods=48, freq='30T')})
            # Format the 'Date/Time' column in next_day_df as required
            next_day_df['Date/Time'] = next_day_df['Date/Time'].dt.strftime("%d-%m-%Y %H:%M")
            next_date_for_get_data = pd.to_datetime(next_day_df['Date/Time'],format="%d-%m-%Y %H:%M")
            # If the next day is not weekday, then take the previous weekend data
            if is_holiday(next_date_for_get_data.iloc[0]) | next_day.weekday() >= 5:
                model_version=load_version_by_date(next_date_for_get_data.iloc[0])
                historical_data = get_data_for_model(next_date_for_get_data.iloc[0])
                historical_df = pd.DataFrame(historical_data)
                historical_df=removeNegativeSign(historical_df)
                
            elif next_day.weekday() < 5:
                if last_date.weekday()== 6 | is_holiday(last_date):
                    historical_data = get_data_for_model(next_date_for_get_data.iloc[0])
                    historical_df = pd.DataFrame(historical_data)
                model_version=load_version_by_date(next_date_for_get_data.iloc[0])
                historical_df=removeNegativeSign(historical_df)
            model = get_model(model_version)
            prediction_df = predict_next_48_points(model,historical_df,next_day_df['Date/Time'])
            save_data_database(prediction_df,is_prediction=True)
            return jsonify({'message': 'File Uploaded and Processed'}), 200

    except Exception as e:
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return jsonify({'error': 'An error occurred during file upload'}), 500

    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

    app.run(debug=True)

