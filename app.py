from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class NewUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class EditUserForm(FlaskForm):
    username = StringField('ユーザ名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('新しいパスワード', validators=[DataRequired()])

class LoginForm(FlaskForm):
    student_id = IntegerField('学籍番号', validators=[DataRequired("学籍番号を入力してください。")])
    password = PasswordField('パスワード', validators=[DataRequired("パスワードを入力してください。")])

class UserForm(FlaskForm):
    student_id = IntegerField('学籍番号', validators=[DataRequired("学籍番号を入力してください。")])
    username = StringField('ユーザ名', validators=[DataRequired("ユーザ名を入力してください。")])
    password = PasswordField('パスワード', validators=[DataRequired("パスワードを入力してください。")])
    faculty = StringField('学部', validators=[Length(max=200)])
    department = StringField('学科', validators=[Length(max=200)])
    course = StringField('コース', validators=[Length(max=200)])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, nullable=False, unique=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    faculty = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(200), nullable=True)
    course = db.Column(db.String(200), nullable=True)

    def __str__(self):
        return f'学籍番号：{self.student_id} ユーザ名：{self.username}'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
@app.route('/top')
def top():
     posts = Post.query.all()
     return render_template('top.html', posts=posts)  




@app.route('/index')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/post', methods=['POST'])
def post():
    title = request.form['title']
    content = request.form['content']
    category = request.form['category']
    new_post = Post(title=title, content=content, category=category)
    db.session.add(new_post)
    db.session.commit()
    flash('投稿完了しました')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('query')
    if query:
        posts = Post.query.filter(Post.content.contains(query)).all()
    else:
        posts = Post.query.all()
    return render_template('search.html', posts=posts, query=query)

@app.route('/category')
def category():
    category = request.args.get('category')
    if category:
        posts = Post.query.filter_by(category=category).all()
    else:
        posts = Post.query.all()
    return render_template('category.html', posts=posts)

@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    form = UserForm()
    if request.method == "POST" and form.validate_on_submit():
        student_id = form.student_id.data
        username = form.username.data
        password = form.password.data
        faculty = form.faculty.data
        department = form.department.data
        course = form.course.data

        # すでに学籍番号が登録されているかを確認
        user = User.query.filter_by(student_id=student_id).first()
        if user:
            flash('この学籍番号は既に登録されています。')
            return render_template("new_user.html", form=form)

        new_user = User(student_id=student_id, username=username, password=password, faculty=faculty, department=department, course=course)
        db.session.add(new_user)
        db.session.commit()
        flash('登録が完了しました。ログインページにリダイレクトします。')
        return redirect(url_for("login"))  # ログイン画面にリダイレクト
    
    return render_template("new_user.html", form=form)


@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        student_id = form.student_id.data
        password = form.password.data
        
        user = User.query.filter_by(student_id=student_id, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for("top"))
        else:
            flash('学籍番号またはパスワードが間違っています。')
    
    return render_template("login.html", form=form)

# 投稿の削除機能
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('投稿が削除されました')
    return redirect(url_for('index'))
@app.route('/mypage')
def mypage():
    # ここではユーザー情報を表示するためのコードを追加
    # セッションからユーザーIDを取得して、ユーザー情報を表示するなど
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('mypage.html', user=user)
    else:
        flash('ログインしてください。')
        return redirect(url_for('login'))




@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    form = EditUserForm()
    if 'user_id' not in session:
        flash('ログインしてください。')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if form.validate_on_submit():
        user.username = form.username.data
        user.password = form.password.data
        db.session.commit()
        flash('ユーザー情報が更新されました。')
        return redirect(url_for('mypage'))

    # フォームに現在のユーザー情報をセット
    form.username.data = user.username

    return render_template('edit_user.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
