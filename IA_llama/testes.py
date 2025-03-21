import re

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def extrair_partes(texto):
    padrao_capitulo = re.compile(r"(Capítulo \d+): (.*?)\n", re.DOTALL)
    padrao_parte = re.compile(r"(Parte \d+): (.*?)\n(.*?)(?=\nParte \d+:|\nCapítulo \d+:|\Z)", re.DOTALL)

    documentos = []
    capitulos = list(padrao_capitulo.finditer(texto))
    
    for i, cap in enumerate(capitulos):
        capitulo = cap.group(1)
        titulo_capitulo = cap.group(2)

        # Determina o trecho do texto onde buscar partes
        inicio = cap.end()
        fim = capitulos[i + 1].start() if i + 1 < len(capitulos) else len(texto)
        trecho = texto[inicio:fim]

        for correspondencia in padrao_parte.finditer(trecho):
            parte_num = int(correspondencia.group(1).split(" ")[1])
            titulo_parte = correspondencia.group(2)
            conteudo = correspondencia.group(3).strip()

            # Criar o documento com os metadados e conteúdo
            documento = Document(
                page_content=conteudo,
                metadata={
                    "capitulo": capitulo,
                    "titulo_capitulo": titulo_capitulo,
                    "parte": parte_num,
                    "titulo_parte": titulo_parte
                }
            )

            documentos.append(documento)

    return documentos

# Nome do arquivo
nome_arquivo = 'Historia.txt'

# Ler o texto do arquivo
with open(nome_arquivo, 'r', encoding='utf-8') as file:
    texto = file.read()

documentos = extrair_partes(texto)

# Exibir os resultados
for doc in documentos:
    print(doc.metadata)
