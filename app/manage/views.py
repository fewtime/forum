from flask import render_template, redirect, abort, flash, url_for, \
    request, current_app, make_response
from flask_login import login_required, current_user
from . import manage
from .forms import PostForm, NodeForm, EditProfileAdminForm
from .. import db
from ..models import Permission, User, Post, Node, Comment, Role
from ..decorators import admin_required, permission_required


@manage.route('/post')
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post():
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('manage/index.html', title=u"你的帖子",
                           items=posts, catagory="post",
                           pagination=pagination, is_all=False)


@manage.route('/all-posts')
@login_required
@admin_required
def all_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('manage/index.html', title=u"全部帖子",
                           items=posts, pagination=pagination,
                           catagory="post", is_all=True)


@manage.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
       not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash(u'你的帖子已经发布')
        return redirect(url_for('manage.post_edit', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('manage/edit_post.html', form=form)


@manage.route('/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
       not current_user.can(Permission.ADMINISTER):
        abort(403)
    post.disabled = True
    print(post.disabled)
    db.session.add(post)
    flash(u'你的帖子已经删除')
    return redirect(url_for('main.index'))


@manage.route('/post/recovery/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_recovery(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
       not current_user.can(Permission.ADMINISTER):
        abort(403)
    post.disabled = False
    db.session.add(post)
    flash(u'你的帖子已经恢复')
    return redirect(url_for('main.index'))


@manage.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FORUM_FOLLOWERS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    for comment in comments:
        print(comment.post_id)
    return render_template('manage/moderate.html', comments=comments,
                           pagination=pagination, page=page)


@manage.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('manage.moderate',
                            page=request.args.get('page', 1, type=int)))


@manage.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('manage.moderate',
                            page=request.args.get('page', 1, type=int)))


@manage.route('/node')
@login_required
@admin_required
def all_node():
    page = request.args.get('page', 1, type=int)
    pagination = Node.query.order_by(Node.timestamp.desc()).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    nodes = pagination.items
    return render_template('manage/index.html', title=u"全部节点",
                           items=nodes, pagination=pagination,
                           catagory="node", is_all=True)


@manage.route('/node/create-new-node', methods=['GET', 'POST'])
@login_required
@admin_required
def new_node():
    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = NodeForm()
    if form.validate_on_submit():
        node = Node(name=form.name.data,
                    intro=form.intro.data,
                    author_id=current_user.id)
        db.session.add(node)
        return redirect(url_for('manage.all_node'))
    return render_template('manage/new_node.html', form=form)


@manage.route('/node/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def node_edit(id):
    node = Node.query.get_or_404(id)
    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = NodeForm()
    if form.validate_on_submit():
        node.name = form.name.data
        node.intro = form.intro.data
        node.author_id = current_user.id
        db.session.add(node)
        flash(u'你的节点已经更新')
        return redirect(url_for('manage.all_node'))
    form.name.data = node.name
    form.intro.data = node.intro
    return render_template('manage/edit_node.html', form=form)


@manage.route('/node/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def node_delete(id):
    node = Node.query.get_or_404(id)
    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    node.disabled = True
    db.session.add(node)
    flash(u'你的节点已经删除')
    return redirect(url_for('manage.all_node'))


@manage.route('/node/recovery/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def node_recovery(id):
    node = Node.query.get_or_404(id)
    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    node.disabled = False
    db.session.add(node)
    flash(u'你的节点已经恢复')
    return redirect(url_for('manage.all_node'))


@manage.route('/user')
@login_required
@admin_required
def all_user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.username).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    user = pagination.items
    return render_template('manage/index.html', title=u"全部用户",
                           items=user, pagination=pagination,
                           catagory="user", is_all=True)


@manage.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'资料已经更新')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('manage/edit_profile.html', form=form, user=user)


@manage.route('/user/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_delete(id):
    user = User.query.get_or_404(id)
    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    user.disabled = True
    db.session.add(user)
    flash(u'用户已经删除')
    return redirect(url_for('manage.all_user'))


@manage.route('/user/recovery/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_recovery(id):
    user = User.query.get_or_404(id)
    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    user.disabled = False
    db.session.add(user)
    flash(u'用户已经恢复')
    return redirect(url_for('manage.all_user'))
