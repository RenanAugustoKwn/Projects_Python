from dotenv import load_dotenv
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
# 🔹 Carregar variáveis de ambiente
load_dotenv()

# 🔹 Verificar se o arquivo da história existe
historia_path = "Historia.txt"
regras_path = "Regras.txt"  # Caminho para o arquivo de regras do D&D
if not os.path.exists(historia_path):
    raise FileNotFoundError(f"Arquivo '{historia_path}' não encontrado!")
if not os.path.exists(regras_path):
    raise FileNotFoundError(f"Arquivo '{regras_path}' não encontrado!")

# 🔹 Carregar a história do arquivo
loader = TextLoader(historia_path)
documents = loader.load()

# 🔹 Carregar as regras do D&D
with open(regras_path, 'r', encoding='utf-8') as file:
    regras_dnd = file.read()

# 🔹 Dividir o texto em partes menores
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# 🔹 Criar embeddings usando Hugging Face
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 🔹 Criar um banco de dados vetorial com ChromaDB

# 🔹 Verificar se o modelo LLaMA existe antes de carregar
llama_model_path = "Llama-3.2-3B-Instruct-f16.gguf"
if not os.path.exists(llama_model_path):
    raise FileNotFoundError(f"Modelo '{llama_model_path}' não encontrado!")

# 🔹 Carregar o modelo LLaMA
llm = LlamaCpp(
    model_path=llama_model_path,
    temperature=0.3,    # Reduz a criatividade para respostas mais consistentes
    top_p=0.9,          # Mantém a diversidade das respostas sem torná-las aleatórias
    top_k=40,           # Filtra as melhores palavras possíveis
    n_ctx=4096,         # Define o tamanho do contexto (quanto maior, mais coerente a conversa)
    max_tokens=100,     # Limita o tamanho da resposta para evitar desvios
    repetition_penalty=1.2,  # Penaliza repetições para evitar redundâncias
    verbose=True
)

# 🔹 Criar a cadeia de perguntas e respostas

# Histórico de escolhas
historico_de_jogo = []

def mestre_dnd(pergunta):

    #historia_contexto = capitulos[parte_atual]
    # Garantir que a IA saiba que é um jogo de D&D e siga as regras
    prompt_completo = f"""
    Traduzir sua resposta para portugues e responda em portugues,
    responda a  pergunta com o maximo de 20 palavras,
    Pergunta: {pergunta}
    """
    resposta = llm.invoke(prompt_completo)

    historico_de_jogo.append(f"Jogador perguntou: {pergunta}")
    historico_de_jogo.append(f"Mestre respondeu: {resposta}")

    #if isinstance(resposta, dict):
        #return resposta.get("result", "")  # Retorna apenas o valor da chave 'result'
    #else:
    return str(resposta)  # Caso não seja um dicionário, retornamos o valor diretamente.



# 🔹 Loop interativo para perguntas
while True:
    pergunta = input("Faça sua pergunta para o mestre (ou 'sair' para encerrar): ")
    
    if pergunta.lower() == 'sair':
        print("Até logo, aventureiro!")
        break

    resposta = mestre_dnd(pergunta)
    print(f"Resposta do mestre: {resposta}\n")