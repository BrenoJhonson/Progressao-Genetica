# Simulação de Robô com Programação Genética

Este projeto implementa uma simulação de um robô autônomo que utiliza programação genética para aprender a navegar em um ambiente, coletar recursos e atingir uma meta final.

## Características

- Simulação de ambiente 2D com obstáculos, recursos e meta
- Robô autônomo com sensores e sistema de movimento
- Algoritmo genético para evolução do comportamento do robô
- Visualização em tempo real da simulação
- Sistema de avaliação de fitness baseado em múltiplos critérios

## Requisitos

- Python 3.x
- NumPy
- Matplotlib
- Pandas

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
```

2. Instale as dependências:
```bash
pip install numpy matplotlib pandas
```

## Estrutura do Projeto

- `robo_exercicio.py`: Arquivo principal contendo toda a implementação
- `melhor_robo.json`: Arquivo que armazena o melhor indivíduo encontrado
- `log.txt`: Arquivo de log com histórico de evolução
- `grafico_fitness.png`: Gráfico da evolução do fitness

## Componentes Principais

### Ambiente
- Geração aleatória de obstáculos e recursos
- Sistema de colisão
- Verificação de coleta de recursos
- Verificação de meta atingida

### Robô
- Sistema de sensores (distância, ângulos, energia)
- Movimento com aceleração e rotação
- Sistema de energia
- Detecção e resposta a colisões

### Programação Genética
- População de 30 indivíduos
- Profundidade de árvore de 2
- 50 gerações de evolução
- Sistema de fitness baseado em:
  - Recursos coletados
  - Meta atingida
  - Energia restante
  - Colisões
  - Distância percorrida

## Como Executar

1. Execute o arquivo principal:
```bash
python robo_exercicio.py
```

2. A simulação será exibida em uma janela separada
3. O robô começará a evoluir através das gerações
4. O melhor indivíduo será salvo em `melhor_robo.json`

## Parâmetros Configuráveis

- Tamanho do ambiente
- Número de obstáculos
- Número de recursos
- Tamanho da população
- Número de gerações
- Profundidade das árvores de decisão

## Visualização

A simulação inclui:
- Obstáculos (retângulos vermelhos)
- Recursos (círculos verdes)
- Meta (círculo amarelo)
- Robô (círculo azul)
- Informações em tempo real:
  - Tempo
  - Recursos coletados
  - Energia
  - Colisões
  - Distância percorrida
  - Status da meta

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
