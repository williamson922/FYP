<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ModelVersionController;
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

header('Access-Control-Allow-Origin:  *');
header('Access-Control-Allow-Methods:  POST, GET, OPTIONS, PUT, DELETE');
header('Access-Control-Allow-Headers:  Content-Type, X-Auth-Token, Origin, Authorization');
Route::group(['middleware' => ['api']], function () {
    Route::post('/bms-data', [BMSDataController::class, 'receiveDataFromBMSAndSendToAPI']);
    Route::get('/api-data', [BMSDataController::class, 'receiveDataFromAPIAndSendToWeb']);
    // Route::match(['GET', 'POST'], '/bms-data', [BMSDataController::class, 'receiveData']);

});

Route::post('/get-data/actual', [BMSDataController::class, 'getActualData'])->name('data.actual');
Route::post('/get-data/predict', [BMSDataController::class, 'getPredictData'])->name('data.predict');

Route::get('/get-model-versions/{modelType}', [ModelVersionController::class, 'getModelVersions'])->name('model.versions');
Route::post('set-model-version', [ModelVersionController::class, 'setModelVersion'])->name('model.set-version');

Route::post('/set-holiday', [HolidayController::class, 'create'])->name('holiday.insert');
Route::post('/holiday', [HolidayController::class, 'destroy'])->name('holiday.delete');
Route::get('/holidays', [HolidayController::class, 'index'])->name('holiday.showAll');
