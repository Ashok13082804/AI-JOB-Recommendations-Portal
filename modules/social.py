from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json

from extensions import db
from models import Post, Comment, Like, Connection, User, Skill, Endorsement

social_bp = Blueprint('social_bp', __name__, url_prefix='/social')

@social_bp.route('/feed')
@login_required
def feed():
    # Get posts from connections and own posts
    connection_ids = [c.connected_user_id for c in 
                     Connection.query.filter_by(user_id=current_user.id, status='accepted').all()]
    connection_ids.append(current_user.id)
    
    posts = Post.query.filter(Post.user_id.in_(connection_ids))\
                     .order_by(Post.created_at.desc())\
                     .limit(20).all()
    
    # Get trending skills (simplified)
    trending_skills = ['Python', 'React', 'Machine Learning', 'AWS', 'Docker', 'TypeScript']
    
    # Get connection suggestions
    my_skills = [s.name.lower() for s in Skill.query.filter_by(user_id=current_user.id).all()]
    
    suggestions = User.query.filter(
        User.id != current_user.id,
        User.role == 'seeker'
    ).limit(5).all()
    
    return render_template('social/feed.html', 
                         posts=posts, 
                         trending_skills=trending_skills,
                         suggestions=suggestions)

@social_bp.route('/post', methods=['POST'])
@login_required
def create_post():
    data = request.get_json() if request.is_json else request.form
    
    post = Post(
        user_id=current_user.id,
        content=data.get('content'),
        post_type=data.get('post_type', 'text'),
        image_url=data.get('image_url')
    )
    
    db.session.add(post)
    db.session.commit()
    
    # If it's a job update or shared profile, add extra metadata if needed
    
    return jsonify({
        'success': True,
        'post_id': post.id,
        'message': f"{data.get('post_type', 'Post').capitalize()} created successfully"
    })

@social_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        like = Like(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        post.likes_count += 1
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': post.likes_count
    })

@social_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    data = request.get_json()
    
    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=data.get('content')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment_id': comment.id,
        'author': current_user.name,
        'content': comment.content
    })

@social_bp.route('/connect/<int:user_id>', methods=['POST'])
@login_required
def send_connection(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot connect with yourself'})
    
    # Check if connection exists
    existing = Connection.query.filter(
        ((Connection.user_id == current_user.id) & (Connection.connected_user_id == user_id)) |
        ((Connection.user_id == user_id) & (Connection.connected_user_id == current_user.id))
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Connection already exists'})
    
    connection = Connection(
        user_id=current_user.id,
        connected_user_id=user_id,
        status='pending'
    )
    
    db.session.add(connection)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Connection request sent'
    })

@social_bp.route('/connection/<int:connection_id>/accept', methods=['POST'])
@login_required
def accept_connection(connection_id):
    connection = Connection.query.get_or_404(connection_id)
    
    if connection.connected_user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    connection.status = 'accepted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Connection accepted'
    })

@social_bp.route('/connection/<int:connection_id>/reject', methods=['POST'])
@login_required
def reject_connection(connection_id):
    connection = Connection.query.get_or_404(connection_id)
    
    if connection.connected_user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db.session.delete(connection)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Connection rejected'
    })

@social_bp.route('/connections')
@login_required
def connections_list():
    # Accepted connections
    connections = Connection.query.filter(
        ((Connection.user_id == current_user.id) | (Connection.connected_user_id == current_user.id)),
        Connection.status == 'accepted'
    ).all()
    
    # Pending requests (received)
    pending = Connection.query.filter_by(
        connected_user_id=current_user.id,
        status='pending'
    ).all()
    
    return render_template('social/connections.html', 
                         connections=connections, 
                         pending=pending)

@social_bp.route('/endorse/<int:skill_id>', methods=['POST'])
@login_required
def endorse_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    if skill.user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot endorse your own skill'})
    
    existing = Endorsement.query.filter_by(skill_id=skill_id, endorsed_by=current_user.id).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Already endorsed'})
    
    endorsement = Endorsement(skill_id=skill_id, endorsed_by=current_user.id)
    skill.endorsements += 1
    
    db.session.add(endorsement)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'endorsements': skill.endorsements
    })
