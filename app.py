from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests


app = Flask(__name__)

client = MongoClient('3.34.5.163', 27017, username="test", password="test")
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    msg = request.args.get("msg")
    words = list(db.words.find({}, {"_id": False}))
    print(words)
    return render_template("index.html", words=words, msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    status_receive = request.args.get("status_give", "new")
    # url로 받는 parameter니까 args.get
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}", headers={"Authorization": "Token d48249c2ea738e8467a58758336670a1410c9c41"})
    print(r)
    if r.status_code != 200:
        return redirect(url_for("main", msg="단어가 이상해요"))
    result = r.json()
    print(result)
    return render_template("detail.html", word=keyword, result=result, status=status_receive)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    word_receive = request.form['word_give']
    definition_receive = request.form['definition_give']
    print(word_receive, definition_receive)
    # post 요청으로 받는 변수들이니까 request.form
    doc = {
        'word': word_receive,
        'definition': definition_receive
    }
    db.words.insert_one(doc)
    # 단어 저장하기
    return jsonify({'result': 'success', 'msg': f'단어 "{word_receive}"저장'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word_receive = request.form['word_give']
    db.words.delete_one({'word': word_receive})
    # 단어 삭제하기
    return jsonify({'result': 'success', 'msg': f'단어 {word_receive}삭제'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)