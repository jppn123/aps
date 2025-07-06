from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import select
from connection import SessionDep
from model.face_data import FaceData
from model.usuario import Usuario
from model.login import Login
from services.token import valida_token, cria_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from io import BytesIO
import json
import numpy as np
from PIL import Image
import os
import traceback
import cv2

router = APIRouter(
    prefix="/face",
    tags=["Face"]
)

security = HTTPBearer()

# Configurações do InsightFace
THRESHOLD = 0.5  # Threshold para reconhecimento (0.5 = mais preciso que DeepFace)

# Variável global para o modelo InsightFace
face_analyzer = None

def get_face_analyzer():
    """Inicializa o modelo InsightFace uma única vez"""
    global face_analyzer
    if face_analyzer is None:
        try:
            import insightface
            from insightface.app import FaceAnalysis
            
            # Inicializar o modelo InsightFace
            face_analyzer = FaceAnalysis(name='buffalo_l')
            face_analyzer.prepare(ctx_id=0, det_size=(640, 640))
            print("✅ Modelo InsightFace carregado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao carregar InsightFace: {str(e)}")
            return None
    return face_analyzer

def save_image_from_bytes(image_bytes: bytes, filename: str = "temp.jpg"):
    """Salva bytes da imagem em arquivo temporário"""
    try:
        with open(filename, "wb") as f:
            f.write(image_bytes)
        return filename
    except Exception as e:
        print(f"Erro ao salvar imagem: {str(e)}")
        return None

def get_face_embedding(image_path: str):
    """Extrai embedding da face usando InsightFace"""
    try:
        analyzer = get_face_analyzer()
        if analyzer is None:
            return None
        
        # Carregar imagem com OpenCV
        img = cv2.imread(image_path)
        if img is None:
            print(f"Erro ao carregar imagem: {image_path}")
            return None
        
        # Converter BGR para RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detectar faces
        faces = analyzer.get(img_rgb)
        
        if len(faces) == 0:
            print("Nenhuma face detectada na imagem")
            return None
        
        # Pegar a primeira face detectada
        face = faces[0]
        
        # Extrair embedding (vetor de 512 dimensões)
        embedding = face.embedding.tolist()
        
        print(f"✅ Face detectada e embedding extraído: {len(embedding)} dimensões")
        return embedding
        
    except Exception as e:
        print(f"Erro ao extrair embedding: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def compare_faces(embedding1, embedding2):
    """Compara dois embeddings usando métrica de cosseno"""
    try:
        # Converter para numpy arrays
        emb1 = np.array(embedding1, dtype=float)
        emb2 = np.array(embedding2, dtype=float)
        
        print(f"  Dimensões: emb1={emb1.shape}, emb2={emb2.shape}")
        
        # Calcular similaridade de cosseno
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # Converter para distância (1 - similaridade)
        distance = float(1 - similarity)
        
        print(f"  Distância calculada: {distance:.4f} (threshold: {THRESHOLD})")
        return distance <= THRESHOLD
    except Exception as e:
        print(f"  Erro ao comparar faces: {str(e)}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

@router.post("/register")
def register_face(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: SessionDep,
    file: UploadFile = File(...)
):
    try:
        print(f"=== CADASTRO DE FACE (InsightFace) ===")
        print(f"Arquivo recebido: {file.filename}, content_type: {file.content_type}")
        
        token_data = valida_token(credentials.credentials)
        user_id = token_data.get("id_usu")
        if not user_id:
            raise HTTPException(403, "Token não contém id de usuário")

        usuario = session.exec(select(Usuario).where(Usuario.id == user_id)).first()
        if not usuario:
            raise HTTPException(404, "Usuário não encontrado")

        image_bytes = file.file.read()
        if len(image_bytes) == 0:
            raise HTTPException(400, "Arquivo vazio")
        
        print(f"Cadastrando face para usuário {usuario.nome}: {len(image_bytes)} bytes")
        
        # Salvar imagem temporariamente
        temp_image_path = save_image_from_bytes(image_bytes, f"temp_register_{user_id}.jpg")
        if not temp_image_path:
            raise HTTPException(400, "Erro ao salvar imagem temporária")
        
        try:
            # Extrair embedding da face
            embedding = get_face_embedding(temp_image_path)
            if not embedding:
                raise HTTPException(400, "Nenhum rosto detectado na imagem enviada")
            
            print(f"✅ Embedding extraído com sucesso: {len(embedding)} dimensões")
            
            # Verifica se já existe face cadastrada
            face_data = session.exec(select(FaceData).where(FaceData.usuario_id == user_id)).first()
            if face_data:
                face_data.imagem = image_bytes
                face_data.embedding = json.dumps(embedding)
                print(f"✅ Face atualizada para usuário {usuario.nome}")
            else:
                face_data = FaceData(
                    usuario_id=user_id, 
                    imagem=image_bytes,
                    embedding=json.dumps(embedding)
                )
                session.add(face_data)
                print(f"✅ Face cadastrada para usuário {usuario.nome}")
            
            session.commit()
            return {"msg": "Face cadastrada com sucesso"}
            
        except Exception as e:
            print(f"❌ Erro ao processar imagem: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(400, f"Erro ao processar imagem: {str(e)}")
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro inesperado no cadastro: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, "Erro interno do servidor")

@router.post("/login")
def login_face(
    session: SessionDep,
    file: UploadFile = File(...)
):
    try:
        print(f"=== LOGIN FACIAL (InsightFace) ===")
        print(f"Arquivo recebido: {file.filename}, content_type: {file.content_type}")
        
        image_bytes = file.file.read()
        if len(image_bytes) == 0:
            raise HTTPException(400, "Arquivo vazio")
        
        print(f"Recebida imagem: {len(image_bytes)} bytes")
        
        # Buscar todos os usuários com face cadastrada
        faces = session.exec(select(FaceData)).all()
        print(f"Faces cadastradas encontradas: {len(faces)}")
        
        if not faces:
            raise HTTPException(404, "Nenhuma face cadastrada")

        # Salvar imagem temporariamente
        temp_image_path = save_image_from_bytes(image_bytes, "temp_login.jpg")
        if not temp_image_path:
            raise HTTPException(400, "Erro ao salvar imagem temporária")
        
        try:
            # Extrair embedding da face recebida
            unknown_embedding = get_face_embedding(temp_image_path)
            if not unknown_embedding:
                raise HTTPException(400, "Nenhum rosto detectado na imagem enviada")
            
            print(f"✅ Embedding da face recebida extraído: {len(unknown_embedding)} dimensões")
            print(f"Comparando com {len(faces)} faces cadastradas...")
            
            for i, face in enumerate(faces):
                try:
                    print(f"Processando face {i+1}/{len(faces)} (ID: {face.id})")
                    
                    if not face.embedding:
                        print(f"  ❌ Face {face.id}: Sem embedding cadastrado")
                        continue
                    
                    # Carregar embedding cadastrado
                    known_embedding = json.loads(face.embedding)
                    print(f"  Tipo do embedding cadastrado: {type(known_embedding)}")
                    
                    # Comparar faces
                    match = compare_faces(known_embedding, unknown_embedding)
                    
                    print(f"  {'✅' if match else '❌'} Face {face.id}: {'Corresponde' if match else 'Não corresponde'}")
                    
                    if match:
                        usuario = session.exec(select(Usuario).where(Usuario.id == face.usuario_id)).first()
                        if not usuario:
                            print(f"  ❌ Usuário não encontrado para face {face.id}")
                            continue
                        
                        # Buscar o login do usuário para obter o tipo
                        login = session.exec(select(Login).where(Login.id == usuario.id_login)).first()
                        if not login:
                            print(f"  ❌ Login não encontrado para usuário {usuario.id}")
                            continue
                        
                        print(f"  ✅ Face reconhecida para usuário: {usuario.nome}")
                        # Gera token igual ao login tradicional, incluindo o tipo de login
                        token = cria_token(usuario.id, params={"tp_login": login.tipo})
                        return {"token": token}
                        
                except Exception as e:
                    print(f"  ❌ Erro ao processar face {face.id}: {str(e)}")
                    print(f"  Traceback: {traceback.format_exc()}")
                    continue
                    
            print("❌ Nenhuma face foi reconhecida")
            raise HTTPException(401, "Face não reconhecida")
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Erro ao processar imagem: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(400, f"Erro ao processar imagem: {str(e)}")
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro inesperado no login: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, "Erro interno do servidor") 