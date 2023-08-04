<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Queue;


class QueueStatusController extends Controller
{
    public function checkQueueStatus(){
        $hasPendingJob = Queue::size()>0;
        return response()->json(['has_pending_job' => $hasPendingJob]);
    }
}
