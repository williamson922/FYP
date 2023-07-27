<?php

namespace App\Http\Controllers;

use DateTime;
use Illuminate\Http\Request;

class BMSDataController extends Controller
{
    private $lastValues;

    public function receiveData(Request $request){
   // Perform data cleaning and feature addition
//    dd($request->all());
   $cleanedData = $this->cleanData($request->all());
   $dataWithFeatures = $this->addFeatures($cleanedData);   

   // Update last observed values
   $this->updateLastValues($dataWithFeatures);

   return response()->json(['message' => 'Data received and processed successfully']);
}
  // Method to perform data cleaning (fill missing values and add features)
  private function cleanData($data)
  {
      $columns = ['voltageA', 'voltageB', 'voltageC', 'currentA', 'currentB', 'currentC', 'powerFactor'];
  
      foreach ($columns as $column) {
          $value = $data[$column];
          if ($this->isMissingValues($value)) {
              $filledValue = $this->fillMissingValuesWithLOCF($value,$column);
              $data[$column] = $filledValue;
              
          }
      }
  
      return $data;
  }
  
  private function isMissingValues($value)
  {
        return $value === null || $value === '' || is_nan($value);
  }
  
  private function fillMissingValuesWithLOCF($value,$column)
  { 
      return $this->lastValues[$column];
  }
  
  private function addFeatures($data)
  {
      // Extract the date and time components from the timestamp
      $timestamp = $data['timestamp'];
      $dateTime = DateTime::createFromFormat('m/d/Y h:i:s A', $timestamp);
      $date = $dateTime->format('Y-m-d');
      $time = $dateTime->format('H:i:s');

      // Add additional features
      $data['date'] = $date;
      $data['time'] = $time;
      $data['powerPhaseA'] = $data['voltageA'] * $data['currentA'] * abs($data['powerFactor']);
      $data['powerPhaseB'] = $data['voltageB'] * $data['currentB'] * abs($data['powerFactor']);
      $data['powerPhaseC'] = $data['voltageC'] * $data['currentC'] * abs($data['powerFactor']);
      $data['totalPower'] = $data['powerPhaseA'] + $data['powerPhaseB'] + $data['powerPhaseC'];
      return $data;
  }
  
private function updateLastValues($data)
    {
        $columns = ['voltageA', 'voltageB', 'voltageC', 'currentA', 'currentB', 'currentC', 'powerFactor'];

        foreach ($columns as $column) {
            $value = $data[$column];
            $lastValue = $value;
            $this->lastValues[$column] = $lastValue;
        }
    }
  
}
