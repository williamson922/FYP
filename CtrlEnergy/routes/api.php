<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\MLController;
use App\Http\Controllers\BMSDataController;
use App\Http\Controllers\HolidayController;
use App\Http\Controllers\QueueStatusController;

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

header('Access-Control-Allow-Origin:  *');
header('Access-Control-Allow-Methods:  POST, GET, OPTIONS, PUT, DELETE');
header('Access-Control-Allow-Headers:  Content-Type, X-Auth-Token, Origin, Authorization');
Route::group(['middleware' => ['api']], function () {
    Route::get('/queue/status', [QueueStatusController::class, 'checkQueueStatus']);
    Route::post('/bms-data', [BMSDataController::class, 'receiveDataFromBMSAndSendToAPI']);
    Route::get('/api-data', [BMSDataController::class, 'receiveDataFromAPIAndSendToWeb']);
    // Route::match(['GET', 'POST'], '/bms-data', [BMSDataController::class, 'receiveData']);

});

Route::post('/get-data', [BMSDataController::class, 'getTodayData'])->name('data.today');

Route::post('/set-holiday', [HolidayController::class, 'create'])->name('holiday.insert');
Route::post('/holiday', [HolidayController::class, 'destroy'])->name('holiday.delete');
Route::get('/holidays', [HolidayController::class, 'index'])->name('holiday.showAll');
