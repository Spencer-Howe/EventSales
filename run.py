from eventapp import create_app
from eventapp.tasks import check_and_send_reminders
from eventapp.extensions import scheduler

app = create_app(scheduler=scheduler, check_and_send_reminders=check_and_send_reminders)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
