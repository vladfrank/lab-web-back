from flask import Blueprint, render_template, request, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from db.models import users, articles
from flask_login import (
    login_user, login_required,
    logout_user, current_user
)

lab8 = Blueprint('lab8', __name__)


@lab8.route('/lab8/')
def main():
    return render_template('lab8/lab8.html')


@lab8.route('/lab8/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')

    if not login_form or not password_form:
        return render_template(
            'lab8/register.html',
            error='Логин и пароль обязательны'
        )

    if users.query.filter_by(login=login_form).first():
        return render_template(
            'lab8/register.html',
            error='Пользователь уже существует'
        )

    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)

    db.session.add(new_user)
    db.session.commit()

    # автологин
    login_user(new_user)

    return redirect('/lab8/')


@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = users.query.filter_by(login=login_form).first()

    if user and check_password_hash(user.password, password_form):
        login_user(user, remember=remember)
        return redirect('/lab8/')

    return render_template(
        'lab8/login.html',
        error='Неверный логин или пароль'
    )


from sqlalchemy import or_

@lab8.route('/lab8/articles')
def article_list():
    search = request.args.get('q', '')

    base_filter = articles.title.ilike(f'%{search}%') | \
                  articles.article_text.ilike(f'%{search}%')

    if current_user.is_authenticated:
        article_list = articles.query.filter(
            base_filter,
            or_(
                articles.is_public == True,
                articles.login_id == current_user.id
            )
        ).all()
    else:
        article_list = articles.query.filter(
            base_filter,
            articles.is_public == True
        ).all()

    return render_template(
        'lab8/articles.html',
        articles=article_list
    )


@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8/')


@lab8.route('/lab8/articles/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create_article.html')

    title = request.form.get('title')
    text = request.form.get('text')

    if not title or not text:
        return render_template(
            'lab8/create_article.html',
            error='Все поля обязательны'
        )

    is_public = True if request.form.get('is_public') else False

    article = articles(
        title=title,
        article_text=text,
        login_id=current_user.id,
        is_public=is_public
    )

    db.session.add(article)
    db.session.commit()

    return redirect('/lab8/articles')


@lab8.route('/lab8/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.get_or_404(article_id)

    # 🔐 защита
    if article.login_id != current_user.id:
        return "Доступ запрещён", 403

    if request.method == 'GET':
        return render_template(
            'lab8/edit_article.html',
            article=article
        )

    article.title = request.form.get('title')
    article.article_text = request.form.get('text')

    db.session.commit()
    return redirect('/lab8/articles')


@lab8.route('/lab8/articles/delete/<int:article_id>')
@login_required
def delete_article(article_id):
    article = articles.query.get_or_404(article_id)

    # 🔐 защита
    if article.login_id != current_user.id:
        return "Доступ запрещён", 403

    db.session.delete(article)
    db.session.commit()

    return redirect('/lab8/articles')
