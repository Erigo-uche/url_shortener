from flask import Blueprint, redirect, request, url_for, session, render_template, current_app, abort
from app import db, utils
import hashlib


links_bp = Blueprint("links", __name__)

@links_bp.route("/dashboard", methods=["GET", "POST"])
def home():
    try:
        user_id = session.get("user_id")
        
        if not user_id:
            return redirect(url_for("auth.login"))
        
        links = db.get_links(user_id)
        
        short_url = None
        
        if request.method == "POST":
            original_url = request.form["original_url"]
            if not original_url:
                raise ValueError("URL is required")
            
            url = original_url.strip()

            if url.endswith("/"):
                url = url[:-1]
        
            url_hash = hashlib.sha256(url.encode()).hexdigest()
        
            encrypted_url = utils.encrypt_url(original_url)

            short_url = db.check_existing(user_id, url_hash)

            if not short_url:
                short_url = db.gen_shortc(user_id, encrypted_url, url_hash)

        return render_template(
            "dashboard.html",
            links=links,
            short_url=short_url
        )
    except Exception as e:
        current_app.logger.exception("Error loading main page: %s", e)
        raise
    
@links_bp.route("/<short_code>")
def redirect_link(short_code):

    url = db.get_redirect_url(short_code)

    if not url:
        abort(404)
        
    return redirect(url)


    
    
