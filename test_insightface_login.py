import requests
import json
import os

# Configurações
BASE_URL = "http://localhost:8000"
EMAIL = "teste@gmail.com"
SENHA = "12345678"
FOTO_CADASTRO = "JHONY1.jpeg"  # Foto para cadastrar a face
FOTO_LOGIN = "MUCA1.jpeg"     # Foto para testar o login facial

def test_insightface_login():
    print("=== Teste de Login Facial com InsightFace ===")
    
    # 1. Login tradicional para obter token
    print("\n1. Fazendo login tradicional...")
    login_data = {"email": EMAIL, "senha": SENHA}
    response = requests.post(f"{BASE_URL}/login/entrar", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Erro no login: {response.text}")
        return
    
    token = response.json()["token"]
    print(f"✅ Login realizado. Token obtido.")
    print(f"Token: {token[:50]}...")
    
    # 2. Cadastrar face
    print(f"\n2. Cadastrando face com {FOTO_CADASTRO}...")
    if not os.path.exists(FOTO_CADASTRO):
        print(f"❌ Arquivo {FOTO_CADASTRO} não encontrado!")
        print("Por favor, coloque a foto no mesmo diretório.")
        return

    with open(FOTO_CADASTRO, "rb") as f:
        files = {"file": f}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/face/register", files=files, headers=headers)

    if response.status_code != 200:
        print(f"❌ Erro ao cadastrar face: {response.text}")
        return

    print("✅ Face cadastrada com sucesso!")
    
    # 3. Testar login facial
    print(f"\n3. Testando login facial com {FOTO_LOGIN}...")
    if not os.path.exists(FOTO_LOGIN):
        print(f"❌ Arquivo {FOTO_LOGIN} não encontrado!")
        print("Por favor, coloque a foto no mesmo diretório.")
        return
    
    with open(FOTO_LOGIN, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/face/login", files=files)
    
    if response.status_code == 200:
        face_token = response.json()["token"]
        print("✅ Login facial realizado com sucesso!")
        print(f"Token obtido: {face_token[:50]}...")
    else:
        print(f"❌ Erro no login facial: {response.text}")
    
    print("\n=== Teste concluído ===")

def test_only_login():
    """Teste apenas do login facial (sem cadastrar)"""
    print("=== Teste Apenas Login Facial ===")
    
    print(f"Testando login facial com {FOTO_LOGIN}...")
    if not os.path.exists(FOTO_LOGIN):
        print(f"❌ Arquivo {FOTO_LOGIN} não encontrado!")
        return
    
    with open(FOTO_LOGIN, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/face/login", files=files)
    
    if response.status_code == 200:
        face_token = response.json()["token"]
        print("✅ Login facial realizado com sucesso!")
        print(f"Token obtido: {face_token}")
    else:
        print(f"❌ Erro no login facial: {response.text}")
    
    print("=== Teste concluído ===")

if __name__ == "__main__":
    # Escolha qual teste executar
    print("Escolha o teste:")
    print("1. Teste completo (cadastro + login)")
    print("2. Teste apenas login (se já tem face cadastrada)")
    
    choice = input("Digite 1 ou 2: ").strip()
    
    if choice == "1":
        test_insightface_login()
    elif choice == "2":
        test_only_login()
    else:
        print("Opção inválida!") 