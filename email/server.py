from flask import Flask, render_template, request, redirect
import smtplib
from enum import Enum, auto
from dataclasses import dataclass
from jinja2 import Template

app = Flask(__name__)


class Action(Enum):
    create = auto()
    delete = auto()
    edit = auto()


@dataclass(frozen=True)
class Event:
    action: Action
    who: str
    ticket_id: str


class EmailSender:
    our_email: str
    password: str
    their_email: str

    @staticmethod
    def notify(our_email: str, their_email: str, event: Event) -> None:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp_server:
            context = Template('User {{who}} {{action}} task number {{ticket_id}}')
            html = context.render(who=event.who, action=event.action.name, ticket_id=event.ticket_id)
            smtp_server.starttls()
            try:
                smtp_server.login(our_email, email_sender.password)
                smtp_server.send(our_email, their_email, html)
            except:
                print("I did not login:", html, our_email, email_sender.password, their_email)
            finally:
                smtp_server.quit()


email_sender = EmailSender()


@app.route('/', methods=['GET'])
def login_get():
    return render_template("login.html")


@app.route('/', methods=['POST'])
def login_post():
    email_sender.our_email = request.form['mail']
    email_sender.password = request.form['password']
    return redirect('/sender')


@app.route('/sender', methods=['GET'])
def sender_get():
    return render_template("send.html")


@app.route('/sender', methods=['POST'])
def sender_post():
    message = emit_event(request.form)
    email_sender.notify(email_sender.our_email, email_sender.their_email, message)
    return redirect('/sender')


def emit_event(form_data):
    who_sending = form_data['who']
    sender_ticket_id = form_data['ticket_id']

    email_sender.their_email = form_data['mail']

    button_value = form_data['button']
    match button_value:
        case "create": action = Action.create
        case "edit": action = Action.edit
        case _: action = Action.delete

    return Event(action=action, who=who_sending, ticket_id=sender_ticket_id)


if __name__ == '__main__':
    app.run(debug=True)
