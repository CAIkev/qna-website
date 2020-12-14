from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from ..forms import QuestionForm, AnswerForm
from ..models import User, Question, Answer
from ..utils import current_time

questions = Blueprint("questions", __name__)

""" ************ View functions ************ """

@questions.route("/", methods=["GET", "POST"])
def index():
    form = QuestionForm()

    if form.validate_on_submit():
        new_id = str(Question.objects().count())
        question = Question(
            user=current_user._get_current_object(),
            content=form.ask.data,
            date=current_time(),
            q_id =new_id,
        )
        question.save()
        return redirect(url_for("questions.question", id=new_id))

    return render_template("index.html", form=form, questions=Question.objects().order_by('-q_id'))


@questions.route("/questions/<id>", methods=["GET", "POST"])
def question(id):
    try:
        result = Question.objects(q_id=id).first()
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("questions.index"))

    form = AnswerForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        answer = Answer(
            user=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            q_id = id,
        )
        answer.save()

        return redirect(request.path)
    
    answers = Answer.objects(q_id=id).order_by('-date')

    return render_template(
        "question.html", form=form, question=result, answers=answers
    )

@questions.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    user_questions = Question.objects(user=user).order_by('-date')
    questions = Question.objects()
    answers = Answer.objects(user=user).order_by('-date')

    return render_template("user_detail.html", username=username, 
                            user_questions=user_questions, 
                            questions=questions, answers=answers)
