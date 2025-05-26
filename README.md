# Projeto de Programação Genética para Controle de Robôs Autônomos

## 📌 Visão Geral
Este projeto implementa um algoritmo de **Programação Genética** para evoluir o comportamento de um robô autônomo em um ambiente 2D com obstáculos, recursos e uma meta. O robô deve navegar pelo ambiente, coletar recursos e atingir a meta de forma eficiente, enquanto evita colisões e otimiza seu consumo de energia.

---

## 🚀 Funcionalidades
- **Ambiente Dinâmico**: Geração aleatória de obstáculos, recursos e meta em posições seguras.
- **Sistema de Sensores**: O robô utiliza dados como distância até recursos, obstáculos, meta, ângulos relativos e energia para tomar decisões.
- **Árvores de Decisão**: Comportamento controlado por expressões matemáticas evoluídas geneticamente.
- **Algoritmo Genético Aprimorado**:
  - Operadores diversificados (`sin`, `cos`, `if_positivo`, etc.).
  - Sistema de fitness balanceado (recompensas/penalidades ajustadas).
  - Mecanismos anti-estagnação (aumento de mutação e diversidade).
- **Visualização em Tempo Real**: Simulação gráfica do robô e do ambiente usando `matplotlib`.

---

## 📊 Melhorias Implementadas (vs. Código Original)
| **Característica**          | **Versão Original**               | **Versão Aprimorada**                     |
|-----------------------------|-----------------------------------|-------------------------------------------|
| Operadores Genéticos        | Básicos (`+`, `-`, `*`, `/`)     | Ampliados (`sin`, `cos`, `if_positivo`, etc.) |
| Sistema de Fitness          | Penalidades/recompensas fixas     | Balanceado e adaptativo                   |
| Elitismo                   | 1 indivíduo                      | 20% da população                          |
| Controle de Estagnação      | Não implementado                 | Mutação adaptativa e reinicialização parcial |
| Tamanho da População       | 20                               | 100                                       |

---

## 📦 Requisitos
- Python 3.8+
- Bibliotecas:
  ```bash
  numpy
  matplotlib
  ```

## 🛠️ Como Executar
```bash
git clone https://github.com/BrenoJhonson/Progressao-Genetica.git
cd Progressao-Genetica
```

## Execute o algoritmo genético:
```bash
python robo_exercicio.py
```

## 📝 Relatório Detalhado

Consulte o relatório completo em: 
- [Relatório.md](./Relatório.md)
