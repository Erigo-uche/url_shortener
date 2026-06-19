from flask import Blueprint, redirect, request, url_for, session, render_template, current_app, abort, flash, jsonify
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
        total_clicks = sum(link[2] for link in links)
        
        short_url = None 
        
        if request.method == "POST":
            original_url = request.form["original_url"]
            if not original_url:
                raise ValueError("URL is required")
            
            url = original_url.strip()

            if not url.startswith("http://", "https://"):
                url = "https://" + url
            
            if not utils.valid_url(url):
                raise ValueError("Invalid URL")
        
            url_hash = hashlib.sha256(url.encode()).hexdigest()
        
            encrypted_url = utils.encrypt_url(url)

            title = utils.get_title(url)

            short_url = db.check_existing(user_id, url_hash)

            if not short_url:
                short_url = db.gen_shortc(user_id, encrypted_url, url_hash, title)

            flash(short_url, "generated_link")
            
            return redirect(url_for("links.home"))

        return render_template(
            "dashboard.html",
            links=links,
            short_url=short_url,
            total_clicks=total_clicks
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

@links_bp.route("/delete/<short_code>", methods=["POST"])
def delete_link(short_code):
    try:
        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("auth.login"))
        
        db.delete_link(user_id, short_code)

        flash("link successfully deleted")

        return redirect(url_for("links.home"))
    except Exception as e:
        current_app.logger.exception("Failed deleting link: %s", e)
        raise

@links_bp.route("/deleted-links")
def deleted_links():
    user_id = session.get("user_id")

    if not user_id:
        flash("Login required")
        return redirect(url_for("auth.login"))

    links = db.deletd_list(user_id)

    return jsonify([
    {
        "short_code": link[0],
        "title": link[1],
        "clicks": link[2],
        "deleted_at": link[3]
    }
    for link in links
    ])

@links_bp.route("/restore/<short_code>", methods=["POST"])
def restore(short_code):
    user_id = session.get("user_id")

    db.restore(user_id, short_code)

    return jsonify(
        {"success": True}
    )

    
