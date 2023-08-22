<?php

namespace App\Console;

use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Console\Kernel as ConsoleKernel;
use Illuminate\Support\Facades\Log;
use App\Models\EnergyData;
use App\Models\User;
use App\Notifications\EnergyEfficiencyNotification;

class Kernel extends ConsoleKernel
{
    /**
     * Define the application's command schedule.
     */
    protected function schedule(Schedule $schedule): void
    {
        $schedule->call(function () {
            Log::info('Scheduled task started'); // Log the start of the task
            // Call the checkEnergyEfficiencyAndNotify function
            app()->make('App\Http\Controllers\BMSDataController')->checkEnergyEfficiencyAndNotification();
            app()->make('App\Http\Controllers\EnergyModelController')->triggerModelTraining();
            Log::info('Scheduled task completed'); // Log the completion of the task
        })->everyMinute();
    }

    /**
     * Register the commands for the application.
     */
    protected function commands(): void
    {
        $this->load(__DIR__ . '/Commands');

        require base_path('routes/console.php');
    }
}
