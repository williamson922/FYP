<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\MLModel;
use Illuminate\Support\Facades\Log;

class ModelVersionController extends Controller
{
    public function getModelVersions(Request $request)
    {
        Log::debug('Received data for model type', ['model_type' => $request->modelType]);
        $versions = MLModel::where('model_type', $request->modelType)->get();
        Log::debug('Model versions', ['versions' => $versions]);
        return response()->json(['versions' => $versions]);
    }

    public function setModelVersion(Request $request)
    {
        Log::debug('Received data for model type', ['model_type' => $request->modelType]);
        $modelType = $request->input('modelType');
        $selectedVersion = $request->input('selectedVersion');

        // Step 1: Find the currently selected version for the specified model type
        $currentSelectedVersion = MLModel::where('model_type', $modelType)
            ->where('is_selected', 1)
            ->first();

        // Step 2: Set the current selected version's is_selected to 0
        if ($currentSelectedVersion) {
            $currentSelectedVersion->update([
                'is_selected' => 0,
            ]);
        }

        // Step 3: Set the newly selected version's is_selected to 1
        $newSelectedVersion = MLModel::where('model_type', $modelType)
            ->where('version', $selectedVersion)
            ->first();

        if ($newSelectedVersion) {
            $newSelectedVersion->update([
                'is_selected' => 1,
            ]);
        }

        return response()->json(['message' => 'Model version updated successfully']);
    }
}
