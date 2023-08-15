<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;
use App\Models\QueryLog;
use App\Events\receiveAPIDataEvent;
use App\Models\EnergyData;

class BMSDataController extends Controller
{
    public function receiveDataFromBMSAndSendToAPI(Request $request)
    {
        $data = $request->all();
        phpinfo();
        $validatedData = $this->validateAndConvertNumericData($data);
        $jsonData = ['data' => $validatedData]; // The data is already an array

        // Make the HTTP POST request to the prediction API
        $response = Http::asJson()->post('http://localhost:5000/api/predict', $jsonData);
        // Check if the request was successful
        if ($response->successful()) {
            $apiData = $response->json();
            // ReceiveAPIData::dispatch($apiData)->afterCommit();
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
        $predict_data = EnergyData::select('Date/Time', 'predicted power')->whereDate('Date/Time', '=', $date)->limit(48)->get();

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
}
