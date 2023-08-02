<?php

namespace App\Http\Controllers;

use DateTime;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class BMSDataController extends Controller
{
    public function receiveData(Request $request)
    {
        $data = $request->all();
        $jsonData = ['data' => $data]; // The data is already an array

        // Make the HTTP POST request to the prediction API
        $response = Http::asJson()->post('http://localhost:5000/api/predict', $jsonData);
        // Check if the request was successful
        if ($response->successful()) {
            // Get the response body as JSON
            $responseData = $response->json();

            return response()->json(['message' => 'Data received and processed successfully', 'response' => $responseData]);
        } else {

            // Request was not successful, return an error response
            return response()->json(['error' => 'Failed to process data'], $response->status());
        }
    }
}

