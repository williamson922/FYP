<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use App\Events\receiveAPIDataEvent;

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
}
