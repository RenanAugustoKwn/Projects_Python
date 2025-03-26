from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from ollama import Client
from langchain.schema import Document
import re

# 🔹 Carregar variáveis de ambiente
load_dotenv()

# 🔹 Configurar o cliente Ollama
client = Client(host="http://localhost:11434")
model = "llama3.2"

progresso_historia = {'id_historia': 0, 'capitulo_atual': 0, 'parte_atual': 1, 'total_perguntas': 0}
total_capitulos = 0

def criar_documentos(caminho_arquivo):
    global total_capitulos

    with open(caminho_arquivo, "r", encoding="utf-8") as file:
        texto = file.read()

    padrao_capitulo = re.compile(r"(Capítulo \d+): (.*?)\n", re.DOTALL)
    padrao_parte = re.compile(r"(Parte \d+): (.*?)\n(.*?)(?=\nParte \d+:|\nCapítulo \d+:|\Z)", re.DOTALL)

    documentos = []
    capitulos = list(padrao_capitulo.finditer(texto))
    total_capitulos = len(capitulos) - 1

    id_historia = -1
    for i, cap in enumerate(capitulos):
        capitulo = cap.group(1)
        titulo_capitulo = cap.group(2)
        
        inicio = cap.end()
        fim = capitulos[i + 1].start() if i + 1 < len(capitulos) else len(texto)
        trecho = texto[inicio:fim]

        partes = list(padrao_parte.finditer(trecho))
        total_partes = len(partes)

        for parte in partes:
            parte_num = int(parte.group(1).split(" ")[1])
            titulo_parte = parte.group(2)
            conteudo = parte.group(3).strip()
            id_historia += 1
            
            documento = Document(
                page_content=conteudo,
                metadata={
                    "id": id_historia,
                    "capitulo": capitulo,
                    "titulo_capitulo": titulo_capitulo,
                    "parte": parte_num,
                    "titulo_parte": titulo_parte,
                    "total_partes": total_partes
                }
            )
            documentos.append(documento)
    
    return documentos

def criar_universo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as file:
        texto = file.read()
    
    # Dividir em partes menores para melhor indexação
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    textos_divididos = text_splitter.split_text(texto)
    
    # Criar objetos do tipo Document
    documentos = [Document(page_content=chunk) for chunk in textos_divididos]
    return documentos

# 🔹 Criar documentos a partir do arquivo
caminho_historia= "Historia.txt"
caminho_universo = "Universo.txt"

documentos = criar_documentos(caminho_historia)
docUni = criar_universo(caminho_universo)

# Exibir os resultados
print(documentos)

if not documentos:
    raise ValueError("Nenhum documento foi criado. Verifique a estrutura do arquivo.")

# 🔹 Criar o banco de vetores FAISS
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstoreUniverse = FAISS.from_documents(docUni, embedding_model)

vectorstore = FAISS.from_documents(documentos, embedding_model)

retriever = vectorstoreUniverse.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# 🔹 Histórico da conversa
historico_conversa = []

# 🔹 Template de prompt
rag_template = """
Você é um mestre de RPG de mesa conduzindo uma aventura,
Continue a história sem sair do Contexto,
Siga a narrativa, evite respostas longas e mantenha a continuidade lógica dos eventos e da "Pergunta ou ação:",
Continue a partir de "Últimas ações:",
Siga o contexto da história,
Deixe o jogador poder fazer as atividades que querer dentro desse universo, mesmo que nao for a história principal, seje criativa,
Responda com uma pergunta no final como "Oque você irá fazer agora?", "Qual sua proxima ação?",
Não coloque falas para o jogador,
Não coloque falas para o mestre,
Não dê alternativas para o jogador,
Não dê opções para o jogador,
Resuma tudo em uma frase sempre que possível.

Capítulo Atual: {capitulo_atualtxt}
Parte Atual: {parte_atualtxt}

Contexto: {context}
Últimas ações do jogador: {historico}
Pergunta ou ação: {questao}
"""

prompt = ChatPromptTemplate.from_template(rag_template)

# 🔹 Função para avançar na história
def avancar_historia(): 
    global progresso_historia
    
    print(total_capitulos)
    print(progresso_historia['capitulo_atual'])

    if progresso_historia['total_perguntas'] < 5:
        progresso_historia['total_perguntas']+=1
        return
    
    progresso_historia['total_perguntas'] = 0

    if progresso_historia['capitulo_atual'] > total_capitulos:
        print("História concluída!")
        return
    
    progresso_historia['parte_atual'] += 1

    if progresso_historia['parte_atual'] > documentos[progresso_historia['id_historia']].metadata['total_partes']:
        progresso_historia['capitulo_atual'] += 1
        progresso_historia['parte_atual'] = 1

    if progresso_historia['capitulo_atual'] > total_capitulos:
        print("História concluída!")
        return
    
    
    progresso_historia['id_historia'] += 1


# 🔹 Função para perguntar à IA
def perguntar(questao):
    global progresso_historia
    print(progresso_historia)

    try:
        capitulo_atualSTR = documentos[progresso_historia['id_historia']].metadata['titulo_capitulo']
        parte_atualSTR = documentos[progresso_historia['id_historia']].metadata['titulo_parte']
        
        contexto = retriever.get_relevant_documents(questao)
        contexto_texto = "\n".join([doc.page_content for doc in contexto])

        ultimas_interacoes = "\n".join(historico_conversa[-5:])

        mensagem = prompt.format(
            context=contexto_texto,
            historico=ultimas_interacoes,
            questao=questao,
            capitulo_atualtxt=capitulo_atualSTR,
            parte_atualtxt=parte_atualSTR
        )
        
        ##print(mensagem)
        resposta = client.chat(model=model, messages=[{"role": "user", "content": mensagem}])

        avancar_historia()
        
        return resposta['message']['content']
    except IndexError as e:
        print(f"Erro: {e}")
        return "Erro ao acessar a história. Reiniciando..."

print("Ativando assistente\n")
while True:
    perguntando = input("Você: ")
    if perguntando.lower() == "sair":
        break
    resposta = perguntar(perguntando)
    historico_conversa.append(f"Jogador: {perguntando}")
    historico_conversa.append(f"Mestre: {resposta}")
    print(f"{model}: {resposta}")

# 🔹 Salvar histórico
caminho_historico = "Historico_conversa.txt"
with open(caminho_historico, "w", encoding="utf-8") as arquivo:
    for linha in historico_conversa:
        arquivo.write(linha + "\n")

print("Histórico salvo em:", caminho_historico)
print("Desligando")