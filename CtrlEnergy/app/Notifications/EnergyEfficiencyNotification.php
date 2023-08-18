<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\URL;

class EnergyEfficiencyNotification extends Notification
{
    use Queueable;

    protected $energyEfficiency;
    /**
     * Create a new notification instance.
     */
    public function __construct($energyEfficiency)
    {
        $this->energyEfficiency = $energyEfficiency;
    }

    /**
     * Get the notification's delivery channels.
     *
     * @return array<int, string>
     */
    public function via(object $notifiable): array
    {
        return ['mail'];
    }

    /**
     * Get the mail representation of the notification.
     */
    public function toMail($notifiable)
    {
        $mailMessage = (new MailMessage)
            ->subject('Energy Efficiency Alert')
            ->line('The introduction to the notification.');

        if ($this->energyEfficiency > 110) {
            $mailMessage->line('Energy usage is high. Consider taking measures to reduce consumption.');
        } elseif ($this->energyEfficiency < 85) {
            $mailMessage->line('Energy efficiency is degraded. Consider retraining the model.');
        } elseif ($this->energyEfficiency > 115) {
            $mailMessage->line('Energy efficiency is degraded. Consider retraining the model.');
        } else {
            $mailMessage->line('Energy efficiency is within acceptable range.');
        }
        // Add a button with a link to your web application
        $mailMessage->action('View Energy Data', URL::route('home'));

        return $mailMessage;
    }

    /**
     * Get the array representation of the notification.
     *
     * @return array<string, mixed>
     */
    public function toArray(object $notifiable): array
    {
        return [
            //
        ];
    }
}
