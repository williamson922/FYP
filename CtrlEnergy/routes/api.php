<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\MLController;
use App\Http\Controllers\BMSDataController;
use App\Http\Controllers\HolidayController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

// Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
//     return $request->user();
// });

Route::post('/bms-data',[BMSDataController::class,'receiveData']);

Route::post('/set-holiday',[HolidayController::class,'store'])->name('holiday.insert');
Route::get('/holidays',[HolidayController::class,'index'])->name('holiday.showAll');