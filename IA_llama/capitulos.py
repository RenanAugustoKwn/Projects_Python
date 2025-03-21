import re

def extrair_partes(texto):
    # Padrão para capturar partes
    padrao_parte = re.compile(r"Parte \d+: (.*)")

    partes = []

    for linha in texto.splitlines():
        match_parte = padrao_parte.match(linha)
        if match_parte:
            partes.append(match_parte.group(1))

    return partes

def criar_metadados(partes):
    metadados = []
    for i, parte in enumerate(partes):
        metadado = {
            "parte": i + 1,
            "titulo": parte
        }
        metadados.append(metadado)
    return metadados

# Nome do arquivo
nome_arquivo = 'Historia.txt'

# Ler o texto do arquivo
with open(nome_arquivo, 'r', encoding='utf-8') as file:
    texto = file.read()

# Extrair as partes
partes = extrair_partes(texto)

# Criar os metadados
metadados = criar_metadados(partes)

# Exibir os metadados
print(metadados)