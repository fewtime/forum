from flask import render_template, redirect, abort, flash, url_for, \
    request, current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, CommentForm, PostForm
from .. import db
from ..models import User, Role, Permission, Post, Comment, Node
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    nodes = Node.query.order_by(Node.name).all()
    return render_template('index.html', posts=posts, nodes=nodes,
                           nodename=None, top=False, new=False,
                           show_followed=show_followed,
                           pagination=pagination)


@main.route('/newest-list')
def new_posts():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    nodes = Node.query.order_by(Node.name).all()
    return render_template('index.html', posts=posts, nodes=nodes,
                           nodename=None, top=False, new=True,
                           show_followed=show_followed,
                           pagination=pagination)


@main.route('/top-list')
def top_posts():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    pagination = Post.query.order_by(Post.count.desc()).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    nodes = Node.query.order_by(Node.name).all()
    return render_template('index.html', posts=posts, nodes=nodes,
                           nodename=None, top=True, new=False,
                           show_followed=show_followed,
                           pagination=pagination)


@main.route('/node/<nodename>')
def node(nodename):
    page = request.args.get('page', 1, type=int)
    show_followed = False
    node = Node.query.filter_by(name=nodename).first()
    if node is None:
        abort(404)
    pagination = node.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FORUM_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    nodes = Node.query.order_by(Node.name).all()
    return render_template('index.html', posts=posts, nodes=nodes,
                           nodename=nodename, top=False, new=False,
                           show_followed=show_followed,
                           pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'你的资料已经更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    post.count += 1
    db.session.add(post)

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'你的评论已经发布')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               current_app.config['FORUM_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FORUM_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注了该用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'你现在关注了 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户名')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你没有关注了该用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你已经不再关注 %s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FORUM_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u"你的粉丝",
                           endpoint='.followers', pagination=pagination,
                           follows=follows, followed=False)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'非法用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FORUM_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u"关注的人",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows, followed=True)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*(24*60*60))
    return resp


@main.route('/new-post', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
       form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    node=Node.query.get(form.node.data),
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('new_post.html', form=form)
