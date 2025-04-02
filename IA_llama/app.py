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
finalizar_historia = False
total_capitulos = 0
acabou = 0

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

print(documentos)

if not documentos:
    raise ValueError("Nenhum documento foi criado. Verifique a estrutura do arquivo.")

# 🔹 Criar o banco de vetores FAISS
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstoreUniverse = FAISS.from_documents(docUni, embedding_model)

vectorstore = FAISS.from_documents(documentos, embedding_model)

retrieverUni = vectorstoreUniverse.as_retriever(search_type="similarity", search_kwargs={"k": 3})

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})

# 🔹 Histórico da conversa
historico_conversa = []

# 🔹 Template de prompt
rag_template = """
Eu sou o jogador e Você a IA é um mestre de RPG de mesa em uma aventura, continue a aventura se beseando no contexto: {context} e no historico {historico}"

Siga as regras para responder me responder:
- Continue a história a partir do histórico e da pergunta ou ação atual.
- Responda com uma pergunta no final como "Qual sua proxima ação?"
- Não coloque falas para o mim
- Não coloque falas para o mestre
- Sem opções pré-definidas
- Deixe eu escolher as ações que vou tomar
- Faça respostas curtas e seje direto

Com base nas minhas escolhas e no histórico da narrativa, continue a aventura mantendo a coerência com os eventos anteriores e o tom da história.  
Sempre responda considerando as consequências das ações.

Pergunta ou ação atual: {questao}
"""

prompt = ChatPromptTemplate.from_template(rag_template)

rag_templateFinal = """
Eu sou o jogador e Você a IA é um mestre de RPG de mesa em uma aventura, continue a aventura se beseando no contexto: {context} e no historico {historico}"

Siga as regras para responder me responder:
- Finalize a história a partir do histórico
- Responda com uma pergunta no final como "Qual sua proxima ação?"
- Não coloque falas para o mim
- Não coloque falas para o mestre
- Sem opções pré-definidas
- Deixe eu escolher as ações que vou tomar
- Faça respostas curtas e seje direto

Com base nas minhas escolhas e no histórico da narrativa, finalize a história.
"""

promptFinal = ChatPromptTemplate.from_template(rag_templateFinal)

# 🔹 Função para avançar na história
def avancar_historia(): 
    global progresso_historia
    global finalizar_historia
    
    print(total_capitulos)
    print(progresso_historia['capitulo_atual'])

    if progresso_historia['total_perguntas'] < 2:
        progresso_historia['total_perguntas']+=1
        return
    
    
    if finalizar_historia:
        return
    
    progresso_historia['total_perguntas'] = 0

    progresso_historia['parte_atual'] += 1

    if progresso_historia['parte_atual'] > documentos[progresso_historia['id_historia']].metadata['total_partes']:
        progresso_historia['capitulo_atual'] += 1
        progresso_historia['parte_atual'] = 1

    if progresso_historia['capitulo_atual'] > total_capitulos:
        finalizar_historia = True
        print("História concluída!")
        return
    
    
    progresso_historia['id_historia'] += 1


# 🔹 Função para perguntar à IA
def perguntar(questao):
    global progresso_historia
    global finalizar_historia
    global acabou

    print(progresso_historia)


    try:
        capitulo_atualSTR = documentos[progresso_historia['id_historia']].metadata['titulo_capitulo']
        parte_atualSTR = documentos[progresso_historia['id_historia']].metadata['titulo_parte']
        

        contexto = retriever.get_relevant_documents(questao)
        ##contexto_texto = "\n".join([doc.page_content for doc in contexto])
        contexto_texto = documentos[progresso_historia['id_historia']].page_content

        ultimas_interacoes = "\n".join(historico_conversa[-20:])

        if finalizar_historia:
            acabou+=1
            mensagem = promptFinal.format(
            context="Finalize a historia por completo de acordo com as Últimas ações do jogador",
            historico=ultimas_interacoes)

        else:

            ##mensagem = prompt.format(
            ##context=contexto_texto,
            ##historico=ultimas_interacoes,
            ##questao=questao,
            ##capitulo_atualtxt=capitulo_atualSTR,
            ##parte_atualtxt=parte_atualSTR)

            mensagem = prompt.format(
            context=contexto_texto,
            historico=ultimas_interacoes,
            questao=questao)
        

        if acabou >= 2:
            return
        

        print(contexto_texto)
        resposta = client.chat(model=model, messages=[{"role": "user", "content": mensagem}])

        avancar_historia()
        
        return resposta['message']['content']
    except IndexError as e:
        print(f"Erro: {e}")
        return "Erro ao acessar a história. Reiniciando..."

# 🔹 Salvar histórico
def salvar_historico():
 caminho_historico = "Historico_conversa.txt"
 with open(caminho_historico, "w", encoding="utf-8") as arquivo:
    for linha in historico_conversa:
        arquivo.write(linha + "\n")

print("Começando Aventura:\n")
while True:
    perguntando = input("Você: ")
    if perguntando.lower() == "sair":
        break

    resposta = perguntar(perguntando)
    historico_conversa.append(f"Eu: {perguntando}")
    historico_conversa.append(f"IA: {resposta}")
    salvar_historico()
    print(f"{model}: {resposta}")

print("Desligando")