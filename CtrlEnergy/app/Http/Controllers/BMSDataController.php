<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;
use App\Models\QueryLog;
use App\Events\receiveAPIDataEvent;
use App\Models\EnergyData;
use App\Models\User;
use App\Notifications\MAPENotification;
use Carbon\Carbon;

class BMSDataController extends Controller
{
    public function receiveDataFromBMSAndSendToAPI(Request $request)
    {
        $data = $request->all();
        $validatedData = $this->validateAndConvertNumericData($data);
        $jsonData = ['data' => $validatedData]; // The data is already an array
        // Make the HTTP POST request to the prediction API
        $response = Http::asJson()->post('http://localhost:5000/api/predict', $jsonData);
        // Check if the request was successful
        if ($response->successful()) {
            $apiData = $response->json();
            event(new receiveAPIDataEvent($apiData));
            return response()->json(["message" => "Data received successfully and processed successfully"]);
        } else {
            // Request was not successful, return an error response
            return response()->json(['error' => 'Failed to process data'], $response->status());
        }
    }
    private function validateAndConvertNumericData(array $data)
    {
        $validatedData = [];
        foreach ($data as $key => $value) {
            // Check if the value is numeric (float or integer)
            if (is_numeric($value)) {
                $validatedData[$key] = (float) $value; // Convert to float
            } else {
                // Keep non-numeric values as they are
                $validatedData[$key] = $value;
            }
        }

        return $validatedData;
    }
    public function getPredictData(Request $request)
    {
        // Enable query logging
        DB::enableQueryLog();
        $datetime = $request->input('Date/Time');
        $date = date('Y-m-d', strtotime($datetime)); // Extract the date part

        info(['Date' => $date]);
        info(['Time' => date('H:i:s', strtotime($datetime))]);

        // Use the date to get the data for that specific date and before
        $predict_data = EnergyData::select('Date/Time', 'predicted power')->whereDate('Date/Time', '=', $date)->orderBy('Date/Time', 'ASC')->limit(48)->get();

        // Convert the collection to an array before logging
        $predict_data_array = $predict_data->toArray();

        // Log the data
        info(['From table' => $predict_data_array]);

        // Get the logged queries
        $loggedQueries = DB::getQueryLog();

        // Store the query log in a separate table for later analysis
        foreach ($loggedQueries as $loggedQuery) {
            QueryLog::create([
                'table' => 'testing', // Change this to the actual table name
                'query' => $loggedQuery['query'],
                'bindings' => json_encode($loggedQuery['bindings']),
                'time' => $loggedQuery['time'],
            ]);
        }

        return response()->json($predict_data);
    }
    public function getActualData(Request $request)
    {
        $datetime = $request->input('Date/Time');
        $date = date('Y-m-d', strtotime($datetime)); // Extract the date part

        info(['Date' => $date]);
        info(['Time' => date('H:i:s', strtotime($datetime))]);

        // Use the date to get the data for that specific date and before
        $actual_data = EnergyData::whereDate('Date/Time', '=', $date)
            ->whereTime('Date/Time', '<=', date('H:i:s', strtotime($datetime)))
            ->orderBy('Date/Time', 'ASC')
            ->get();

        // Loop through the actual data and remove unwanted keys
        foreach ($actual_data as &$entry) {
            unset($entry['Unix Timestamp']);
            unset($entry['predicted power']);
        }
        // Convert the collection to an array before logging
        $actual_data_array = $actual_data->toArray();

        // Log the data
        info(['From table' => $actual_data_array]);

        return response()->json($actual_data);
    }

    public function checkMAPEAndNotification()
    {
        Log::info('Start of checkMAPEAndNotification.');
        $mapeThreshold = 10; // Set your desired MAPE threshold here
        // $currentDate = Carbon::today(); // Get the current date
        $currentDate = '2023-03-04';
        // Fetch actual total power for the day
        $actualData = EnergyData::whereDate('Date/Time', $currentDate)
            ->select('Total Power')
            ->get(); // Adjust column name and model as needed

        // Fetch predicted total power for the day
        $predictedData = EnergyData::whereDate('Date/Time', $currentDate)
            ->select('predicted power')
            ->get(); // Adjust column name and model as needed

        // Ensure both actual and predicted data are available
        if ($actualData->count() > 0 && $predictedData->count() > 0) {
            $mapeValues = [];

            // Calculate MAPE for each data point
            foreach ($actualData as $index => $actualEntry) {
                $actual = $actualEntry['Total Power'];
                $predicted = $predictedData[$index]['predicted power'];
                $mape = abs(($actual - $predicted) / $actual) * 100;
                $mapeValues[] = $mape;
            }

            // Check for MAPE exceeding the threshold
            $anomalies = array_filter($mapeValues, function ($mape) use ($mapeThreshold) {
                return $mape > $mapeThreshold;
            });

            if (!empty($anomalies)) {
                Log::debug($anomalies);
                // Send notifications to all users
                $users = User::all();
                foreach ($users as $user) {
                    $user->notify(new MAPENotification($anomalies));
                }
            }
        }
        Log::info('MAPE check executed successfully.');
    }
}
