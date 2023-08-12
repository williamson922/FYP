<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Holiday;

class HolidayController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $holidays = Holiday::orderBy('date', 'desc')->get();
        //if success, send back to the frontend
        return response()->json($holidays);
    }

    /**
     * Show the form for creating a new resource.
     */ public function create(Request $request)
    {
        $holiday = new Holiday();
        $holiday->fill($request->all());
        $holiday->save();

        return response()->json(['message' => 'Holiday created successfully'], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Request $request)
    {
        $dateToDelete = $request->input('date');

        // Find and delete the holiday record based on the provided date
        $holiday = Holiday::where('date', $dateToDelete)->first();
        if ($holiday) {
            $holiday->delete();
            return response()->json(['message' => 'Holiday deleted successfully']);
        } else {
            return response()->json(['message' => 'Holiday not found'], 404);
        }
    }
}
