from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration - Use environment variables in production
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here_change_in_production')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'}

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Portfolio data - Projects (from resume.json)
PORTFOLIO_ITEMS = [
    {
        'id': 1,
        'title': 'EMPLOY SALARY PREDICTION',
        'description': 'Designed and implemented Flutter mobile application to promote food transparency by scanning barcodes and retrieving ingredients, and Nutri-Score data. Integrated Firebase Authentication for secure user login and implemented backend logic using API calls.',
        'image': 'project_salary.jpg',
        'technologies': ['Flutter', 'Firebase (Auth)', 'Dart']
    },
    {
        'id': 2,
        'title': 'PERSONALIZED EDUCATIONAL PLATFORM',
        'description': 'Developed a mobile application that provides real-time scene descriptions and interactive Q/A for visually impaired users using Vision-Language Models (VLMs). Built the frontend with React Native (Expo) and backend with FastAPI (Python) integrating YOLO and Whisper for multimodal AI capabilities. Applied OCR and object detection (OpenCV, Detectron2, YOLO) to identify text, objects, and environmental hazards.',
        'image': 'project_education.jpg',
        'technologies': ['React Native', 'FastAPI', 'PyTorch', 'OpenCV', 'Detectron2', 'YOLO', 'TypeScript', 'Flutter', 'SQL']
    },
    {
        'id': 3,
        'title': 'SENSORS USING DETECTION ROBOTS (DIPLOMA)',
        'description': 'Using IoT and Arduino boards with IR sensors to build vehicles that detect distance.',
        'image': 'project_robots.jpg',
        'technologies': ['IoT', 'Arduino', 'IR sensors']
    }
]


SKILLS = {
    'Languages': ['Java', 'Python', 'C', 'SQL'],
    'Frontend': ['HTML', 'CSS'],
    'Database': ['MySQL'],
    'CS Fundamentals': ['Data Structures and Algorithms', 'DSA', 'Object Oriented Programming', 'Computer Networks', 'Machine Learning basics', 'UiPath']
}

# Load structured resume data (falls back to a default if the file is missing)
try:
    with open(os.path.join(os.path.dirname(__file__), 'data', 'resume.json'), 'r', encoding='utf-8') as f:
        RESUME = json.load(f)
except Exception:
    RESUME = {
        'name': 'Ch. Krishna Kumar',
        'contact': {'location': 'Sathupally, Telangana', 'email': 'chettimalakrishna@gmail.com', 'phone': '9391454023', 'github': 'https://github.com/chettimalakrishna-504'},
        'objective': 'Computer Science undergrad (GPA 8.35/10) passionate to apply strong fundamentals in algorithms, data structures, and object-oriented design, seeking to leverage academic knowledge and practical skills gained from coursework and online training.',
        'academics': [],
        'skills': SKILLS,
        'projects': [],
        'certifications': [
            'Smart Coder (DSA) — Smart Interviews',
            'Problem Solving (Basic) — HackerRank',
            'NPTEL Certification in Big Data Computing',
            'IIT Madras Certification (EV Vehicle)',
            'Trained at SAK Informatics',
            'Web Development Certification — Infosys Springboard (and Hackathon Certificate)',
            'Cisco Networking Academy — Programming Essentials in C'
        ],
        'experience': [
            {
                'year': '2023',
                'title': 'Intruder Detection Robots using Sensors',
                'company': 'MIST / Diploma Project',
                'duration': '~6 months',
                'details': ['Worked on intruder detection robots using IR sensors and Arduino boards.', 'Implemented distance sensing, basic control logic, and prototype testing.']
            },
            {
                'year': '2024',
                'title': 'EMPLOY SALARY PREDICTION — Team Leader (ML)',
                'company': 'Project',
                'duration': '6+ months',
                'details': ['Led team to implement a salary prediction system using foundational ML techniques.', 'Coordinated data collection, preprocessing, model training and evaluation.']
            },
            {
                'year': '2025',
                'title': 'EMPLOY SALARY PREDICTION — Team Leader (AI & ML)',
                'company': 'Project',
                'duration': 'Ongoing',
                'details': ['Continued leading enhancements to the salary prediction project, applying AI & ML techniques to improve performance.', 'Focused on feature engineering, model optimization, and deployment considerations.']
            }
        ],
        'additional': [],
        'personal': {}
    }

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Routes ====================

@app.route('/')
def index():
    """Home page with portfolio overview"""
    visits = session.get('visits', 0)
    visits += 1
    session['visits'] = visits
    
    # Check for flash messages
    message = request.args.get('message', None)
    if message:
        flash(message, 'info')
    
    return render_template('index.html', projects=PORTFOLIO_ITEMS[:3], skills=SKILLS)

@app.route('/about')
def about():
    """About page"""
    user_name = session.get('user', 'Guest')
    return render_template('about.html', user_name=user_name)

@app.route('/portfolio')
def portfolio():
    """Portfolio/Projects page"""
    return render_template('portfolio.html', projects=PORTFOLIO_ITEMS, skills=SKILLS)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Individual project detail page with variable rule"""
    project = next((p for p in PORTFOLIO_ITEMS if p['id'] == project_id), None)
    if project is None:
        flash('Project not found!', 'danger')
        return redirect(url_for('portfolio'))
    return render_template('project_detail.html', project=project)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate form data
        if not all([name, email, subject, message]):
            flash('Please fill in all required fields!', 'danger')
            return redirect(url_for('contact'))
        
        # Save contact message (in production, send email)
        contact_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store in session for demo purposes
        contacts = session.get('contacts', [])
        contacts.append(contact_data)
        session['contacts'] = contacts
        
        flash(f'Thank you {name}! Your message has been received. I will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/skills')
def skills():
    """Skills page"""
    return render_template('skills.html', skills=SKILLS)

@app.route('/services')
def services():
    """Services page"""
    services_list = [
        {
            'title': 'Web Development',
            'description': 'Full-stack web development with modern frameworks',
            'icon': '💻'
        },
        {
            'title': 'API Development',
            'description': 'RESTful and GraphQL API development',
            'icon': '⚙️'
        },
        {
            'title': 'Database Design',
            'description': 'Database architecture and optimization',
            'icon': '🗄️'
        },
        {
            'title': 'Consulting',
            'description': 'Technical consulting and code review',
            'icon': '📋'
        }
    ]
    return render_template('services.html', services=services_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Simple authentication (in production, use proper database)
        if username and password == 'password123':
            session['user'] = username
            
            # Set session expiration
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=7)
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = session.get('user')
    contacts = session.get('contacts', [])
    visits = session.get('visits', 0)
    
    return render_template('dashboard.html', user=user, contacts=contacts, visits=visits)

@app.route('/logout')
def logout():
    """Logout user"""
    user = session.get('user', 'User')
    session.clear()
    flash(f'Goodbye, {user}! You have been logged out.', 'info')
    return redirect(url_for('index', message=f'{user} logged out successfully!'))

@app.route('/resume', methods=['GET', 'POST'])
def resume():
    """Resume upload and download page"""
    if request.method == 'POST':
        # Check if file is in request
        if 'resume_file' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(url_for('resume'))
        
        file = request.files['resume_file']
        
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(url_for('resume'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Store in session
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append({
                'filename': filename,
                'original_name': request.files['resume_file'].filename,
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            session['uploaded_files'] = uploaded_files
            
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('resume'))
        else:
            flash('Invalid file type! Allowed types: pdf, txt, doc, docx, png, jpg, jpeg, gif', 'danger')
    
    uploaded_files = session.get('uploaded_files', [])
    return render_template('resume.html', uploaded_files=uploaded_files, resume=RESUME)

@app.route('/download/<filename>')
def download(filename):
    """Download uploaded file"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found!', 'danger')
            return redirect(url_for('resume'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('resume'))

# API to fetch resume data (useful for integrations)
@app.route('/api/resume')
def api_resume():
    return jsonify(RESUME)

# Download a simple text version of the resume generated from structured data
@app.route('/download_resume')
def download_resume():
    from io import BytesIO
    r = RESUME
    lines = []

    # Header / Contact
    lines.append(r.get('name', ''))
    c = r.get('contact', {})
    lines.append(f"{c.get('location','')} | {c.get('email','')} | {c.get('phone','')} | {c.get('github','')}")
    lines.append('')

    # Objective
    lines.append('Objective')
    lines.append('---------')
    lines.append(r.get('objective',''))
    lines.append('')

    # Academics
    lines.append('Academics')
    lines.append('---------')
    for a in r.get('academics',[]):
        lines.append(f"{a.get('title','')} — {a.get('institution','')} {a.get('date','')}")
        lines.append(f"  - {a.get('gpa','')}")
        if a.get('notes'):
            lines.append(f"  - {a.get('notes')}")
    lines.append('')

    # Technical Skills
    lines.append('Technical Skills')
    lines.append('----------------')
    for k, v in r.get('skills', {}).items():
        lines.append(f"{k}: {', '.join(v)}")
    lines.append('')

    # Projects
    lines.append('Projects')
    lines.append('--------')
    for p in r.get('projects', []):
        lines.append(p.get('title',''))
        lines.append('  ' + p.get('description',''))
        if p.get('tools'):
            lines.append('  Tools Used: ' + ', '.join(p.get('tools')))
        lines.append('')

    # Certifications
    lines.append('Certifications')
    lines.append('--------------')
    for cert in r.get('certifications', []):
        lines.append(f"- {cert}")
    lines.append('')

    # Experience
    lines.append('Experience')
    lines.append('----------')
    for e in r.get('experience', []):
        lines.append(f"{e.get('title','')} — {e.get('company','')}")
        for d in e.get('details', []):
            lines.append(f"  - {d}")
    lines.append('')

    # Additional
    lines.append('Additional')
    lines.append('----------')
    for a in r.get('additional', []):
        lines.append(f"- {a}")
    lines.append('')

    # Personal Details
    lines.append('Personal Details')
    lines.append('----------------')
    p = r.get('personal', {})
    lines.append(f"Name: {p.get('name','')}")
    lines.append(f"Father: {p.get('father','')}")
    lines.append(f"Mother: {p.get('mother','')}")
    lines.append(f"DOB: {p.get('dob','')}")
    lines.append(f"Address: {p.get('address','')}")
    lines.append('')

    # Declaration
    lines.append('Declaration')
    lines.append('-----------')
    lines.append('I hereby declare that the information given above is true to the best of my knowledge.')
    lines.append(p.get('name',''))

    content = '\n'.join(lines)
    return send_file(BytesIO(content.encode('utf-8')), as_attachment=True, download_name='resume_Chettimala_Krishna_Kumar.txt', mimetype='text/plain')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback form with file upload"""
    if request.method == 'POST':
        feedback_text = request.form.get('feedback')
        rating = request.form.get('rating')
        
        if not feedback_text:
            flash('Please provide feedback!', 'danger')
            return redirect(url_for('feedback'))
        
        feedback_data = {
            'feedback': feedback_text,
            'rating': rating,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Handle optional file upload
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    feedback_data['attachment'] = filename
        
        # Store feedback
        feedbacks = session.get('feedbacks', [])
        feedbacks.append(feedback_data)
        session['feedbacks'] = feedbacks
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    
    return render_template('feedback.html')

# ==================== Error Handlers ====================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403

# ==================== Context Processors ====================

@app.context_processor
def inject_user():
    """Inject user data into all templates"""
    return {
        'current_user': session.get('user'),
        'is_logged_in': 'user' in session,
        'site_resume': RESUME
    }

# ==================== Main ====================

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
