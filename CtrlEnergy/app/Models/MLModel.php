<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MLModel extends Model
{
    use HasFactory;
    public $table = 'model_versions';
    protected $fillable = ['model_type', 'version', 'is_selected'];
}
