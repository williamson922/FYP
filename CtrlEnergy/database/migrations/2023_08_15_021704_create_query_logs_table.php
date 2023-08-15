<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateQueryLogsTable extends Migration
{
    public function up()
    {
        Schema::create('query_logs', function (Blueprint $table) {
            $table->id();
            $table->string('table'); // To store the table name
            $table->text('query'); // To store the executed query
            $table->text('bindings'); // To store the query bindings (in JSON format)
            $table->float('time'); // To store the query execution time
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('query_logs');
    }
}
