from flask import Blueprint, render_template, request, make_response, redirect, session
lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5/')
def main():
    return render_template('lab5/lab5.html')