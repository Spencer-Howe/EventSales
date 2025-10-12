from flask import Flask, redirect, url_for, Blueprint, request, render_template
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, UserMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields import DateTimeLocalField, TextAreaField
from datetime import datetime, timedelta
from sqlalchemy import func
from .extensions import db
from eventapp.models import Event, Booking





class CalendarView(BaseView):

    @expose('/')
    def index(self):
        return self.render('admin/calendar.html')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

class EventURLsView(BaseView):
    @expose('/')
    def index(self):
        events = Event.query.all()


        event_urls = []
        for event in events:
            # Construct the event URL
            event_url = f"https://thehoweranchpayment.com/checkout?event_id={event.id}&tickets=1"
            event_urls.append({'id': event.id, 'title': event.title, 'url': event_url})

        # Render the template to display the event URLs
        return self.render('admin/event_urls.html', event_urls=event_urls)

    # Add access control logic if needed
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

class CryptoAdminView(BaseView):
    @expose('/')
    def index(self):
        # look for open crypto payments
        try:
            # Filter for crypto payments using the new Payment table
            from eventapp.models import Payment
            crypto_bookings = Booking.query.join(Payment).filter(
                Payment.payment_method == 'crypto',
                Payment.status == 'pending_crypto'
            ).all()
        except Exception as e:
            # field doesnt exist yet
            crypto_bookings = []
        
        return self.render('crypto_admin.html', bookings=crypto_bookings)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

class SearchBookingsView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        search_results = []
        search_term = ""
        search_type = "name"
        
        if request.method == 'POST':
            search_term = request.form.get('search_term', '').strip()
            search_type = request.form.get('search_type', 'name')
            
            if search_term:
                from eventapp.models import Customer
                if search_type == 'name':
                    search_results = Booking.query.join(Customer).filter(
                        Customer.name.ilike(f'%{search_term}%')
                    ).all()
                elif search_type == 'email':
                    search_results = Booking.query.join(Customer).filter(
                        Customer.email.ilike(f'%{search_term}%')
                    ).all()
                elif search_type == 'order_id':
                    search_results = Booking.query.filter(
                        Booking.order_id.ilike(f'%{search_term}%')
                    ).all()
                elif search_type == 'phone':
                    search_results = Booking.query.join(Customer).filter(
                        Customer.phone.ilike(f'%{search_term}%')
                    ).all()
        
        return self.render('admin/search_bookings.html', 
                         search_results=search_results,
                         search_term=search_term,
                         search_type=search_type)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

class ReportsView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        report_data = []
        report_type = "sales"
        date_from = ""
        date_to = ""
        report_generated = datetime.now()
        
        if request.method == 'POST':
            report_type = request.form.get('report_type', 'sales')
            date_from = request.form.get('date_from', '')
            date_to = request.form.get('date_to', '')
            
            # base
            query = Booking.query
            
            # add filters - join with Event for date filtering
            from eventapp.models import Event
            query = query.join(Event)
            
            if date_from:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Event.start >= date_from_obj)
            
            if date_to:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                # Add 1 day to include the end date
                date_to_obj = date_to_obj + timedelta(days=1)
                query = query.filter(Event.start < date_to_obj)
            
            if report_type == 'sales':
                # Sales report - filter by payment status
                from eventapp.models import Payment
                report_data = query.join(Payment).filter(
                    Payment.status.in_(['COMPLETED', 'pending_crypto'])
                ).all()
            elif report_type == 'attendance':
                # check booking numbers
                from eventapp.models import Payment, Event
                report_data = db.session.query(
                    Event.start,
                    Event.title,
                    func.count(Booking.id).label('total_bookings'),
                    func.sum(Booking.tickets).label('total_attendees'),
                    func.sum(Payment.amount_paid).label('total_revenue')
                ).join(Event).join(Payment).filter(
                    Payment.status.in_(['COMPLETED', 'pending_crypto'])
                ).group_by(Event.id, Event.start, Event.title).all()
            elif report_type == 'payment_methods':
                # check payment methods to see crypto business needs
                from eventapp.models import Payment
                report_data = db.session.query(
                    Payment.payment_method,
                    func.count(Booking.id).label('booking_count'),
                    func.sum(Payment.amount_paid).label('total_amount')
                ).join(Booking).filter(
                    Payment.status.in_(['COMPLETED', 'pending_crypto'])
                ).group_by(Payment.payment_method).all()
        
        return self.render('admin/reports.html',
                         report_data=report_data,
                         report_type=report_type,
                         date_from=date_from,
                         date_to=date_to,
                         report_generated=report_generated)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

class AttendanceLookupView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        events = Event.query.all()
        selected_event = None
        attendance_data = None
        
        if request.method == 'POST':
            event_id = request.form.get('event_id')
            if event_id:
                selected_event = Event.query.get(event_id)
                if selected_event:
                    # Get attendance count for this specific event
                    from eventapp.models import Payment
                    attendance_data = db.session.query(
                        func.sum(Booking.tickets).label('total_attendees'),
                        func.count(Booking.id).label('total_bookings'),
                        func.sum(Payment.amount_paid).label('total_revenue')
                    ).join(Payment).filter(
                        Booking.event_id == selected_event.id,
                        Payment.status.in_(['COMPLETED', 'pending_crypto'])
                    ).first()
        
        return self.render('admin/attendance_lookup.html',
                         events=events,
                         selected_event=selected_event,
                         attendance_data=attendance_data)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))


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
    form_columns = ['title', 'start', 'end', 'price_per_ticket', 'max_capacity', 'description', 'private', 'is_private', 'is_booked']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))


# Custom AdminIndexView
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

def setup_admin(app):
    from eventapp.models import Event
    from .extensions import db

    admin = Admin(app, name='admin', index_view=MyAdminIndexView(), template_mode='bootstrap3')
    admin.add_view(EventModelView(Event, db.session, name='Event Model'))
    admin.add_view(CalendarView(name='Calendar', endpoint='calendar'))
    admin.add_view(EventURLsView(name='Event URLs', endpoint='event_urls'))
    admin.add_view(CryptoAdminView(name='Crypto Admin', endpoint='cryptoadmin'))
    admin.add_view(SearchBookingsView(name='Search Bookings', endpoint='search_bookings'))
    admin.add_view(ReportsView(name='Reports', endpoint='reports'))
    admin.add_view(AttendanceLookupView(name='Attendance Lookup', endpoint='attendance_lookup'))