from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import select
from connection import SessionDep
from model.face import Face
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
import gc

router = APIRouter(
    prefix="/face",
    tags=["Face"]
)

security = HTTPBearer()

# Configurações do InsightFace - mais leves para Railway
THRESHOLD = 0.6  # Threshold mais permissivo (0.6 = menos preciso, mas mais rápido)

# Variável global para o modelo InsightFace
face_analyzer = None

def get_face_analyzer():
    """Inicializa o modelo InsightFace sob demanda com configurações leves"""
    global face_analyzer
    if face_analyzer is None:
        try:
            import insightface
            from insightface.app import FaceAnalysis
            
            # Configurações ultra-leves para Railway
            face_analyzer = FaceAnalysis(name='buffalo_s')  # Modelo menor
            face_analyzer.prepare(ctx_id=-1, det_size=(160, 160))  # Resolução menor
            print("✅ Modelo InsightFace carregado com configurações leves")
        except Exception as e:
            print(f"❌ Erro ao carregar InsightFace: {str(e)}")
            return None
    return face_analyzer

def cleanup_memory():
    """Força limpeza de memória"""
    gc.collect()
    if face_analyzer is not None:
        try:
            # Limpar cache do modelo
            if hasattr(face_analyzer, 'clear_cache'):
                face_analyzer.clear_cache()
        except:
            pass

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
    """Extrai embedding da face usando InsightFace otimizado"""
    try:
        analyzer = get_face_analyzer()
        if analyzer is None:
            return None
        
        # Carregar imagem com OpenCV
        img = cv2.imread(image_path)
        if img is None:
            print(f"Erro ao carregar imagem: {image_path}")
            return None
        
        # Redimensionar imagem para economizar memória
        height, width = img.shape[:2]
        if width > 640 or height > 640:
            scale = min(640/width, 640/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
        
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
    finally:
        # Limpar memória após processamento
        cleanup_memory()

def compare_faces(embedding1, embedding2):
    """Compara dois embeddings usando métrica de cosseno otimizada"""
    try:
        # Converter para numpy arrays
        emb1 = np.array(embedding1, dtype=np.float32)  # float32 em vez de float64
        emb2 = np.array(embedding2, dtype=np.float32)
        
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
    finally:
        # Limpar memória após comparação
        cleanup_memory()

@router.post("/register")
def register_face(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: SessionDep,
    file: UploadFile = File(...)
):
    try:
        print(f"=== CADASTRO DE FACE (InsightFace Otimizado) ===")
        print(f"Arquivo recebido: {file.filename}, content_type: {file.content_type}")
        
        # Verificar se o modelo está disponível
        analyzer = get_face_analyzer()
        if analyzer is None:
            raise HTTPException(503, "Serviço de reconhecimento facial temporariamente indisponível")
        
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
        
        # Verificar tamanho da imagem (limitar a 5MB)
        if len(image_bytes) > 5 * 1024 * 1024:
            raise HTTPException(400, "Imagem muito grande. Máximo 5MB.")
        
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
            face_data = session.exec(select(Face).where(Face.usuario_id == user_id)).first()
            if face_data:
                face_data.imagem = image_bytes
                face_data.embedding = json.dumps(embedding)
                print(f"✅ Face atualizada para usuário {usuario.nome}")
            else:
                face_data = Face(
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
            # Limpar memória
            cleanup_memory()
                
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
        print(f"=== LOGIN FACIAL (InsightFace Otimizado) ===")
        print(f"Arquivo recebido: {file.filename}, content_type: {file.content_type}")
        
        # Verificar se o modelo está disponível
        analyzer = get_face_analyzer()
        if analyzer is None:
            raise HTTPException(503, "Serviço de reconhecimento facial temporariamente indisponível")
        
        image_bytes = file.file.read()
        if len(image_bytes) == 0:
            raise HTTPException(400, "Arquivo vazio")
        
        # Verificar tamanho da imagem (limitar a 5MB)
        if len(image_bytes) > 5 * 1024 * 1024:
            raise HTTPException(400, "Imagem muito grande. Máximo 5MB.")
        
        print(f"Recebida imagem: {len(image_bytes)} bytes")
        
        # Buscar todos os usuários com face cadastrada
        faces = session.exec(select(Face)).all()
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
            # Limpar memória
            cleanup_memory()
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro inesperado no login: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, "Erro interno do servidor") 