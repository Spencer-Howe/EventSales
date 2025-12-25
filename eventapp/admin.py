from flask import Flask, redirect, url_for, Blueprint, request, render_template
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, UserMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields import DateTimeLocalField, TextAreaField
from wtforms.validators import ValidationError
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

class ManualBookingView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        events = Event.query.all()
        message = ""
        message_type = ""
        
        if request.method == 'POST':
            try:
                # Get form data
                customer_name = request.form.get('customer_name', '').strip()
                customer_email = request.form.get('customer_email', '').strip()
                customer_phone = request.form.get('customer_phone', '').strip()
                order_id = request.form.get('order_id', '').strip()
                event_id = request.form.get('event_id')
                tickets = int(request.form.get('tickets', 1))
                amount_paid = float(request.form.get('amount_paid', 0))
                payment_method = request.form.get('payment_method', 'paypal')
                paypal_order_id = request.form.get('paypal_order_id', '').strip()
                
                if not all([customer_name, customer_email, order_id, event_id]):
                    message = "Missing required fields"
                    message_type = "error"
                else:
                    from eventapp.models import Customer, Payment
                    
                    # Step 1: Insert customer record (skip if already exists)
                    customer = Customer.query.filter_by(email=customer_email).first()
                    if not customer:
                        customer = Customer(
                            name=customer_name,
                            email=customer_email,
                            phone=customer_phone if customer_phone else None
                        )
                        db.session.add(customer)
                        db.session.flush()  # Get the customer ID
                    
                    # Step 2: Insert booking record
                    booking = Booking(
                        order_id=order_id,
                        tickets=tickets,
                        booking_date=datetime.now(),
                        reminder_sent=False,
                        checked_in=False,
                        customer_id=customer.id,
                        event_id=int(event_id)
                    )
                    db.session.add(booking)
                    db.session.flush()  # Get the booking ID
                    
                    # Step 3: Insert payment record
                    payment = Payment(
                        amount_paid=amount_paid,
                        currency='USD',
                        status='COMPLETED',
                        payment_method=payment_method,
                        payment_date=datetime.now(),
                        paypal_order_id=paypal_order_id if paypal_order_id else None,
                        booking_id=booking.id
                    )
                    db.session.add(payment)
                    
                    # Commit all changes
                    db.session.commit()
                    
                    message = f"Booking successfully created with Order ID: {order_id}"
                    message_type = "success"
                    
            except Exception as e:
                db.session.rollback()
                message = f"Error creating booking: {str(e)}"
                message_type = "error"
        
        return self.render('admin/manual_booking.html', 
                         events=events, 
                         message=message, 
                         message_type=message_type)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

class ValentineMagicAdminView(BaseView):
    @expose('/')
    def index(self):
        return self.render('valentine_magic_admin.html')

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
    
    # Form columns - both is_private and private are needed for different purposes
    form_columns = ['title', 'start', 'end', 'price_per_ticket', 'max_capacity', 'description', 'is_private', 'private', 'is_booked', 'user_id']
    
    # List view columns
    column_list = ['id', 'title', 'start', 'end', 'price_per_ticket', 'max_capacity', 'is_private', 'is_booked', 'user.username']
    column_searchable_list = ['title', 'description']
    column_filters = ['start', 'is_private', 'is_booked', 'user.username']
    column_sortable_list = ['id', 'title', 'start', 'end', 'price_per_ticket', 'max_capacity']
    
    # Form validation and pre-population
    def on_model_change(self, form, model, is_created):
        # Auto-assign current user if no user is selected
        if not model.user_id:
            model.user_id = current_user.id
        
        # Validate that end time is after start time
        if model.end and model.start and model.end <= model.start:
            raise ValidationError('End time must be after start time')
        
        # Default values for new events
        if is_created:
            if not model.max_capacity:
                model.max_capacity = 50
            if not model.price_per_ticket:
                model.price_per_ticket = 0.0

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('views.login_view'))

class RepeatEventsView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        message = ""
        message_type = ""
        created_events = []
        
        if request.method == 'POST':
            try:
                # Get form data
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip()
                start_date = request.form.get('start_date', '').strip()
                start_time = request.form.get('start_time', '').strip()
                duration_hours = int(request.form.get('duration_hours', 2))
                price_per_ticket = float(request.form.get('price_per_ticket', 0))
                max_capacity = int(request.form.get('max_capacity', 50))
                is_private = request.form.get('is_private') == 'on'
                private = request.form.get('private') == 'on'
                
                # Repeat options
                repeat_type = request.form.get('repeat_type', 'none')
                repeat_count = int(request.form.get('repeat_count', 1))
                repeat_days = request.form.getlist('repeat_days')  # For weekly repeats
                repeat_interval = int(request.form.get('repeat_interval', 1))
                
                if not all([title, start_date, start_time]):
                    message = "Missing required fields: title, start date, and start time"
                    message_type = "error"
                else:
                    from eventapp.models import User
                    
                    # Get current user
                    user = User.query.get(current_user.id)
                    if not user:
                        raise Exception("User not found")
                    
                    # Parse start datetime
                    start_datetime_str = f"{start_date} {start_time}"
                    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                    end_datetime = start_datetime + timedelta(hours=duration_hours)
                    
                    # Create events based on repeat type
                    if repeat_type == 'none':
                        # Single event
                        event = Event(
                            title=title,
                            description=description,
                            start=start_datetime,
                            end=end_datetime,
                            price_per_ticket=price_per_ticket,
                            max_capacity=max_capacity,
                            is_private=is_private,
                            private=private,
                            is_booked=False,
                            user_id=user.id
                        )
                        db.session.add(event)
                        created_events.append(event)
                        
                    elif repeat_type == 'daily':
                        # Daily repeats
                        for i in range(repeat_count):
                            event_start = start_datetime + timedelta(days=i * repeat_interval)
                            event_end = event_start + timedelta(hours=duration_hours)
                            
                            event = Event(
                                title=f"{title} - Day {i + 1}" if repeat_count > 1 else title,
                                description=description,
                                start=event_start,
                                end=event_end,
                                price_per_ticket=price_per_ticket,
                                max_capacity=max_capacity,
                                is_private=is_private,
                                private=private,
                                is_booked=False,
                                user_id=user.id
                            )
                            db.session.add(event)
                            created_events.append(event)
                            
                    elif repeat_type == 'weekly':
                        # Weekly repeats on specific days
                        if not repeat_days:
                            repeat_days = [str(start_datetime.weekday())]  # Default to same day of week
                        
                        week_count = 0
                        while len(created_events) < repeat_count:
                            for day_num in repeat_days:
                                if len(created_events) >= repeat_count:
                                    break
                                    
                                # Calculate date for this day of the week
                                days_ahead = int(day_num) - start_datetime.weekday()
                                if days_ahead < 0:  # Target day already happened this week
                                    days_ahead += 7
                                    
                                event_date = start_datetime.date() + timedelta(
                                    days=days_ahead + (week_count * repeat_interval * 7)
                                )
                                event_start = datetime.combine(event_date, start_datetime.time())
                                event_end = event_start + timedelta(hours=duration_hours)
                                
                                # Skip if we've already passed the original start date for first week
                                if week_count == 0 and event_start < start_datetime:
                                    continue
                                
                                event = Event(
                                    title=f"{title} - {event_start.strftime('%m/%d')}" if repeat_count > 1 else title,
                                    description=description,
                                    start=event_start,
                                    end=event_end,
                                    price_per_ticket=price_per_ticket,
                                    max_capacity=max_capacity,
                                    is_private=is_private,
                                    private=private,
                                    is_booked=False,
                                    user_id=user.id
                                )
                                db.session.add(event)
                                created_events.append(event)
                            
                            week_count += 1
                            
                    elif repeat_type == 'monthly':
                        # Monthly repeats
                        for i in range(repeat_count):
                            # Add months while keeping the same day
                            month_offset = i * repeat_interval
                            year_offset = month_offset // 12
                            month_offset = month_offset % 12
                            
                            new_year = start_datetime.year + year_offset
                            new_month = start_datetime.month + month_offset
                            if new_month > 12:
                                new_year += 1
                                new_month -= 12
                            
                            try:
                                event_start = start_datetime.replace(year=new_year, month=new_month)
                                event_end = event_start + timedelta(hours=duration_hours)
                                
                                event = Event(
                                    title=f"{title} - {event_start.strftime('%m/%d')}" if repeat_count > 1 else title,
                                    description=description,
                                    start=event_start,
                                    end=event_end,
                                    price_per_ticket=price_per_ticket,
                                    max_capacity=max_capacity,
                                    is_private=is_private,
                                    private=private,
                                    is_booked=False,
                                    user_id=user.id
                                )
                                db.session.add(event)
                                created_events.append(event)
                            except ValueError:
                                # Handle cases where day doesn't exist in target month (e.g., Feb 30)
                                continue
                    
                    # Commit all events
                    db.session.commit()
                    
                    message = f"Successfully created {len(created_events)} event(s)!"
                    message_type = "success"
                    
            except Exception as e:
                db.session.rollback()
                message = f"Error creating events: {str(e)}"
                message_type = "error"
        
        return self.render('admin/repeat_events.html', 
                         message=message, 
                         message_type=message_type,
                         created_events=created_events)

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
    admin.add_view(ManualBookingView(name='Manual Booking', endpoint='manual_booking'))
    admin.add_view(ValentineMagicAdminView(name='Valentine Magic Photo Shoots', endpoint='valentine_magic_admin'))
    admin.add_view(RepeatEventsView(name='Create Repeat Events', endpoint='repeat_events'))