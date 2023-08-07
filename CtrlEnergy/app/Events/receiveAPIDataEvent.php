<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Broadcasting\PresenceChannel;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;

class receiveAPIDataEvent implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    protected $data;
    /**
     * Create a new event instance.
     */
    public function __construct($data)
    {
        Log::debug("Event Constructor:",[$data]);
        $this->data = $data;
        Log::debug("Event Constructor:",[$this->data]);

    }

    /**
     * Get the channels the event should broadcast on.
     *
     * @return array<int, \Illuminate\Broadcasting\Channel>
     */
    public function broadcastOn(): array
    {
        return [
            new Channel('public-channel'),
        ];
    }
    public function broadcastAs(){
        return "event_apidata";
    }
    public function broadcastWith(){
        Log::debug("Broadcasting Data:", $this->data);
        return ['data' => $this->data];
    }
}
