from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, redirect, url_for, request,
    flash, session, jsonify, current_app, send_file
)
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Portfolio
from . import db
from .ai_processor import generate_portfolio_sections, extract_text_from_pdf
import json
from app.forms import EditProfileForm, UploadPhotoForm
import os
import secrets
from PIL import Image
import uuid
import base64
from functools import wraps
from flask import abort
import re
from markupsafe import Markup
from flask import jsonify

import tempfile
from playwright.sync_api import sync_playwright  # <-- THIS WAS THE MISSING PIECE!



def clean_text(content):
    """Clean AI text: remove brackets, quotes, fix commas/spaces, add line breaks."""
    if not content:
        return ""
    text = str(content)

    text = re.sub(r"^\[|\]$", "", text)
    text = text.replace("['", "").replace("']", "")
    text = text.replace('"', '').replace("'", '')

    text = re.sub(r",(?=\S)", ", ", text)

   
    text = re.sub(r"\s{2,}", " ", text)
    text = text.strip()

   
    text = text.replace("\n", "<br>")

    return Markup(text)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            ext = os.path.splitext(image_path)[1][1:].lower() or "png"
            return f"data:image/{ext};base64,{encoded}"
    except Exception as e:
        print("Base64 Image Error:", e)
        return None


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

main = Blueprint("main", __name__)


UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@main.route("/")
def home():
    return render_template("home.html")

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route("/edit-profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio
        form.links.data = current_user.links

    if form.validate_on_submit():
        if form.profile_picture.data and hasattr(form.profile_picture.data, 'filename'):
            picture_file = save_picture(form.profile_picture.data)
            current_user.profile_picture = picture_file

        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.links = form.links.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template("edit_profile.html", form=form)



@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful! Welcome back.", "success")
            return redirect(url_for("main.dashboard"))  # redirect to dashboard
        else:
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for("main.login"))

    return render_template("login.html")

@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
        else:
            new_user = User(
                full_name=full_name,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created! Please login.", "success")
            return redirect(url_for("main.login"))

    return render_template("signup.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main.login"))


@main.route('/dashboard')
@login_required
def dashboard():
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html",
                           name=current_user.full_name,
                           email=current_user.email,
                           profile_picture=current_user.profile_picture,
                           portfolios=portfolios)



@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash("No file uploaded", "danger")
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash("No selected file", "danger")
            return redirect(request.url)

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        session['last_uploaded_resume'] = filepath

       
        resume_text = extract_text_from_pdf(filepath)

 
        try:
            ai_output = generate_portfolio_sections(resume_text)
            if not ai_output or "Error" in ai_output:
                raise ValueError("AI failed to generate content")
        except Exception as e:
            print("AI Error:", str(e))
            ai_output = [{"section_title": "Error", "content": str(e)}]

       
        session["ai_generated_content"] = ai_output

        return redirect(url_for("main.customize_portfolio"))

    return render_template("upload.html")


@main.route('/customize_portfolio')
@login_required
def customize_portfolio():
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()

    if portfolio:
       
        raw_content = portfolio.resume_data
        portfolio_theme = portfolio.theme
        slug = portfolio.slug
    else:
        
        raw_content = session.get("ai_generated_content", [])
        portfolio_theme = "pastel"
        slug = str(uuid.uuid4())[:8]

    
    if isinstance(raw_content, str):
        try:
            sections = json.loads(raw_content)
        except (json.JSONDecodeError, TypeError):
            sections = []
    else:
        sections = raw_content

    print("DEBUG: Sections being sent to template:", sections)  # 👀 Debug log

    return render_template(
        "customize_portfolio.html",
        sections=sections,
        user=current_user,
        portfolio_theme=portfolio_theme,
        slug=slug
    )



@main.route("/save_portfolio/<slug>", methods=["POST"])
@login_required
def save_portfolio(slug):
    try:
        sections_json = request.form.get("sectionsData")
        selected_theme = request.form.get("selectedTheme", "pastel")

        if not sections_json:
            flash("No portfolio sections received.", "warning")
            return redirect(url_for("main.customize_portfolio"))

       
        try:
            sections = json.loads(sections_json)
            
            if isinstance(sections, dict):
                sections = [sections]
        except Exception as e:
            flash("Invalid sections data.", "danger")
            print("Invalid JSON in save_portfolio:", e)
            return redirect(url_for("main.customize_portfolio"))

       
        session["saved_sections"] = sections
        session["selected_theme"] = selected_theme

        
        portfolio = Portfolio.query.filter_by(slug=slug, user_id=current_user.id).first()
        if portfolio:
            portfolio.resume_data = json.dumps(sections)
            portfolio.theme = selected_theme
            
        else:
           
            portfolio = Portfolio(
                user_id=current_user.id,
                title=current_user.full_name or f"{current_user.email}'s Portfolio",
                slug=slug,
                resume_data=json.dumps(sections),
                theme=selected_theme
            )
            db.session.add(portfolio)

        db.session.commit()

        print("💾 Saved sections to DB for slug:", slug, "sections count:", len(sections))
        flash("Portfolio saved successfully!", "success")
        return redirect(url_for("main.preview_portfolio", slug=slug))

    except Exception as e:
        db.session.rollback()
        print("❌ Error saving portfolio:", str(e))
        flash("Failed to save portfolio.", "danger")
        return redirect(url_for("main.customize_portfolio"))





@main.route("/preview/<slug>")
def preview_portfolio(slug):
    format_mode = request.args.get('format', 'screen')
   
    portfolio_obj = Portfolio.query.filter_by(slug=slug).first()

    sections_list = []
    if portfolio_obj and portfolio_obj.resume_data:
        try:
            sections_list = json.loads(portfolio_obj.resume_data)
        except (json.JSONDecodeError, TypeError):
            sections_list = []
    else:
      
        sections_list = session.get("saved_sections", [])

    
    sections_for_template = {
        (s.get("section_title", s.get("title", "Untitled Section")).strip()).lower():
        clean_text(s.get("content", "No content available."))
        for s in sections_list if isinstance(s, dict)
    }

    
    skills_list = []
    raw_skills = None
    for key in ("skills", "key expertise", "technologies", "technical skills"):
        if key in sections_for_template:
            raw_skills = sections_for_template.get(key)
            break

    if raw_skills:
        s = str(raw_skills)
      
        s = s.replace("\\n", ", ").replace("\n", ", ")
        
        s = re.sub(r'^\s*\[|\]\s*$', '', s)
       
        s = s.replace("','", ",").replace('", "', ",").replace("', '", ",")
       
        s = s.replace("'", "").replace('"', "")
      
        parts = re.split(r'[,\|;]+', s)
        
        skills_list = [p.strip() for p in parts if p.strip()]

    
    projects_raw = sections_for_template.get("projects", "")
    projects_html = str(projects_raw) if projects_raw is not None else ""


    
    if portfolio_obj:
        profile_filename = portfolio_obj.user.profile_picture or "default-profile.png"
    else:
        profile_filename = current_user.profile_picture or "default-profile.png"

    profile_path = os.path.join(current_app.root_path, "static/profile_pics", profile_filename)
    profile_base64 = get_base64_image(profile_path)

    return render_template(
        "preview.html",
        portfolio=sections_for_template,
        slug=slug,
        theme=(portfolio_obj.theme if portfolio_obj and portfolio_obj.theme else session.get("selected_theme", "pastel")),
        user=(portfolio_obj.user if portfolio_obj and portfolio_obj.user else current_user),
        profile_base64=profile_base64,
        format_mode=format_mode,
        skills_list=skills_list,
        projects_html=Markup(projects_html)
    )

@main.route("/publish/<slug>", methods=["GET", "POST"])
@login_required
def publish_portfolio(slug):
    """
    AJAX-aware publish endpoint.
    - Returns JSON {url: <public_url>} when called via fetch/ajax (Accept: application/json or ?ajax=1)
    - Otherwise behaves as before (flash + redirect to public url)
    """
   
    portfolio = Portfolio.query.filter_by(slug=slug, user_id=current_user.id).first_or_404()


    public_url = url_for('main.public_portfolio', slug=slug, _external=True)

    
    if request.args.get('ajax') == '1' or request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"status": "ok", "url": public_url}), 200

  
    flash(f"Portfolio '{portfolio.title}' published successfully!", "success")
    return redirect(public_url)

@main.route("/p/<slug>")
def public_portfolio(slug):
    """
    Public read-only view for sharing. Renders preview.html with public=True
    so the template hides edit/publish controls.
    """
    portfolio_obj = Portfolio.query.filter_by(slug=slug).first_or_404()

    
    sections_list = []
    if portfolio_obj.resume_data:
        try:
            sections_list = json.loads(portfolio_obj.resume_data)
        except Exception:
            sections_list = []

    
    sections_for_template = {
        (s.get("section_title", s.get("title", "Untitled Section")).strip()).lower():
        clean_text(s.get("content", "No content available."))
        for s in sections_list if isinstance(s, dict)
    }


    skills_list = []
    raw_skills = None

    for key in ("skills", "key expertise", "technologies", "technical skills"):
        if key in sections_for_template:
            raw_skills = sections_for_template.get(key)
            break

    if raw_skills:
        s = str(raw_skills)
        s = s.replace("\\n", ", ").replace("\n", ", ")
        s = re.sub(r'^\s*\[|\]\s*$', '', s)

        
        s = (
            s.replace("','", ",")
             .replace("', '", ",")
             .replace('", "', ",")
        )

        s = s.replace("'", "").replace('"', "")

        parts = re.split(r"[,\|;]+", s)
        skills_list = [p.strip() for p in parts if p.strip()]


    projects_raw = sections_for_template.get("projects", "")
    projects_html = str(projects_raw) if projects_raw else ""

   
    profile_filename = portfolio_obj.user.profile_picture or "default-profile.png"
    profile_path = os.path.join(current_app.root_path, "static/profile_pics", profile_filename)
    profile_base64 = get_base64_image(profile_path)

    
    return render_template(
        "preview.html",
        portfolio=sections_for_template,
        slug=slug,
        theme=portfolio_obj.theme or "pastel",
        user=portfolio_obj.user,
        profile_base64=profile_base64,
        public=True,              # ⬅ important!
        skills_list=skills_list,
        projects_html=projects_html,
        format_mode="screen"
    )
@main.route("/download/<slug>")
@login_required
def download_pdf(slug):
    """
    Generates a PDF of the portfolio resume using Playwright and sends it for download.
    """
    
 
    portfolio = Portfolio.query.filter_by(slug=slug, user_id=current_user.id).first_or_404()

   
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_path = temp_pdf.name
    temp_pdf.close()
    
    preview_url = url_for("main.preview_portfolio", slug=slug, _external=True) + "?format=resume"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            page.goto(preview_url, wait_until="networkidle")

            page.wait_for_selector("body.pdf-mode", timeout=10000) 

            page.wait_for_timeout(1000)

            page.emulate_media(media="print")

            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
               
                margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"},
            )

            browser.close()
            
    except Exception as e:
       
        print(f"Playwright PDF generation failed: {e}")
       
        raise e

    
    return send_file(pdf_path, as_attachment=True, download_name=f"{slug}.pdf")

@main.route("/delete_portfolio/<int:portfolio_id>", methods=["POST"])
@login_required
def delete_portfolio(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)

    if portfolio.user_id != current_user.id:
        flash("You are not authorized to delete this portfolio.", "danger")
        return redirect(url_for('main.dashboard'))

    db.session.delete(portfolio)
    db.session.commit()
    flash("Portfolio deleted successfully.", "success")
    return redirect(url_for('main.dashboard'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@main.route('/upload_photo_ajax', methods=['POST'])
@login_required
def upload_photo_ajax():
    if 'photo' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    try:
        picture_file = save_picture(file)
        current_user.profile_picture = picture_file
        db.session.commit()
        return jsonify({"status": "success", "filename": picture_file}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
