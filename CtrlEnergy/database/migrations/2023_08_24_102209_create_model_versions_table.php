<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

class CreateModelVersionsTable extends Migration
{
    public function up()
    {
        Schema::create('model_versions', function (Blueprint $table) {
            $table->id();
            $table->string('model_type');
            $table->string('version');
            $table->tinyInteger('is_selected')->default(0); // Default to not selected
            $table->timestamps();
        });

        // Set the default versions for specific model types
        DB::table('model_versions')->insert([
            ['model_type' => 'lstm', 'version' => 'default', 'is_selected' => 1],
            ['model_type' => 'svr_weekend', 'version' => 'default', 'is_selected' => 1],
            ['model_type' => 'svr_holiday', 'version' => 'default', 'is_selected' => 1],

        ]);
    }

    public function down()
    {
        Schema::dropIfExists('model_versions');
    }
}
