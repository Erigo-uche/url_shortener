import os 
import psycopg2
from flask import current_app
import bleach
from hashids import Hashids
from app import utils
 

Database_url = os.getenv("DATABASE_URL")


hashids = Hashids(
    salt=os.getenv("HashID_SALT"), 
    min_length=6
)

def db_connect():
    return psycopg2.connect(Database_url)

def store_info(username, email, p_hash):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("INSERT INTO users(username, email, password_hash) VALUES (%s, %s, %s)", 
                          (bleach.clean(username), bleach.clean(email), p_hash))
    except psycopg2.Error:
        current_app.logger.exception("Failed to load user's info")
        raise

def check_existing_users(email):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("SELECT email FROM  users WHERE email = %s", (email,))
                existing_user = c.fetchone()
                if existing_user:
                    return True
                return None
    except psycopg2.Error:
        current_app.logger.exception("Failed to check existing email")
        raise


def valid_p(email):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
                proof = c.fetchone() 
                return proof
    except psycopg2.Error:
        current_app.logger.exception("Failed to fetch data")
        raise

def gen_shortc(user_id, encrypted_url, url_hash, title):
    try:
        new_short_url = None
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("""INSERT INTO links(
                          user_id,
                          encrypted_url,
                          url_hash,
                          title) 
                          VALUES(%s, %s, %s, %s) RETURNING id 
                          """,(user_id, encrypted_url, url_hash, title)
                          )
                link_id = c.fetchone()[0]
                short_code = hashids.encode(link_id)

                c.execute("""UPDATE links 
                          SET short_code = %s
                          WHERE id = %s""", (short_code, link_id) 
                          )
                new_short_url = f"{short_code}"
                return new_short_url
    except psycopg2.Error:
        current_app.logger.exception("Failed to form short_code")
        raise 


def check_existing(user_id, url_hash):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("""SELECT short_code, deleted_at FROM links
                WHERE user_id = %s AND url_hash = %s""", (user_id, url_hash))
                result=c.fetchone()
                if not result:
                    return None
                
                short_code, deleted_at = result

                if deleted_at is None:
                    return {
                        "active": True,
                        "short_code":short_code
                    }
                
                return {
                    "active": False,
                    "short_code": None
                }
                  
    except psycopg2.Error:
        current_app.logger.exception("Failed to search url_hash")
        raise
    

def get_links(user_id):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("""SELECT 
                          short_code,
                          title,
                          clicks
                          FROM links 
                          WHERE user_id = %s
                          AND deleted_at is NULL
                          ORDER BY created_at DESC """, (user_id,))
                return c.fetchall()
    except psycopg2.Error:
        current_app.logger.exception("Failed to fetch links")
        raise

def get_redirect_url(short_code):
    try: 
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("UPDATE links SET clicks = clicks + 1 WHERE short_code = %s AND deleted_at is NULL RETURNING encrypted_url", (short_code,))
                result = c.fetchone()
                if not result:
                    return None
                url = utils.decrypt_url(result[0])
                if not url:
                    return Exception("Failed decryption") 
                                   
                return url
    except psycopg2.Error:
        current_app.logger.exception("Failed to get url")
        raise

def delete_link(user_id, short_code):
    try:
        with db_connect() as conn:
            with conn.cursor() as c: 
                c.execute("""UPDATE links SET deleted_at = NOW()
                          WHERE user_id=%s
                          AND short_code=%s
                          AND deleted_at IS NULL""", (user_id, short_code))
    except psycopg2.Error:
        current_app.logger.exception("Failed to delete link")
        raise

def deletd_list(user_id):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("""SELECT short_code, title, clicks, deleted_at 
                          FROM links WHERE user_id=%s AND deleted_at IS NOT NULL
                          ORDER BY deleted_at DESC""", (user_id,))
                return c.fetchall()
    except psycopg2.Error:
        current_app.logger.exception("Failed to fetch deleted links")
        raise

def restore(user_id, short_code):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("""UPDATE links SET deleted_at = NULL
                          WHERE user_id=%s
                          AND short_code=%s""", (user_id, short_code))
    except psycopg2.Error:
        current_app.logger.exception("Failed to restore link")
        raise
 
def clear_link(user_id, short_code):
    "Hard delete: permanently removes a link row."
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                c.execute("""DELETE FROM links 
                          WHERE
                          user_id=%s AND
                          short_code=%s AND
                          deleted_at IS NOT NULL
                          RETURNING True""", (user_id, short_code))
                deleted = c.fetchone()
            conn.commit()
        return deleted
    except psycopg2.Error:
        current_app.logger.exception("Error in delete process")
        raise
    
def update_link(user_id, old_code, new_code, title):
    try:
        with db_connect() as conn:
            with conn.cursor() as c:
                if old_code != new_code:
                    c.execute("SELECT id FROM links WHERE short_code=%s", (new_code,))
                    if c.fetchone():
                        return "taken"
                c.execute("""UPDATE links SET
                          short_code=%s,
                          title=%s WHERE
                          user_id=%s AND
                          short_code=%s""", (new_code, title, user_id, old_code))
            conn.commit()
        return "updated"
    except psycopg2.Error:
        current_app.logger.exception("Failed in update process!")
        raise
