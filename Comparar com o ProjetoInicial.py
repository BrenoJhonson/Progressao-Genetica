import difflib

def analisar_diferencas(caminho_arquivo1, caminho_arquivo2):
    with open(caminho_arquivo1, 'r', encoding='utf-8') as f1:
        codigo1 = f1.readlines()
    with open(caminho_arquivo2, 'r', encoding='utf-8') as f2:
        codigo2 = f2.readlines()

    d = difflib.Differ()
    diferencas = list(d.compare(codigo1, codigo2))

    print("Diferenças entre os arquivos:\n")
    for linha in diferencas:
        if linha.startswith("- "):
            print(f"\033[91mRemovido: {linha[2:]}\033[0m", end='')  # vermelho
        elif linha.startswith("+ "):
            print(f"\033[92mAdicionado: {linha[2:]}\033[0m", end='')  # verde
        elif linha.startswith("? "):
            continue  # linhas de ajuda do diff (pontuações, etc.)
        else:
            print(f"Igual: {linha[2:]}", end='')

# Exemplo de uso
analisar_diferencas("ProjetoInicial.py", "robo_exercicio.py")
