from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# ㄴ 플라스크의 기본 설정으로 템플릿이 변경되면 다시 로드합니다. 설정하지 않으면 디버그 모드에서 활성화됩니다.
app.config["UPLOAD_FOLDER"] = "./static/recipe_imgs"
# ㄴ 파일을 업로드하기위한 환경 설정 werkzeug을 임포트 해야한다

SECRET_KEY = 'PIGGIY_LIFE'
# jwt 디코딩 할 때의 시크릿 키
# 어플리케이션 설정 순서가 중요하다

client = MongoClient('13.209.85.240', 27017, username="test", password="test")
db = client.db_hh_w1_g31


# 메인 페이지 > 로그인 쿠키가 없으면 로그인 페이지로 보내버리기
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        matjips = list(db.matjips.find({}, {"_id": False}))
        recipes = list(db.recipes.find({}, {"_id": False}))
        top_ten_recipes = list(db.recipes.find({}).sort("review", -1).limit(10))

        return render_template('index.html', user_info=user_info, msg="로그인 완료", matjips=matjips, recipes=top_ten_recipes)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    # 로그인창을 통과하면 나오는 화면 다시 회원가입 페이지로 간다
    msg = request.args.get("msg")
    # ㄴurl과 같이오는 msg를 파악한다.
    return render_template('login.html', msg=msg)


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({'username': username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

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


@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

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


# '안에서' 눌렀을 때
@app.route('/home')
def recipe_page():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        all_recipe_list_db = list(db.recipes.find({}, {'_id': False}))
        # 모든 레시피 리스트를 카드에 등록

        return render_template('project.html', user_info=user_info, recipes=all_recipe_list_db )
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# search로직
@app.route('/home/posts',  methods=['POST'])
def search():

    keyword = request.form['keyword_give']

    result1 = list(db.recipes.find({'title': {"$regex": keyword}}))
    result2 = list(db.recipes.find({'title2': {"$regex": keyword}})) #재료
    result3 = list(db.recipes.find({'title3': {"$regex": keyword}})) #다른요소
    posts = result1 + result2 + result3
    tempposts = list({post['_id']: post for post in posts}.values())
    finalposts = []
    for temppost in tempposts:
        temppost['_id'] = ""
        finalposts.append(temppost)
    return jsonify({'result': 'success', 'posts': finalposts})


# 레시피 등록
@app.route('/my_recipe_save', methods=['POST'])
def my_recipe_save():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        print(username)

        title_receive = request.form['title_give']
        subtitle_receive = request.form['subtitle_give']
        ingredients_receive = request.form['ingredients_give']
        process_receive = request.form['process_give']
        time_receive = request.form['time_give']
        cost_receive = request.form['cost_give']
        category_receive = request.form['category_give']
        hashtag_receive = request.form['hashtag_give']
        level_receive = request.form['recipe_level_give']

        if 'file_give' in request.files:
            # ㄴ 리퀘스츠로 가져온 폼데이터에 'filegive'가 있으면
            file = request.files["file_give"]

            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"recipe_imgs/{filename}.{extension}"
            file.save("./static/" + file_path)

            doc = {
                'title': title_receive,
                'ingredients': ingredients_receive,
                'process': process_receive,
                'time': time_receive,
                'cost': cost_receive,
                'subtitle': subtitle_receive,
                'category': category_receive,
                'hashtag': hashtag_receive,
                "recipe_img": f"{title_receive}.{extension}",
                "recipe_img_real": file_path,
                'upload_user': username,
                'view': "",
                'img-url': "",
                'review': "",
            }
        db.recipes_test.insert_one(doc)

        return jsonify({"result": "success", 'msg': '레시피를 업로드 했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("project"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    # ㄴ 괄호안에 옵션이 없다면 default는 127.0.0.1:5000
    # host : 127.0.0.1 =localhost
    # port : 5000 = 포트의 디폴트 값
    # debug : true일 경우, 동작 중 서버내용 변경이 일어나면 자동으로 리로드 >> 그 파란화면 디버깅
    # 기타 옵션이 있다.
    # ㄴ run()의 각종 옵션들
