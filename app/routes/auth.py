from flask import Blueprint, request, redirect, url_for, session, flash, current_app, render_template
from app import db, utils

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET","POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form["username"].strip()
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            existing_user = db.check_existing_users(email)
            if existing_user:
                flash("Email already used")
                return redirect(url_for("auth.register"))

            if not all([username, email, password]):
                return "All fields required"
      
            password_hash = utils.hashp(password)

           
            db.store_info(username, email, password_hash)
            flash("Account created successfully")
    
            return redirect(url_for("auth.login"))
        
        return render_template("register.html")
    
    except Exception as e:
        current_app.logger.exception("Error loading register page: %s", e)
        raise
  

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            if not all([email, password]):
                return "Incomplete field"
            
            user = db.valid_p(email)
            if not user:
                flash("Invalid credentials")
                return redirect(url_for("auth.login"))
            
            user_id = user[0]
            p_hash = user[1]

            p_validation = utils.valp(password, p_hash)
            if not p_validation:
                flash("Invalid password")
                return redirect(url_for("auth.login"))
            
            session["user_id"] = user_id

            flash("Login successful")

            return redirect("/dashboard")
        
        return render_template("login.html") 
    
    except Exception as e:
        current_app.logger.exception("Error loading login page: %s", e)
        raise
    

@auth_bp.route("/logout")
def logout():
    session.clear()

    flash("Logged out")

    return redirect(url_for("auth.login"))