from eventapp import create_app
from eventapp.tasks import check_and_send_reminders, check_and_send_photo_followups


app = create_app(check_and_send_reminders=check_and_send_reminders, check_and_send_photo_followups=check_and_send_photo_followups, clear_old_bookings=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
