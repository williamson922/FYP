<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use App\Models\APIData;

class ReceiveAPIData implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;
    protected $data;
    /**
     * Create a new job instance.
     */
    public function __construct($data)
    {
        Log::debug('Data from BMSDataController:', [gettype($data)]);
        $this->data = $data;
        Log::debug('Data passed to constructor:', [gettype($this->data)]);
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        try {
            Log::debug('Im in handle:', [gettype($this->data)]);
            $apiData = new ApiData();
            $apiData->data = json_encode($this->data);
            $apiData->save();
            Log::debug('Im fine, save successful:', [gettype($apiData->data)]);

        }
        catch (\Exception $e) {
        // Log the error for debugging
        // You can also rethrow the exception to let the queue worker handle it
        // throw $e;
        Log::error('Job Failed: ' . $e->getMessage());
        }
    }
}
