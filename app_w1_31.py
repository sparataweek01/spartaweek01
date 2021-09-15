from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)

client = MongoClient('13.209.85.240', 27017, username="test", password="test")
# ㄴ 이건 제 EC2 ip입니다 너무 헤집어놓지 않으시길..
db = client.db_hh_w1_g31

SECRET_KEY = 'PIGGIY_LIFE'
# jwt 디코딩 할 때의 시크릿 키


# 메인 페이지 입장
@app.route('/')
def main():
    result = '메인 로그인 페이지 sign_in을 통과해야 들어올 수 있어요!'
    return result


# 로그인 페이지
@app.route('/sign_in')
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입 페이지
@app.route('/sign_up')
def sign_up():

    username_receive = request.form['username_give'] #이름이 두번 써져서 나온 줄
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디 초기 설정 불가능 추후에 본인이 변경 할 수 있음
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지 #스테틱에 있어야함
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 전체 맛집 리스트 출력
@app.route("/api/matjip_lists", methods=['GET'])
def matjip_lists():

    matjip_list_db = list(db.matjips.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'msg': '전체 맛집 리스트 연결 완료!', 'all_matjip_list': matjip_list_db})


# 원하는 맛집 검색
@app.route('/api/search_matjip', methods=['GET'])
def search_matjip():

    title_receive = request.form['title_give']
    category_receive = request.form['category_give']
    like_count_receive = request.form['like_count_give']

    searched_matjip_list_db = list(db.matjips.find(
        {
            'title': title_receive,
            'category': category_receive,
            'like': like_count_receive
        }, {'_id': False}
    ))

    return jsonify({'result': 'success', 'msg': '맛집 검색 연결 완료!', 'searched_matjip_list': searched_matjip_list_db})


    # -------------------------------------------
    # 검색을 어떻게 할 것 인지 가게명, 내용 한번에?
    # 아니면 복수 조건으로?

    word_receive = request.form['word_give']
    result_list = list(db.recipes.find({'$**': word_receive}, {'_id': False}))
    # ㄴ $** 은 모든 카테고리에 검색하는 것
    print(result_list)


# 전체 레시피 리스트 조회
@app.route('/api/recipe_lists', methods=['GET'])
def recipe_lists():

    recipe_list_db = list(db.recipes.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'msg': '전체 레시피 리스트 조회 완료!', 'all_recipe_list': recipe_list_db})


# 추천 맛집 리스트 조회
@app.route('/api/rcd_matjip_list', methods=['GET'])
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
    if like_count_receive > 1000: #조건은 수정해야함!
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
@app.route('/api/my_recipe_save', methods=['POST'])
def my_recipe_save():

    title_receive = request.form['title_give']
    subtitle_receive = request.form['subtitle_give']
    detail_receive = request.form['detail_give']
    category_receive = request.form['category_give']
    img_receive = request.form['img_give'] # 사진에 대한 코드는 수정 필요
    smtg1_receive = request.form['mtg1_give']
    smtg2_receive = request.form['smtg2_give']

    doc = {
        'title': title_receive,
        'subtitle': subtitle_receive,
        'detail': detail_receive,
        'category': category_receive,
        'img': img_receive,
        'smtg1': smtg1_receive,
        'smtg2': smtg2_receive
    }
    db.recipes.insert_one(doc)

    return jsonify({'msg': '레시피 등록 완료!'})


# 레시피 검색
@app.route('/api/searching_recipe', methods=['GET'])
def searching_recipe():
    # 검색을 어떻게 할 것 인지 가게명, 내용 한번에?
    # 아니면 복수 조건으로?

    word_receive = request.form['word_give']
    result_list = list(db.recipes.find({'$**': word_receive}, {'_id': False}))
    # ㄴ $** 은 모든 카테고리에 검색하는 것
    print(result_list)

    return render_template('')


# 좋아요 업데이트
@app.route('/api/update_like', methods=['POST'])
def update_like():

    # 수정 필요!!!!-----------------------------------
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
@app.route('/api/save_img', methods=['POST'])
def save_img():

    # 수정 필요!!!!-----------------------------------

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



# 마킹 저장
@app.route('/api/marking', methods=['POST'])
def marking():
    # 북마크는 뺄까요?!! -------------------------------------

    title_receive = request.form["title_give"]
    address_receive = request.form["address_give"]
    x_receive = request.form["x_give"]
    y_receive = request.form["y_give"]
    change_receive = request.form["change_give"]

    print(title_receive, address_receive, x_receive, y_receive, change_receive)

    if change_receive == "marked":
        db.matjips.update_one({"title": title_receive, "address": address_receive, "mapx": x_receive, "mapy": y_receive}, {"$set": {"marked": True}})
    else:
        db.matjips.update_one({"title": title_receive, "address": address_receive, "mapx": x_receive, "mapy": y_receive}, {"$unset": {"marked": False}})
    return jsonify({'result': 'success'})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    # ㄴ 괄호안에 옵션이 없다면 default는 127.0.0.1:5000
        # host : 127.0.0.1 =localhost
        # port : 5000 = 포트의 디폴트 값
        # debug : true일 경우, 동작 중 서버내용 변경이 일어나면 자동으로 리로드 >> 그 파란화면 디버깅
        # 기타 옵션이 있다.
        # ㄴ run()의 각종 옵션들
