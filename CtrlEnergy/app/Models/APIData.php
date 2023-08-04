<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class APIData extends Model
{
    use HasFactory;
    protected $table = "api_data";
    protected $fillable = ['data'];
}
