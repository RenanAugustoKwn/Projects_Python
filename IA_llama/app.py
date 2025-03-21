from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from ollama import Client
from langchain.schema import Document
import re

# 🔹 Carregar variáveis de ambiente
load_dotenv()

# 🔹 Configurar o cliente Ollama
client = Client(host="http://localhost:11434")
model = "llama3.2"


def extrair_metadados(texto):
    padrao = re.compile(r"(Capítulo \d+): (.*?)\n(Parte \d+): (.*?)\n(.*?)(?=(\nCapítulo \d+:|\Z))", re.DOTALL)
    
    capitulos = {}
    for correspondencia in padrao.finditer(texto):
        capitulo = correspondencia.group(1)
        parte = correspondencia.group(3)
        texto_parte = correspondencia.group(5).strip()
        
        if capitulo not in capitulos:
            capitulos[capitulo] = []
        
        capitulos[capitulo].append({"Parte": parte, "Texto": texto_parte})
    
    return capitulos

def processar_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()
    return extrair_metadados(texto)

def criar_documentos(caminho_arquivo):
    capitulos = processar_arquivo(caminho_arquivo)
    documentos = []
    
    for capitulo, partes in capitulos.items():
        texto_completo = "\n".join([f"{parte['Parte']}: {parte['Texto']}" for parte in partes])
        documentos.append(Document(page_content=texto_completo, metadata={"Capítulo": capitulo}))
    
    return documentos

# Exemplo de uso
caminho_arquivo = "historia.txt"  # Substitua pelo caminho do seu arquivo
documentos = criar_documentos(caminho_arquivo)

# 🔹 Criar o banco de vetores FAISS com metadados
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(documentos, embedding_model)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# 🔹 Histórico da conversa
historico_conversa = []

# 🔹 Template para manter contexto
rag_template = """
Você é um mestre de RPG de mesa tipo D&D conduzindo uma aventura,
Continue a história sem sair do contexto original,
Responda apenas com uma única frase sem oferecer opções,
Em alguns momentos voce pode fazer alguns paragrafos para ficar mais dinamico e criativo,
Siga a narrativa, evite respostas longas e mantenha a continuidade lógica dos eventos,
Nunca saia do contexto da história,
Sempre termine a frase perguntando algo para o jogador,
Responda apenas com uma única frase sem oferecer opções sem que posivel,
Deixe o jogador poder fazer as atividades que qerer dentro desse universo, mesmo que nao for a historia principal, seje criativa,
Responda com uma pergunta no final referente a proxima Ação do jogador.

Capitulo Atual: {capitulo_atualtxt}

Parte Atual: {parte_atualtxt}

Contexto da história: {context}

Últimas ações do jogador: {historico}

Ação do jogador agora: {questao}
"""

prompt = ChatPromptTemplate.from_template(rag_template)

progresso_historia = {'capitulo_atual': 0, 'parte_atual': 0}

# Função para avançar na história
def avancar_historia(): 
    global progresso_historia

    # Verifica se o capítulo atual é válido
    if progresso_historia['capitulo_atual'] >= len(documentos):
        print("História concluída!")
        return  # Retorna se a história estiver concluída

    # Verifica se a parte atual é válida para o capítulo atual
    if progresso_historia['parte_atual'] >= len(documentos[progresso_historia['capitulo_atual']]['partes']):
        # Se não for válida, reinicia a parte e avança para o próximo capítulo
        progresso_historia['capitulo_atual'] += 1
        progresso_historia['parte_atual'] = 0
        if progresso_historia['capitulo_atual'] >= len(documentos):
            print("História concluída!")
            return  # Retorna se a história estiver concluídates

# Função para perguntar à IA
def perguntar(questao):
    global progresso_historia

    try:
        # Verifica se o índice do capítulo atual é válido
        capitulo_atual = progresso_historia['capitulo_atual']
        if capitulo_atual >= len(documentos):
            raise IndexError("Capítulo atual fora do limite")

        # Verifica se o índice da parte atual é válido para o capítulo atual
        parte_atual = progresso_historia['parte_atual']
        if parte_atual >= len(documentos[capitulo_atual]['partes']):
            raise IndexError("Parte atual fora do limite")

        # Acessa a parte atual do capítulo
        parte_atual = documentos[capitulo_atual]['partes'][parte_atual]

        # Recupera o contexto para a pergunta
        contexto = retriever.get_relevant_documents(questao)
        contexto_texto = "\n".join([doc.page_content for doc in contexto])

        # Histórico de interações anteriores
        ultimas_interacoes = "\n".join(historico_conversa[-8:])

        # Prepara a mensagem para a IA
        mensagem = prompt.format(context=contexto_texto, historico=ultimas_interacoes, questao=questao, capitulo_atualtxt=capitulo_atual, parte_atualtxt=parte_atual)

        # Chama a IA para obter a resposta
        resposta = client.chat(model=model, messages=[{"role": "user", "content": mensagem}])

        # Avança na história após a interação
        avancar_historia()

        return resposta['message']['content']
    
    except IndexError as e:
        print(f"Erro ao acessar a parte da história: {e}")
        # Garantir que a parte da história é válida e reiniciar se necessário
        progresso_historia['capitulo_atual'] = 0
        progresso_historia['parte_atual'] = 0
        return "Erro ao acessar a história. Reiniciando..."

print("Ativando assistente")
print()

while True:
    perguntando = input("Você: ")
    if perguntando.lower() == "sair":
        break

    resposta = perguntar(perguntando)

    # 🔹 Salvar a interação no histórico
    historico_conversa.append(f"Jogador: {perguntando}")
    historico_conversa.append(f"Mestre: {resposta}")

    print(f"{model}: {resposta}")

# 🔹 Salvar histórico em um arquivo para consultas futuras
caminho_historico = "historico_conversa.txt"
with open(caminho_historico, "w", encoding="utf-8") as arquivo:
    for linha in historico_conversa:
        arquivo.write(linha + "\n")

print("Histórico salvo em:", caminho_historico)
print("Desligando")
