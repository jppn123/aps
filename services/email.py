from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import BackgroundTasks, HTTPException
from dotenv import load_dotenv
from jinja2 import Template
from random import randint
import os

load_dotenv('.env')
class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')

conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    TEMPLATE_FOLDER="./templates"
)

async def send_email_async(subject: str, email_to: str, name: str):
    print("username:"+Envs.MAIL_USERNAME)
    print("senha:"+Envs.MAIL_PASSWORD)
    codigoAutenticacao = randint(100000, 999999)
    
    with open("./templates/email.html", 'r') as f:
        tmp = Template(f.read())

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=tmp.render({"title":"Redefinir sua senha", "name": name, "codigo": codigoAutenticacao}),
        subtype='html',
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='email.html')

    return codigoAutenticacao