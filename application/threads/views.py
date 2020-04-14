from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from application import app, db
from application.posts.models import Post
from application.auth.models import User
from application.threads.models import Thread

from application.threads.forms import ThreadForm

# lomake uudelle langalle
@app.route("/posts/threads/new/")
@login_required
def threads_form():
  return render_template("threads/new_thread.html", form = ThreadForm())

# uuden langan tallennus
@app.route("/posts/threads/", methods=["POST"])
@login_required
def threads_create():
  form = ThreadForm(request.form)

  if not form.validate():
    return render_template("thread/new.html", form = form)

  # luodaan uusi lanka ja luodaan ID tallentamalla
  thread = Thread(form.title.data)
  thread.owner_id = current_user.id
  db.session.add(thread)
  db.session.commit()

  # luodaan uusi postaus
  posted = Post(form.content.data)
  posted.account_id = current_user.id
  posted.thread_id = thread.id
  db.session().add(posted)
  db.session().commit()
  
  flash("New post succesfully saved!")
  return redirect(url_for("posts_index"))

# yksittäisen langan näkymä
@app.route("/posts/threads/<thread_id>", methods=["GET"])
def posts_thread(thread_id):
  thread = Thread.query.get_or_404(thread_id)

  return render_template("threads/thread.html",
    thread = thread,
    user = current_user
  )

# langan poistaminen
@app.route("/posts/threads/delete/<thread_id>", methods=["GET", "POST"])
@login_required
def threads_delete(thread_id):
  thread = Thread.query.get_or_404(thread_id)

  # kirjautuneen oltava langan omistaja
  if thread.owner_id == current_user.id:
    db.session.delete(thread)
    Thread.delete_thread_posts(thread_id)
    db.session.commit()

    flash("Your post and all the comments were deleted")
    return redirect(url_for("posts_index"))
  else:
    flash("You are not authorized")
    return redirect(url_for("posts_index"))