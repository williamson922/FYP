<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Carbon\Carbon;


class EnergyModelController extends Controller
{
    public function triggerModelTraining()
    {
        // $date = Carbon::today();
        $date = '2022-12-01'; // Static date for testing
        $response = Http::post('http://localhost:5000/api/training_model', ['date' => $date]);

        if ($response->successful()) {
            // Log the API response or handle it as needed
            Log::info('Model training API response: ' . $response->body());

            // You can also send a response back to the client if needed
            return response()->json(['message' => 'Model training request sent successfully']);
        } else {
            // Handle API request failure
            Log::error('Failed to trigger model training: ' . $response->body());
            return response()->json(['error' => 'Failed to trigger model training']);
        }
    }
}
