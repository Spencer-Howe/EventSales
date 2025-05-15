from eventapp import create_app
from eventapp.tasks import check_and_send_reminders, clear_old_bookings


app = create_app(check_and_send_reminders=check_and_send_reminders, clear_old_bookings=clear_old_bookings)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
