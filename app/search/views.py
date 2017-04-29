from flask import request, url_for, redirect, abort
from . import search
from ..models import User, Post, Node


@search.route('/', methods=['POST', 'GET'])
def search():
    text = request.form['text']

    if request.form['type'] == 'post':
        post = Post.query.filter_by(title=text).first()
        if post:
            return redirect(url_for('main.post', id=post.id))
        else:
            abort(404)

    if request.form['type'] == 'node':
        return redirect(url_for('main.node', nodename=text))

    if request.form['type'] == 'user':
        return redirect(url_for('main.user', username=text))
