<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\URL;

class MAPENotification extends Notification
{
    use Queueable;

    protected $mape;
    /**
     * Create a new notification instance.
     */
    public function __construct($mape)
    {
        $this->mape = $mape;
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
            ->subject('MAPE Anomaly Alert')
            ->line('You are receiving this notification because of a MAPE anomaly.');

        if ($this->mape > 10) {
            // If the MAPE is greater than 10, it's considered an anomaly indicating potential issues.
            $mailMessage->line('Anomaly detected in MAPE. Please investigate.');
        } else {
            // If the MAPE is within an acceptable range (<= 10), no anomaly is detected.
            $mailMessage->line('No significant anomalies detected in MAPE.');
        }

        // Add a button with a link to your web application
        $mailMessage->action('View MAPE Data', URL::route('home'));

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
