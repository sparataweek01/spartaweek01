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
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"
# ㄴ 파일을 업로드하기위한 환경 설정 werkzeug을 임포트 해야한다

SECRET_KEY = 'PIGGIY_LIFE'
# jwt 디코딩 할 때의 시크릿 키
# 어플리케이션 설정 순서가 중요하다

client = MongoClient('13.209.85.240', 27017, username="test", password="test")
db = client.db_hh_w1_g31


# 메인 페이지 회원가입 관련 페이지
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
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


# 메인 페이지 입장
@app.route('/main', methods=['GET'])
def main():
    # 추천 목록 자동으로 띄워주기
    # likes = db.recipes.find({}, {'_id': False})('like')
    top_ten_recipes = list(db.recipes.find({}).sort("like", -1).limit(10))
    top_ten_matjips = list(db.matjips.find({}).sort("like", -1).limit(10))
    # 탑_텐_레시피스에 좋아요(like)를 내림차순(-1)으로 정렬한 다음 위에서 10개의 딕셔너리들만 리스트로 만든다.

    return jsonify({'result': 'success', 'top_ten_Recipes': top_ten_recipes, 'top_ten_matjips': top_ten_matjips})


# 로그인 페이지
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})
    print(result)

    if result is not None:
        # ㄴ result에 유저이름과 패스워드가 일치하는 것을 찾는다면 이라는 뜻!
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
        # ㄴ 같은 id/pw 조합을 찾지 못한다면 도출


# 회원가입
@app.route('/sign_up', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # location_receive = request.form['location_give'] # 사는 지역

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # ㄴ 패스워드를 해시함수로 변경하여 저장

    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호_해시
        # "location": location_receive # 사는 -시
    }
    # "profile_info": ""  # 프로필 한 마디
    # "profile_name": username_receive,  # 프로필 이름 기본값은 아이디 초기 설정 불가능 추후에 본인이 변경 할 수 있음
    # "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지 #스테틱에 있어야함
    # "profile_pic": "",  # 프로필 사진 파일 이름

    db.users.insert_one(doc)

    return jsonify({'result': 'success'})


# 아이디 중복확인!
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# index > '안에서' 클릭시
@app.route('/athome')
def recipe_page():
    # 인덱스.html 의 안에서 를 클릭하면 project.html로 보낸다
    return render_template('project_sc.html')


# 전체 맛집 리스트 출력
@app.route("/api/matjip_lists", methods=['GET'])
def matjip_lists():
    matjip_list_db = list(db.matjips.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'msg': '전체 맛집 리스트 연결 완료!', 'all_matjip_list': matjip_list_db})

# 해야하는 것 ----------------------------------------------------------------------------------------
# 원하는 맛집 검색
@app.route('/api/search_matjip', methods=['GET'])
def search_matjip():
    word_receive = request.form['word_give']
    result_list = list(db.matjips.find({}))

    for result in result_list:
        if word_receive in result:
            print(result)
        searched_matjips = list.append(result)

    # 구현중..생각보다 어렵네요 ㅠㅠ
    return jsonify({'result': 'success', 'msg': '맛집 검색 연결 완료!', 'searched_matjips': searched_matjips})


# 전체 레시피 리스트 조회
@app.route('/recipe_lists', methods=['GET'])
def recipe_lists():
    recipe_list_db = list(db.recipes.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'msg': '전체 레시피 리스트 조회 완료!', 'all_recipe_list': recipe_list_db})


# 추천 맛집 리스트 조회
@app.route('/rcd_matjip_list', methods=['GET'])
def rcd_matjip_list():
    title_receive = request.form['title_give']
    category_receive = request.form['category_give']
    like_count_receive = request.form['like_count_give']
    # img 파일도 불러오기?
    # 또 불러올 요소를 파학해야함!

    # 아래의 코드는 자스 or 서버 어떻게 할 지 정해지면 마저 작성!
    if like_count_receive > 1000:
        matjip_list_db = list(
            db.matjips.find({'title': title_receive, 'category': category_receive, 'like': like_count_receive},
                            {'_id': False}))
        return jsonify({'result': 'success', 'msg': '추천 맛집 연결 완료!', 'rcd_matjip_list': matjip_list_db})
    else:
        return jsonify({'result': 'success', 'msg': '추천 맛집 연결 실패!'})

    # 이건 자바스크립트에서 할 지, 아니면 서버단에서 보내줄 지 정해함! 개인적으로 temp_html로 붙이는게 더 나을 것 같은 것이
    # 페이지가 새로고침 될 때 갱신된 리스트가 나오는게 더 나을 것 같아서!
    # 서버에서 하려면 for 문!!


# 추천 레시피 리스트 조회
@app.route('/api/rcd_recipe_list', methods=['GET'])
def rcd_recipe_list():
    title_receive = request.form['title_give']
    category_receive = request.form['category_give']
    like_count_receive = request.form['like_count_give']
    # img 파일도 불러오기?
    # 또 불러올 요소를 파학해야함!

    # 아래의 코드는 자스 or 서버 어떻게 할 지 정해지면 마저 작성!
    if like_count_receive > 1000:  # 조건은 수정해야함!
        recipe_list_db = list(
            db.recipes.find({'title': title_receive, 'category': category_receive, 'like': like_count_receive},
                            {'_id': False}))
        return jsonify({'result': 'success', 'msg': '추천 맛집 연결 완료!', 'rcd_recipe_list': recipe_list_db})
    else:
        return jsonify({'result': 'success', 'msg': '추천 맛집 연결 실패!'})

    # 이건 자바스크립트에서 할 지, 아니면 서버단에서 보내줄 지 정해함! 개인적으로 temp_html로 붙이는게 더 나을 것 같은 것이
    # 페이지가 새로고침 될 때 갱신된 리스트가 나오는게 더 나을 것 같아서!
    # 서버에서 하려면 for 문!!


# 나의 레시피 저장
@app.route('/my_recipe_save', methods=['POST'])
def my_recipe_save():
    title_receive = request.form['title_give']
    ingredients_receive = request.form['ingredients_give']
    process_receive = request.form['process_give']
    time_receive = request.form['time_give']
    cost_receive = request.form['cost_give']
    review_receive = request.form['review_give']
    # level_receive = request.form['recipe_level_give']
    posting_time = datetime.now()  # 새로고침을 해야 갱신된다. >> reload 가 필요함

    doc = {
        'title': title_receive,
        'ingredients': ingredients_receive,
        'process': process_receive,
        'time': time_receive,
        'cost': cost_receive,
        'review': review_receive,
        'recipe_img': "",
        'recipe_img_real': "",
        'posting_time': posting_time,
        # 'level': level_receive,
        # 'img': img_receive,
    }

    db.recipes.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '레시피 등록 완료!'})


# 해야하는 것 ----------------------------------------------------------------------------------------
# 원하는 레시피 검색
@app.route('/searching_recipe', methods=['GET'])
def searching_recipe():
    # 모든 데이터 베이스 항목에서 검색
    # 필터 : 1. 작성 시간 // 2. user id

    word_receive = request.form['word_give']
    result_list = list(db.recipes.find({'$**': word_receive}, {'_id': False}))
    # ㄴ $** 은 모든 카테고리에 검색하는 것
    print(result_list)

    return render_template('')


# 해야하는 것 ----------------------------------------------------------------------------------------
# 좋아요 업데이트
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 사진 저장
@app.route('/save_img', methods=['POST'])
def save_img():
    # 음식을 등록할 때 사진을 올릴 수 있게 하는 기능
    try:
        name_receive = request.form["name_give"]
        new_doc = {"title": name_receive}
        if 'file_give' in request.files:
            # ㄴ 리퀘스츠로 가져온 파일에 'filegive'가 있으면
            file = request.files["file_give"]
            # ㄴ 파일기브! 이것이 지정한 파일이다
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{filename}.{extension}"
            file.save("./static/" + file_path)
            new_doc["recipe_img"] = f"{name_receive}.{extension}"
            new_doc["recipe_img_real"] = file_path
        db.recipes.update_one({'title': name_receive}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '이미지를 업로드 했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("project_sc"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    # ㄴ 괄호안에 옵션이 없다면 default는 127.0.0.1:5000
    # host : 127.0.0.1 =localhost
    # port : 5000 = 포트의 디폴트 값
    # debug : true일 경우, 동작 중 서버내용 변경이 일어나면 자동으로 리로드 >> 그 파란화면 디버깅
    # 기타 옵션이 있다.
    # ㄴ run()의 각종 옵션들
