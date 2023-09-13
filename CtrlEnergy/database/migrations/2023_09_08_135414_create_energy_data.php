<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('energy_data', function (Blueprint $table) {
            $table->id();
            $table->dateTime('Date/Time');
            $table->float('Voltage Ph-A Avg');
            $table->float('Voltage Ph-B Avg');
            $table->float('Voltage Ph-C Avg');
            $table->float('Current Ph-A Avg');
            $table->float('Current Ph-B Avg');
            $table->float('Current Ph-C Avg');
            $table->float('Power Factor Total');
            $table->float('Power Ph-A');
            $table->float('Power Ph-B');
            $table->float('Power Ph-C');
            $table->float('Total Power');
            $table->bigInteger('Unix Timestamp');
            $table->float('predicted power')->nullable(); // Assuming this column can be nullable
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('energy_data');
    }
};
