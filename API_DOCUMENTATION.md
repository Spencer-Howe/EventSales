# Android App API Docs

here's how the android api works

Base URL: `/api`

## Auth 
Admin stuff needs `Authorization: Bearer admin_<whatever>` in the header

## The endpoints

### GET /api/booking/{order_id}
Gets booking info without actually checking the person in. Safe endpoint.

Returns:
```json
{
  "success": true,
  "order_id": "ABC123", 
  "name": "John Doe",
  "email": "john@example.com",
  "tickets": 2,
  "event": "October 12, 2024 at 02:00 PM",
  "event_timestamp": "2024-10-12T14:00:00",
  "status": "COMPLETED",
  "amount_paid": 50.00,
  "currency": "USD",
  "checked_in": false,
  "checkin_time": null
}
```

### POST /api/admin/login
Login for staff on the mobile app

Send:
```json
{
  "username": "admin",
  "password": "password" 
}
```

Get back:
```json
{
  "success": true,
  "token": "admin_user_20241008123456",
  "staff_id": "admin", 
  "name": "admin"
}
```

### POST /api/admin/checkin/{order_id}
Actually check someone in. Admin only obvs.

Headers: `Authorization: Bearer <admin_token>`

Send:
```json
{
  "staff_id": "admin",
  "location": "entrance"
}
```

Get:
```json
{
  "success": true,
  "name": "John Doe",
  "tickets": 2, 
  "event": "October 12, 2024 at 02:00 PM",
  "checkin_time": "2024-10-08T15:30:00",
  "staff_id": "admin",
  "location": "entrance"
}
```

### GET /api/bookings  
All bookings dump for admin interface

Headers: `Authorization: Bearer admin_<token>`

Returns big  array of all booking objects with customer/event/payment data

## Notes
- Check-in only works during event time window
- Simple token auth for now (should prob do JWT later)
- All times in Pacific timezone cause that's where we are