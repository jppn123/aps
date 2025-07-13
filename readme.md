# criar o ambiente virtual #

```py
python -m venv venv
```

# instalar usando o pip #
```py
pip install --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org -r .\requirements.txt
```

# gerar senha do email

https://myaccount.google.com/u/3/apppasswords

# rodar para poder funcionar no celular fisico

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

precisou instalar o cmake vindo de cmake.org
