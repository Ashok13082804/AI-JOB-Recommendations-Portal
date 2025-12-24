from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json
import os

from extensions import db
from models import Event, EventRegistration, User

events_bp = Blueprint('events_bp', __name__, url_prefix='/events')

@events_bp.route('/')
def index():
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    event_type = request.args.get('type', '')
    is_internship = request.args.get('is_internship') == 'true'
    
    query = Event.query
    
    if search:
        query = query.filter(Event.title.ilike(f'%{search}%') | Event.description.ilike(f'%{search}%'))
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if is_internship:
        query = query.filter(Event.is_internship == True)
        
    events = query.order_by(Event.start_date.asc()).all()
    
    return render_template('events/index.html', 
                           events=events, 
                           search=search, 
                           location=location, 
                           event_type=event_type,
                           is_internship=is_internship)

@events_bp.route('/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = False
    if current_user.is_authenticated:
        is_registered = EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first() is not None
        
    return render_template('events/detail.html', event=event, is_registered=is_registered)

@events_bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    event = Event.query.get_or_404(event_id)
    
    existing = EventRegistration.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Already registered for this event'})
        
    registration = EventRegistration(
        event_id=event_id,
        user_id=current_user.id
    )
    db.session.add(registration)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Successfully registered for the event'})

@events_bp.route('/my-events')
@login_required
def my_events():
    registrations = EventRegistration.query.filter_by(user_id=current_user.id).all()
    events = [r.event for r in registrations]
    return render_template('events/my_events.html', events=events)
