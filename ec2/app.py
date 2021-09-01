#!/usr/bin/env python3
from flask import Flask, request, Response, abort, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_table import Table, Col
from collections import defaultdict
from dynamo import scan_dynamodb, put_dynamodb, delete_dynamodb

app = Flask(__name__)

class LoginInfo(object):
    def __init__(self, Date, Time, User, Emotion):
        self.Date = Date 
        self.Time = Time
        self.User = User
        self.Emotion = Emotion

class LoginTable(Table):
      Date = Col('ログインした日')
      Time = Col('ログインした時間')
      User = Col('ユーザ名')
      Emotion = Col('感情')

class Item(object):
    def __init__(self, Name, ImageName, NewFeed, TrainInfo, WorkPlace):
        self.Name = Name
        self.ImageName = ImageName
        self.NewFeed = NewFeed
        self.TrainInfo = TrainInfo
        self.WorkPlace = WorkPlace

class ItemTable(Table):
      Name = Col('ユーザ名')
      ImageName = Col('顔画像')
      NewFeed = Col('ニュースフィード')
      TrainInfo = Col('路線情報')
      WorkPlace = Col('勤務地')

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# ログイン用ユーザー作成
# パスワードは各自任意のものを設定してください。
users = {
    1: User(1, ＜ユーザ名①＞, ＜パスワード①＞),
    2: User(2, ＜ユーザ名②＞, ＜パスワード②＞)
}

# ユーザーチェックに使用する辞書作成
nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/')
def home():
    return Response("home: <a href='/login/'>Login</a> <a href='/logout/'>Logout</a>")

# ログインしないと表示されないパス
#@app.route('/protected/')
#@login_required
#def protected():
#    return Response('''
#    protected<br />
#    <a href="/logout/">logout</a>
#    ''')

# ログインパス
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return Response('''
            login success!<br />
            <a href="/userlist/">ユーザ管理</a><br />
            <a href="/loginInfo/">ログイン情報</a><br />
            <a href="/logout/">logout</a>
            ''')
        else:
            return abort(401)
    else:
        return render_template("login.html")

# ログアウトパス
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return Response('''
    logout success!<br />
    <a href="/login/">login</a>
    ''')

# ユーザ一覧の表示 
@app.route('/userlist/')
@login_required
def userlist():
#    ulist=scan_dynamodb("Users")
#    return render_template('ulist.html')
    ulist=scan_dynamodb("Users")

    items = []
    for user in ulist:
        items.append(Item(user["Name"],user["ImageName"],user["NewFeed"],user["TrainInfo"],user["WorkPlace"]))

    table = ItemTable(items)

    print(table.__html__())
    return render_template('table.html',title='登録ユーザ一覧',table=table)
    
# ログイン情報の表示 
@app.route('/loginInfo/')
@login_required
def loginInfo():
    llist = scan_dynamodb("LoginInfo")

    uitems=[]
    for llog in llist:
        uitems.append(LoginInfo(llog["Date"],llog["Time"],llog["UserName"],llog["Emotion"]))
    table = LoginTable(uitems)

    print(table.__html__())
    return render_template('table.html',title='ユーザ　ログイン情報',table=table)

# ユーザ登録
@app.route('/register/', methods=["GET", "POST"])
def register():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return Response('''
            login success!<br />
            <a href="/userlist/">ユーザ管理</a><br />
            <a href="/loginInfo/">ログイン情報</a><br />
            <a href="/logout/">logout</a>
            ''')
        else:
            return abort(401)
    else:
        return render_template("login.html")

if __name__ == '__main__':
    
    app.run(host="0.0.0.0",port=5000,debug=True)
