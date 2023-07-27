<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Phpml\ModelManager;
use Carbon\Carbon;
use Rubix\ML\PersistentModel;
use Rubix\ML\Persisters\Filesystem;

class MLController extends Controller
{
    protected $modelManager;

    public function __construct(){
        $this->modelManager = new ModelManager();
    }
    public function predict(Request $request){
        $inputData = $request->all();
        $date = Carbon::parse($request->input('date'));
        $inputData=$this->changeTypeOfData($inputData);
        $inputData = $this->dropColumns($inputData,['timestamp','date','totalPower']);
        $modelPath = $this->getModelPath($date);
        // dd($modelPath);
        // $model = $this->modelManager->restoreFromFile($modelPath);
        $model = PersistentModel::load(new Filesystem($modelPath));
        dd($model);
        $prediction = $model->predict($inputData);
        dd($prediction);
        return response()->json(['prediction'=>$prediction]);
    }
    protected function getModelPath($date){
        if ($date->isWeekday()){
            
            return storage_path('app/models/rnn_weekday.joblib');
        }elseif($date->isWeekend()){
           
            return storage_path('app\models\svr_weekend.joblib');;
        }else{
            return storage_path('app\models\svr_holiday.joblib');;
        }
        }
        protected function dropColumns($data, $columns)
    {
        foreach ($columns as $column) {
            unset($data[$column]);
        }

        return $data;
    } 
        protected function changeTypeOfData($data){
            $columns = ['voltageA', 'voltageB', 'voltageC', 'currentA', 'currentB', 'currentC', 'powerFactor','powerA','powerB','powerC','totalPower'];
            foreach($columns as $column){
                $data[$column] = floatval($data[$column]);
            }
            return $data;
        }
}
