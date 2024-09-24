from flask import Flask, redirect, url_for, Blueprint
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, UserMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields import DateTimeLocalField, TextAreaField
from .extensions import db
from eventapp.models import Event  # Adjust this path based on where your models are defined





class CalendarView(BaseView):

    @expose('/')
    def index(self):
        return self.render('admin/calendar.html')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class EventURLsView(BaseView):
    @expose('/')
    def index(self):
        events = Event.query.all()

        event_urls = []
        for event in events:
            # Construct the event URL
            event_url = f"http://127.0.0.1:5000/checkout?event_id={event.id}&tickets=1"
            event_urls.append({'id': event.id, 'title': event.title, 'url': event_url})

        # Render the template to display the event URLs
        return self.render('admin/event_urls.html', event_urls=event_urls)

    # Add access control logic if needed
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login'))


# EventModelView for Flask-Admin
class EventModelView(ModelView):
    form_overrides = {
        'start': DateTimeLocalField,
        'end': DateTimeLocalField,
        'description': TextAreaField
    }
    form_args = {
        'start': {
            'format': '%Y-%m-%dT%H:%M'
        },
        'end': {
            'format': '%Y-%m-%dT%H:%M'
        }
    }
    form_columns = ['title', 'start', 'end', 'price_per_ticket', 'description', 'private']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login'))


# Custom AdminIndexView
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login'))

def setup_admin(app):
    from eventapp.models import Event
    from .extensions import db

    admin = Admin(app, name='admin', index_view=MyAdminIndexView(), template_mode='bootstrap3')
    admin.add_view(EventModelView(Event, db.session, name='Event Model'))
    admin.add_view(CalendarView(name='Calendar', endpoint='calendar'))
    admin.add_view(EventURLsView(name='Event URLs', endpoint='event_urls'))