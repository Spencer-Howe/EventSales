from eventapp import create_app
from eventapp.tasks import check_and_send_reminders
from eventapp.extensions import scheduler

app = create_app(scheduler=scheduler)

if __name__ == '__main__':
    scheduler.add_job(func=check_and_send_reminders, trigger='interval', hours=1, id='email_reminder')
    scheduler.start()
    app.run(host='0.0.0.0')
