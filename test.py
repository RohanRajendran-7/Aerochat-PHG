from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
from Search import search_past_24_hours_with_selenium

app = Flask(__name__)

pymysql.install_as_MySQLdb()

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://rohan_aerochat:rohan_aerochat@db4free.net:3306/aerochat_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Keywords(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    keywords = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)

class Sentiments(db.Model):
    sentiment_id  = db.Column(db.Integer, primary_key  = True)
    sentiment_type = db.Column(db.String, nullable = False)

class Results(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    link = db.Column (db.String)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_content_match = db.Column(db.Integer, nullable = False)
    is_title_match = db.Column(db.Integer, nullable = False)
    is_complete = db.Column(db.Integer, nullable = False)
    sentiment_id = db.Column(db.Integer, db.ForeignKey('sentiments.sentiment_id'), nullable=False)

class google_search_log(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    search_query = db.Column (db.String)
    search_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    search_result_count = db.Column(db.Integer)
    search_data = db.Column(db.String)

class google_news_log(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    search_query = db.Column (db.String)
    search_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    search_result_count = db.Column(db.Integer)
    search_data = db.Column(db.String)

    
@app.route('/')
def dashboard():
    try:
        new_results = Results.query.filter_by(is_complete = 0).all()
        
        if new_results:
            results = [{"id":result.id, "link": result.link, "created_date" : result.created_date, "is_content_match": result.is_content_match, "is_title_match": result.is_title_match, "sentiment": result.sentiment_id} for result in new_results]
            return render_template('dashboard.html', keywords = results)
        else:
            return render_template('dashboard.html')
    except Exception as e:
        return f"An Error Occurred : {str(e)}", 500

@app.route('/users') 
def users():
    try:
        users = User.query.all()

        if users:
            results = [{"id": user.id, "username": user.username, "password": user.password} for user in users]
            return jsonify(results)
        else:
            return "No users found in the database.", 404

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Missing 'username' or 'password' in request data"}), 400

        new_user = User(username=data['username'], password=data['password'])

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User added successfully", "id": new_user.id, "username": new_user.username}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/keyword_list', methods = ['GET'])
def GetKeywordList():
    try:
        results = []
        keywords_list = Keywords.query.all()
        if keywords_list:
            results = [{"id": keyword.id, "keyword": keyword.keywords, "created_at": keyword.created_date} for keyword in keywords_list]
            print(results)
            return render_template('keywords.html', keywords = results)
        else:
            return render_template('keywords.html', keywords = results)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
@app.route('/add_keywords', methods = ['POST'])
def AddNewKeyword():
    new_keyword  = request.form.get('keyword')
    print(new_keyword, "new")
    keyword = Keywords(
        keywords = new_keyword )
    try:
        db.session.add(keyword)
        db.session.commit()
        return jsonify({
            "message": "Keyword successfully created",
            "status": "success",
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting keyword: {e}")
        
    finally:
        db.session.remove()
    

@app.route('/positive', methods=['GET'])
def positiveLinks():
    try:
        
        links_positive = Results.query.filter_by(is_complete=1, sentiment_id=1).all()
        
        if links_positive:
            results = [{
                "id": result.id, 
                "link": result.link, 
                "created_date": result.created_date, 
                "is_content_match": result.is_content_match, 
                "is_title_match": result.is_title_match, 
                "sentiment": result.sentiment_id
            } for result in links_positive]
            print(results)
            return render_template('positive.html', keywords=results)
        else:
            return render_template('positive.html', keywords=[])
    except Exception as e:
        return render_template('positive.html', error=str(e))

@app.route('/negative', methods=['GET'])
def negativeLinks():
    try:
        
        links_negative = Results.query.filter_by(is_complete=1, sentiment_id=2).all()
        
        if links_negative:
            results = [{
                "id": result.id, 
                "link": result.link, 
                "created_date": result.created_date, 
                "is_content_match": result.is_content_match, 
                "is_title_match": result.is_title_match, 
                "sentiment": result.sentiment_id
            } for result in links_negative]
            print(results)
            return render_template('negative.html', keywords=results)
        else:
            return render_template('negative.html', keywords=[])
    except Exception as e:
        return render_template('negative.html', error=str(e))
    
@app.route('/neutral', methods=['GET'])
def neutralLinks():
    try:
        
        links_neutral = Results.query.filter_by(is_complete=1, sentiment_id=3).all()
        
        if links_neutral:
            results = [{
                "id": result.id, 
                "link": result.link, 
                "created_date": result.created_date, 
                "is_content_match": result.is_content_match, 
                "is_title_match": result.is_title_match, 
                "sentiment": result.sentiment_id
            } for result in links_neutral]
            print(results)
            return render_template('neutral.html', keywords=results)
        else:
            return render_template('neutral.html', keywords=[])
    except Exception as e:
        return render_template('neutral.html', error=str(e))

@app.route('/updateSentiment', methods = ['POST'])
def updateSentiment():
    try:
        sentiment = request.form.get('sentiment')
        keyword_id = int(request.form.get('keyword_id'))
        print(keyword_id, "tsr", sentiment)
        keyword = Results.query.get(keyword_id)
        if keyword:
            print(keyword)
        if str(sentiment).lower() == 'positive':
            keyword.sentiment_id = 1
            keyword.is_complete = 1
        elif str(sentiment).lower() == 'negative':
            keyword.sentiment_id = 2
            keyword.is_complete = 1
        elif str(sentiment).lower() == 'neutral':
            keyword.sentiment_id = 3
            keyword.is_complete = 1
        db.session.add(keyword)
        db.session.commit()
        return jsonify({
                "status": "success",
                "message": "Sentiment successfully Updated",
            }), 200
    except Exception as e :
        db.session.rollback()
        print(f"Error updating sentiment: {e}")
        return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500
    finally:
        db.session.remove()

@app.route('/cronUpdate', methods = ['POST', 'GET'])
def cronUpdate():
    keywords_list_latest = []
    keywords_list = Keywords.query.all()
    try:
        for keyword in keywords_list:
            keywords_list_latest.append(str(keyword.keywords))
            final_result = search_past_24_hours_with_selenium(str(keyword.keywords))
            for keyword_entry in final_result:
                keyword = keyword_entry['keyword']
                results = keyword_entry['results']

                # Iterate through the results for each keyword
                for result in results:
                    url = result['url']
                    title = result['title']
                    is_title_match = result['is_title_match']
                    is_content_match = result['is_content_match']
                    match_type = result['match_type']
                    existing_result = Results.query.filter_by(link=url).first()
                    if not existing_result:
                        # If not found, insert the result into the Results table
                        new_result = Results(
                            link=url,
                            created_date=datetime.utcnow(),
                            is_content_match=1 if is_content_match else 0,
                            is_title_match=1 if is_title_match else 0,
                            is_complete=0,
                            sentiment_id=None
                        )
                        # Add to the session and commit
                        db.session.add(new_result)
                        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Cron job completed and results updated.'})
    except Exception as e:
        db.session.rollback()
        print(f"Error in Cron: {e}")
        return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500
    finally:
        db.session.remove()
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
