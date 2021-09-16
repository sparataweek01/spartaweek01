from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('3.34.5.163', 27017, username="test", password="test")
db = client.dbsparta_plus_week4



# 로그인 영역

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        matjips = list(db.matjips.find({}, {"_id": False}))
        recipes = list(db.recipes.find({}, {"_id": False}))
        return render_template('index.html', user_info=user_info, msg="로그인 완료", matjips=matjips, recipes=recipes)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    print(result)

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        'username': username_receive,
        'password': password_hash,
        'profile_name': username_receive,
        'profile_pic': "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        'profile_info': ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# 아이디 중복확인

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({'username': username_receive}))
    return jsonify({'result': 'success', 'exists': exists} )


# 검색창
@app.route('/home')
def receipe():
    return render_template('home.html')


#  검색로직
@app.route('/home/posts',  methods=['POST'])
def search():
    keyword = request.form['keyword_give']
    result1 = list(db.recipes.find({'title': {"$regex": keyword}}))
    result2 = list(db.recipes.find({'title2': {"$regex": keyword}}))
    result3 = list(db.recipes.find({'title3': {"$regex": keyword}}))
    posts = result1 + result2 + result3
    tempposts = list({post['_id']: post for post in posts}.values())
    finalposts = []
    for temppost in tempposts:
        temppost['_id'] = ""
        finalposts.append(temppost)
    return jsonify({'result': 'success', 'posts': finalposts})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)




