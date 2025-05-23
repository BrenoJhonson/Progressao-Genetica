import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import json
import time
import pandas as pd

# =====================================================================
# PARTE 1: ESTRUTURA DA SIMULAÇÃO (NÃO MODIFICAR)
# Esta parte contém a estrutura básica da simulação, incluindo o ambiente,
# o robô e a visualização. Não é recomendado modificar esta parte.
# =====================================================================

class Ambiente:
    def __init__(self, largura=800, altura=600, num_obstaculos=5, num_recursos=5):
        self.largura = largura
        self.altura = altura
        self.obstaculos = self.gerar_obstaculos(num_obstaculos)
        self.recursos = self.gerar_recursos(num_recursos)
        self.tempo = 0
        self.max_tempo = 1000  # Tempo máximo de simulação
        self.meta = self.gerar_meta()  # Adicionando a meta
        self.meta_atingida = False  # Flag para controlar se a meta foi atingida
    
    def gerar_obstaculos(self, num_obstaculos):
        obstaculos = []
        for _ in range(num_obstaculos):
            x = random.randint(50, self.largura - 50)
            y = random.randint(50, self.altura - 50)
            largura = random.randint(20, 100)
            altura = random.randint(20, 100)
            obstaculos.append({
                'x': x,
                'y': y,
                'largura': largura,
                'altura': altura
            })
        return obstaculos
    
    def gerar_recursos(self, num_recursos):
        recursos = []
        for _ in range(num_recursos):
            x = random.randint(20, self.largura - 20)
            y = random.randint(20, self.altura - 20)
            recursos.append({
                'x': x,
                'y': y,
                'coletado': False
            })
        return recursos
    
    def gerar_meta(self):
        # Gerar a meta em uma posição segura, longe dos obstáculos
        max_tentativas = 100
        margem = 50  # Margem das bordas
        
        for _ in range(max_tentativas):
            x = random.randint(margem, self.largura - margem)
            y = random.randint(margem, self.altura - margem)
            
            # Verificar se a posição está longe o suficiente dos obstáculos
            posicao_segura = True
            for obstaculo in self.obstaculos:
                # Calcular a distância até o obstáculo mais próximo
                dist_x = max(obstaculo['x'] - x, 0, x - (obstaculo['x'] + obstaculo['largura']))
                dist_y = max(obstaculo['y'] - y, 0, y - (obstaculo['y'] + obstaculo['altura']))
                dist = np.sqrt(dist_x**2 + dist_y**2)
                
                if dist < 50:  # 50 pixels de margem extra
                    posicao_segura = False
                    break
            
            if posicao_segura:
                return {
                    'x': x,
                    'y': y,
                    'raio': 30  # Raio da meta
                }
        
        # Se não encontrar uma posição segura, retorna o centro
        return {
            'x': self.largura // 2,
            'y': self.altura // 2,
            'raio': 30
        }
    
    def verificar_colisao(self, x, y, raio):
        # Verificar colisão com as bordas
        if x - raio < 0 or x + raio > self.largura or y - raio < 0 or y + raio > self.altura:
            return True
        
        # Verificar colisão com obstáculos
        for obstaculo in self.obstaculos:
            if (x + raio > obstaculo['x'] and 
                x - raio < obstaculo['x'] + obstaculo['largura'] and
                y + raio > obstaculo['y'] and 
                y - raio < obstaculo['y'] + obstaculo['altura']):
                return True
        
        return False
    
    def verificar_coleta_recursos(self, x, y, raio):
        recursos_coletados = 0
        for recurso in self.recursos:
            if not recurso['coletado']:
                distancia = np.sqrt((x - recurso['x'])**2 + (y - recurso['y'])**2)
                if distancia < raio + 10:  # 10 é o raio do recurso
                    recurso['coletado'] = True
                    recursos_coletados += 1
        return recursos_coletados
    
    def verificar_atingir_meta(self, x, y, raio):
        if not self.meta_atingida:
            distancia = np.sqrt((x - self.meta['x'])**2 + (y - self.meta['y'])**2)
            if distancia < raio + self.meta['raio']:
                self.meta_atingida = True
                return True
        return False
    
    def reset(self):
        self.tempo = 0
        for recurso in self.recursos:
            recurso['coletado'] = False
        self.meta_atingida = False
        return self.get_estado()
    
    def get_estado(self):
        return {
            'tempo': self.tempo,
            'recursos_coletados': sum(1 for r in self.recursos if r['coletado']),
            'recursos_restantes': sum(1 for r in self.recursos if not r['coletado']),
            'meta_atingida': self.meta_atingida
        }
    
    def passo(self):
        self.tempo += 1
        return self.tempo >= self.max_tempo
    
    def posicao_segura(self, raio_robo=15):
        """Encontra uma posição segura para o robô, longe dos obstáculos"""
        max_tentativas = 100
        margem = 50  # Margem das bordas
        
        for _ in range(max_tentativas):
            x = random.randint(margem, self.largura - margem)
            y = random.randint(margem, self.altura - margem)
            
            # Verificar se a posição está longe o suficiente dos obstáculos
            posicao_segura = True
            for obstaculo in self.obstaculos:
                # Calcular a distância até o obstáculo mais próximo
                dist_x = max(obstaculo['x'] - x, 0, x - (obstaculo['x'] + obstaculo['largura']))
                dist_y = max(obstaculo['y'] - y, 0, y - (obstaculo['y'] + obstaculo['altura']))
                dist = np.sqrt(dist_x**2 + dist_y**2)
                
                if dist < raio_robo + 20:  # 20 pixels de margem extra
                    posicao_segura = False
                    break
            
            if posicao_segura:
                return x, y
        
        # Se não encontrar uma posição segura, retorna o centro
        return self.largura // 2, self.altura // 2

class Robo:
    def __init__(self, x, y, raio=15):
        self.x = x
        self.y = y
        self.raio = raio
        self.angulo = 0  # em radianos
        self.velocidade = 0
        self.energia = 100
        self.recursos_coletados = 0
        self.colisoes = 0
        self.distancia_percorrida = 0
        self.tempo_parado = 0  # Novo: contador de tempo parado
        self.ultima_posicao = (x, y)  # Novo: última posição conhecida
        self.meta_atingida = False  # Novo: flag para controlar se a meta foi atingida
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.energia = 100
        self.recursos_coletados = 0
        self.colisoes = 0
        self.distancia_percorrida = 0
        self.tempo_parado = 0
        self.ultima_posicao = (x, y)
        self.meta_atingida = False
    
    def mover(self, aceleracao, rotacao, ambiente):
        # Atualizar ângulo
        self.angulo += rotacao
        
        # Verificar se o robô está parado
        distancia_movimento = np.sqrt((self.x - self.ultima_posicao[0])**2 + (self.y - self.ultima_posicao[1])**2)
        if distancia_movimento < 0.1:  # Se moveu menos de 0.1 unidades
            self.tempo_parado += 1
            # Forçar movimento após ficar parado por muito tempo
            if self.tempo_parado > 5:  # Após 5 passos parado
                aceleracao = max(0.2, aceleracao)  # Força aceleração mínima
                rotacao = random.uniform(-0.2, 0.2)  # Pequena rotação aleatória
        else:
            self.tempo_parado = 0
        
        # Atualizar velocidade
        self.velocidade += aceleracao
        self.velocidade = max(0.1, min(5, self.velocidade))  # Velocidade mínima de 0.1
        
        # Calcular nova posição
        novo_x = self.x + self.velocidade * np.cos(self.angulo)
        novo_y = self.y + self.velocidade * np.sin(self.angulo)
        
        # Verificar colisão
        if ambiente.verificar_colisao(novo_x, novo_y, self.raio):
            self.colisoes += 1
            self.velocidade = 0.1  # Mantém velocidade mínima mesmo após colisão
            # Tenta uma direção diferente após colisão
            self.angulo += random.uniform(-np.pi/4, np.pi/4)
        else:
            # Atualizar posição
            self.distancia_percorrida += np.sqrt((novo_x - self.x)**2 + (novo_y - self.y)**2)
            self.x = novo_x
            self.y = novo_y
        
        # Atualizar última posição conhecida
        self.ultima_posicao = (self.x, self.y)
        
        # Verificar coleta de recursos
        recursos_coletados = ambiente.verificar_coleta_recursos(self.x, self.y, self.raio)
        self.recursos_coletados += recursos_coletados
        
        # Verificar se atingiu a meta
        if not self.meta_atingida and ambiente.verificar_atingir_meta(self.x, self.y, self.raio):
            self.meta_atingida = True
            # Recuperar energia ao atingir a meta
            self.energia = min(100, self.energia + 50)
        
        # Consumir energia
        self.energia -= 0.1 + 0.05 * self.velocidade + 0.1 * abs(rotacao)
        self.energia = max(0, self.energia)
        
        # Recuperar energia ao coletar recursos
        if recursos_coletados > 0:
            self.energia = min(100, self.energia + 20 * recursos_coletados)
        
        return self.energia <= 0
    
    def get_sensores(self, ambiente):
        # Distância até o recurso mais próximo
        dist_recurso = float('inf')
        for recurso in ambiente.recursos:
            if not recurso['coletado']:
                dist = np.sqrt((self.x - recurso['x'])**2 + (self.y - recurso['y'])**2)
                dist_recurso = min(dist_recurso, dist)
        
        # Distância até o obstáculo mais próximo
        dist_obstaculo = float('inf')
        for obstaculo in ambiente.obstaculos:
            # Simplificação: considerar apenas a distância até o centro do obstáculo
            centro_x = obstaculo['x'] + obstaculo['largura'] / 2
            centro_y = obstaculo['y'] + obstaculo['altura'] / 2
            dist = np.sqrt((self.x - centro_x)**2 + (self.y - centro_y)**2)
            dist_obstaculo = min(dist_obstaculo, dist)
        
        # Distância até a meta
        dist_meta = np.sqrt((self.x - ambiente.meta['x'])**2 + (self.y - ambiente.meta['y'])**2)
        
        # Ângulo até o recurso mais próximo
        angulo_recurso = 0
        if dist_recurso < float('inf'):
            for recurso in ambiente.recursos:
                if not recurso['coletado']:
                    dx = recurso['x'] - self.x
                    dy = recurso['y'] - self.y
                    angulo = np.arctan2(dy, dx)
                    angulo_recurso = angulo - self.angulo
                    # Normalizar para [-pi, pi]
                    while angulo_recurso > np.pi:
                        angulo_recurso -= 2 * np.pi
                    while angulo_recurso < -np.pi:
                        angulo_recurso += 2 * np.pi
                    break
        
        # Ângulo até a meta
        dx_meta = ambiente.meta['x'] - self.x
        dy_meta = ambiente.meta['y'] - self.y
        angulo_meta = np.arctan2(dy_meta, dx_meta) - self.angulo
        # Normalizar para [-pi, pi]
        while angulo_meta > np.pi:
            angulo_meta -= 2 * np.pi
        while angulo_meta < -np.pi:
            angulo_meta += 2 * np.pi
        
        return {
            'dist_recurso': dist_recurso,
            'dist_obstaculo': dist_obstaculo,
            'dist_meta': dist_meta,
            'angulo_recurso': angulo_recurso,
            'angulo_meta': angulo_meta,
            'energia': self.energia,
            'velocidade': self.velocidade,
            'meta_atingida': self.meta_atingida
        }

class Simulador:
    def __init__(self, ambiente, robo, individuo):
        self.ambiente = ambiente
        self.robo = robo
        self.individuo = individuo
        self.frames = []
        
        # Configurar matplotlib para melhor visualização
        plt.style.use('default')  # Usar estilo padrão
        plt.ion()  # Modo interativo
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_xlim(0, ambiente.largura)
        self.ax.set_ylim(0, ambiente.altura)
        self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
    
    def simular(self):
        self.ambiente.reset()
        # Encontrar uma posição segura para o robô
        x_inicial, y_inicial = self.ambiente.posicao_segura(self.robo.raio)
        self.robo.reset(x_inicial, y_inicial)
        self.frames = []
        
        # Limpar a figura atual
        self.ax.clear()
        self.ax.set_xlim(0, self.ambiente.largura)
        self.ax.set_ylim(0, self.ambiente.altura)
        self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Desenhar obstáculos (estáticos)
        for obstaculo in self.ambiente.obstaculos:
            rect = patches.Rectangle(
                (obstaculo['x'], obstaculo['y']),
                obstaculo['largura'],
                obstaculo['altura'],
                linewidth=1,
                edgecolor='black',
                facecolor='#FF9999',  # Vermelho claro
                alpha=0.7
            )
            self.ax.add_patch(rect)
        
        # Desenhar recursos (estáticos)
        for recurso in self.ambiente.recursos:
            if not recurso['coletado']:
                circ = patches.Circle(
                    (recurso['x'], recurso['y']),
                    10,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#99FF99',  # Verde claro
                    alpha=0.8
                )
                self.ax.add_patch(circ)
        
        # Desenhar a meta
        meta_circ = patches.Circle(
            (self.ambiente.meta['x'], self.ambiente.meta['y']),
            self.ambiente.meta['raio'],
            linewidth=2,
            edgecolor='black',
            facecolor='#FFFF00',  # Amarelo
            alpha=0.8
        )
        self.ax.add_patch(meta_circ)
        
        # Criar objetos para o robô e direção (serão atualizados)
        robo_circ = patches.Circle(
            (self.robo.x, self.robo.y),
            self.robo.raio,
            linewidth=1,
            edgecolor='black',
            facecolor='#9999FF',  # Azul claro
            alpha=0.8
        )
        self.ax.add_patch(robo_circ)
        
        # Criar texto para informações
        info_text = self.ax.text(
            10, self.ambiente.altura - 50,  # Alterado de 10 para 50 para descer a legenda
            "",
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
        )
        
        # Atualizar a figura
        plt.draw()
        plt.pause(0.01)
        
        try:
            while True:
                # Obter sensores
                sensores = self.robo.get_sensores(self.ambiente)
                
                # Avaliar árvores de decisão
                aceleracao = self.individuo.avaliar(sensores, 'aceleracao')
                rotacao = self.individuo.avaliar(sensores, 'rotacao')
                
                # Limitar valores
                aceleracao = max(-1, min(1, aceleracao))
                rotacao = max(-0.5, min(0.5, rotacao))
                
                # Mover robô
                sem_energia = self.robo.mover(aceleracao, rotacao, self.ambiente)
                
                # Atualizar visualização em tempo real
                self.ax.clear()
                self.ax.set_xlim(0, self.ambiente.largura)
                self.ax.set_ylim(0, self.ambiente.altura)
                self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
                self.ax.set_xlabel("X", fontsize=12)
                self.ax.set_ylabel("Y", fontsize=12)
                self.ax.grid(True, linestyle='--', alpha=0.7)
                
                # Desenhar obstáculos
                for obstaculo in self.ambiente.obstaculos:
                    rect = patches.Rectangle(
                        (obstaculo['x'], obstaculo['y']),
                        obstaculo['largura'],
                        obstaculo['altura'],
                        linewidth=1,
                        edgecolor='black',
                        facecolor='#FF9999',
                        alpha=0.7
                    )
                    self.ax.add_patch(rect)
                
                # Desenhar recursos
                for recurso in self.ambiente.recursos:
                    if not recurso['coletado']:
                        circ = patches.Circle(
                            (recurso['x'], recurso['y']),
                            10,
                            linewidth=1,
                            edgecolor='black',
                            facecolor='#99FF99',
                            alpha=0.8
                        )
                        self.ax.add_patch(circ)
                
                # Desenhar a meta
                meta_circ = patches.Circle(
                    (self.ambiente.meta['x'], self.ambiente.meta['y']),
                    self.ambiente.meta['raio'],
                    linewidth=2,
                    edgecolor='black',
                    facecolor='#FFFF00',  # Amarelo
                    alpha=0.8
                )
                self.ax.add_patch(meta_circ)
                
                # Desenhar robô
                robo_circ = patches.Circle(
                    (self.robo.x, self.robo.y),
                    self.robo.raio,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#9999FF',
                    alpha=0.8
                )
                self.ax.add_patch(robo_circ)
                
                # Desenhar direção do robô
                direcao_x = self.robo.x + self.robo.raio * np.cos(self.robo.angulo)
                direcao_y = self.robo.y + self.robo.raio * np.sin(self.robo.angulo)
                self.ax.plot([self.robo.x, direcao_x], [self.robo.y, direcao_y], 'r-', linewidth=2)
                
                # Adicionar informações
                info_text = self.ax.text(
                    10, self.ambiente.altura - 50,  # Alterado de 10 para 50 para descer a legenda
                    f"Tempo: {self.ambiente.tempo}\n"
                    f"Recursos: {self.robo.recursos_coletados}\n"
                    f"Energia: {self.robo.energia:.1f}\n"
                    f"Colisões: {self.robo.colisoes}\n"
                    f"Distância: {self.robo.distancia_percorrida:.1f}\n"
                    f"Meta atingida: {'Sim' if self.robo.meta_atingida else 'Não'}",
                    fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
                )
                
                # Atualizar a figura
                plt.draw()
                plt.pause(0.05)
                
                # Verificar fim da simulação
                if sem_energia or self.ambiente.passo():
                    break
            
            # Manter a figura aberta até que o usuário a feche
            plt.ioff()
            plt.show()
            
        except KeyboardInterrupt:
            plt.close('all')
        
        return self.frames
    
    def animar(self):
        # Desativar o modo interativo antes de criar a animação
        plt.ioff()
        
        # Criar a animação
        anim = animation.FuncAnimation(
            self.fig, self.atualizar_frame,
            frames=len(self.frames),
            interval=50,
            blit=True,
            repeat=True  # Permitir que a animação repita
        )
        
        # Mostrar a animação e manter a janela aberta
        plt.show(block=True)
    
    def atualizar_frame(self, frame_idx):
        return self.frames[frame_idx]

# =====================================================================
# PARTE 2: ALGORITMO GENÉTICO (PARA O VOCÊ MODIFICAR)
# Esta parte contém a implementação do algoritmo genético.
# Deve modificar os parâmetros e a lógica para melhorar o desempenho.
# =====================================================================

class IndividuoPG:
    def __init__(self, profundidade=4):
        self.profundidade = profundidade
        self.arvore_aceleracao = self.criar_arvore_aleatoria()
        self.arvore_rotacao = self.criar_arvore_aleatoria()
        self.fitness = 0
    
    def criar_arvore_aleatoria(self):
        if self.profundidade == 0:
            return self.criar_folha()
        
        # OPERADORES DISPONÍVEIS PARA O ALUNO MODIFICAR
        operador = random.choice(['+', '-', '*', '/', 'max', 'min', 'abs', 'if_positivo', 'if_negativo', 'sin', 'cos', 'tan'])
        if operador in ['+', '-', '*', '/']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'direita': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria()
            }
        elif operador in ['max', 'min']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'direita': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria()
            }
        elif operador in ['abs', 'sin', 'cos', 'tan']: # OPERADORES UNÁRIOS
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'direita': None
            }
        else:  # if_positivo ou if_negativo
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria(),
                'direita': IndividuoPG(self.profundidade - 1).criar_arvore_aleatoria()
            }
    
    def criar_folha(self):
        # VARIÁVEIS DISPONÍVEIS PARA O ALUNO MODIFICAR
        tipo = random.choice(['constante', 'dist_recurso', 'dist_obstaculo', 'dist_meta', 'angulo_recurso', 'angulo_meta', 'energia', 'velocidade', 'meta_atingida'])
        if tipo == 'constante':
            return {
                'tipo': 'folha',
                'valor': round(random.uniform(-2.0, 2.0), 3)
            }
        else:
            return {
                'tipo': 'folha',
                'variavel': tipo
            }
    
    def avaliar(self, sensores, tipo='aceleracao'):
        arvore = self.arvore_aceleracao if tipo == 'aceleracao' else self.arvore_rotacao
        return self.avaliar_no(arvore, sensores)
    
    def avaliar_no(self, no, sensores):
        if no is None:
            return 0.0 # Retornar float para consistência
            
        if no['tipo'] == 'folha':
            if 'valor' in no:
                return float(no['valor']) # Garantir float
            elif 'variavel' in no:
                val = sensores[no['variavel']]
                # Normalizar booleanos para float
                if isinstance(val, bool):
                    return 1.0 if val else 0.0
                if not np.isfinite(val): # Checagem adicional para valores de sensores
                    return 0.0
                return float(val) # Garantir float
        
        # Avaliar 'esquerda' primeiro para operadores unários e condicionais
        esquerda_val = self.avaliar_no(no['esquerda'], sensores)

        # Checar se esquerda_val é finito antes de usar em funções que podem causar erro
        if not np.isfinite(esquerda_val):
            esquerda_val = 0.0 # Valor padrão se não for finito

        if no['operador'] == 'abs':
            return abs(esquerda_val)
        elif no['operador'] == 'sin':
            return np.sin(esquerda_val)
        elif no['operador'] == 'cos':
            return np.cos(esquerda_val)
        elif no['operador'] == 'tan':
            if np.isclose(np.abs(np.cos(esquerda_val)), 0.0): # Evita tan(pi/2)
                # Retorna um valor grande, mas finito, com o sinal de esquerda_val
                # para manter alguma informação direcional, se aplicável.
                return np.sign(esquerda_val) * 1e6 if np.sign(esquerda_val) != 0 else 1e6
            return np.tan(esquerda_val)
        elif no['operador'] == 'if_positivo':
            if esquerda_val > 0:
                direita_val_condicional = self.avaliar_no(no['direita'], sensores)
                return direita_val_condicional if np.isfinite(direita_val_condicional) else 0.0
            else:
                return 0.0
        elif no['operador'] == 'if_negativo':
            if esquerda_val < 0:
                direita_val_condicional = self.avaliar_no(no['direita'], sensores)
                return direita_val_condicional if np.isfinite(direita_val_condicional) else 0.0
            else:
                return 0.0
        
        # Para operadores binários, avaliar 'direita'
        direita_val = self.avaliar_no(no['direita'], sensores) if no['direita'] is not None else 0.0
        
        if not np.isfinite(direita_val): # Checar se direita_val é finito
            direita_val = 0.0 # Valor padrão se não for finito
        
        if no['operador'] == '+':
            return esquerda_val + direita_val
        elif no['operador'] == '-':
            return esquerda_val - direita_val
        elif no['operador'] == '*':
            return esquerda_val * direita_val
        elif no['operador'] == '/':
            if np.isclose(direita_val, 0.0):
                return 0.0 
            res = esquerda_val / direita_val
            return res if np.isfinite(res) else 0.0
        elif no['operador'] == 'max':
            return max(esquerda_val, direita_val)
        elif no['operador'] == 'min':
            return min(esquerda_val, direita_val)
        
        return 0.0 # Caso nenhum operador corresponda
    
    def mutacao(self, probabilidade=0.2):
        self.mutacao_no(self.arvore_aceleracao, probabilidade)
        self.mutacao_no(self.arvore_rotacao, probabilidade)
    
    def mutacao_no(self, no, probabilidade):
        if no is None: # Adicionado para segurança
            return

        if random.random() < probabilidade:
            if no['tipo'] == 'folha':
                if 'valor' in no:
                    no['valor'] = random.uniform(-2.0, 2.0)
                elif 'variavel' in no:
                    no['variavel'] = random.choice(['dist_recurso', 'dist_obstaculo', 'dist_meta', 'angulo_recurso', 'angulo_meta', 'energia', 'velocidade', 'meta_atingida'])
            elif no['tipo'] == 'operador': # Garantir que é um operador
                operadores_binarios = ['+', '-', '*', '/', 'max', 'min', 'if_positivo', 'if_negativo']
                operadores_unarios = ['abs', 'sin', 'cos', 'tan']
                if no.get('direita') is not None: # Se tem um nó à direita, era binário ou if
                    if no['operador'] in ['if_positivo', 'if_negativo']:
                         no['operador'] = random.choice(operadores_binarios + ['if_positivo', 'if_negativo']) # Pode manter-se como if ou mudar
                    else:
                        no['operador'] = random.choice(operadores_binarios)
                else: # Era um operador unário
                    no['operador'] = random.choice(operadores_unarios)

        if no['tipo'] == 'operador':
            if no.get('esquerda'): # Usar .get() para segurança
                self.mutacao_no(no['esquerda'], probabilidade)
            if no.get('direita'): # Usar .get() para segurança
                self.mutacao_no(no['direita'], probabilidade)
    
    def crossover(self, outro):
        novo = IndividuoPG(self.profundidade)
        novo.arvore_aceleracao = self._crossover_arvore(self.arvore_aceleracao, outro.arvore_aceleracao)
        novo.arvore_rotacao = self._crossover_arvore(self.arvore_rotacao, outro.arvore_rotacao)
        return novo

    def _get_todos_nos(self, arvore, nos_disponiveis=None): # Renomeado para clareza
        if nos_disponiveis is None:
            nos_disponiveis = []
        
        if arvore:
            nos_disponiveis.append(arvore)
            if arvore['tipo'] == 'operador':
                if arvore.get('esquerda'): # Usar .get()
                    self._get_todos_nos(arvore['esquerda'], nos_disponiveis)
                if arvore.get('direita'): # Usar .get()
                    self._get_todos_nos(arvore['direita'], nos_disponiveis)
        return nos_disponiveis # Retorna a lista preenchida


    def _copiar_arvore(self, arvore):
        if arvore is None:
            return None
        
        copia = {} # Criar novo dict
        copia['tipo'] = arvore['tipo']

        if arvore['tipo'] == 'folha':
            if 'valor' in arvore:
                copia['valor'] = arvore['valor']
            elif 'variavel' in arvore:
                copia['variavel'] = arvore['variavel']
        elif arvore['tipo'] == 'operador':
            copia['operador'] = arvore['operador']
            copia['esquerda'] = self._copiar_arvore(arvore.get('esquerda')) # Usar .get()
            if 'direita' in arvore and arvore['direita'] is not None: # Checar existência antes de copiar
                copia['direita'] = self._copiar_arvore(arvore['direita'])
            else:
                copia['direita'] = None # Explicitamente None se não existir ou for None
        return copia

    def _crossover_arvore(self, arvore1, arvore2):
        if random.random() < 0.05 or arvore1 is None or arvore2 is None: # Chance baixa de não cruzar, ou se uma das árvores for None
            return self._copiar_arvore(random.choice([arvore1, arvore2]) if arvore1 or arvore2 else self.criar_arvore_aleatoria()) # Escolhe uma ou cria nova se ambas None

        copia_arvore1 = self._copiar_arvore(arvore1)
        copia_arvore2 = self._copiar_arvore(arvore2)

        nos_arvore1 = self._get_todos_nos(copia_arvore1)
        nos_arvore2 = self._get_todos_nos(copia_arvore2)

        if not nos_arvore1 or not nos_arvore2: # Se uma das árvores não tem nós (improvável com _copiar_arvore e _get_todos_nos corretos)
            return self._copiar_arvore(random.choice([arvore1, arvore2]) if arvore1 or arvore2 else self.criar_arvore_aleatoria())


        ponto_crossover_em_arv1_ref = random.choice(nos_arvore1)
        sub_arvore_de_arv2_copia = self._copiar_arvore(random.choice(nos_arvore2))


        # Se o ponto de crossover for a raiz da arvore1, simplesmente retorna a sub-árvore copiada da arvore2
        if id(copia_arvore1) == id(ponto_crossover_em_arv1_ref):
            return sub_arvore_de_arv2_copia
        
        # Caso contrário, precisamos encontrar o pai do ponto_crossover_em_arv1_ref e substituir o filho correto
        # Esta é uma busca BFS/DFS para encontrar o pai e substituir.
        queue = [copia_arvore1]
        encontrado_e_substituido = False
        while queue and not encontrado_e_substituido:
            no_atual = queue.pop(0)
            if no_atual and no_atual['tipo'] == 'operador':
                if no_atual.get('esquerda') and id(no_atual['esquerda']) == id(ponto_crossover_em_arv1_ref):
                    no_atual['esquerda'] = sub_arvore_de_arv2_copia
                    encontrado_e_substituido = True
                    break 
                elif no_atual.get('esquerda'):
                    queue.append(no_atual['esquerda'])

                if no_atual.get('direita') and id(no_atual['direita']) == id(ponto_crossover_em_arv1_ref):
                    no_atual['direita'] = sub_arvore_de_arv2_copia
                    encontrado_e_substituido = True
                    break
                elif no_atual.get('direita'):
                    queue.append(no_atual['direita'])
        
        return copia_arvore1 if encontrado_e_substituido else self._copiar_arvore(arvore1) # Retorna a original se a substituição falhou


    def salvar(self, arquivo):
        with open(arquivo, 'w') as f:
            json.dump({
                'arvore_aceleracao': self.arvore_aceleracao,
                'arvore_rotacao': self.arvore_rotacao
            }, f, indent=2)
    
    @classmethod
    def carregar(cls, arquivo):
        with open(arquivo, 'r') as f:
            dados = json.load(f)
            individuo = cls() # Assume que __init__ pode ser chamado sem profundidade ou usa um default
            individuo.arvore_aceleracao = dados['arvore_aceleracao']
            individuo.arvore_rotacao = dados['arvore_rotacao']
            # Seria bom guardar a profundidade no JSON também se ela for variável no carregamento
            # ou se o construtor do IndividuoPG depender dela de forma crítica.
            # Por ora, o __init__ usa um valor padrão se não for passado.
            return individuo

class ProgramacaoGenetica:
    def __init__(self, tamanho_populacao=60, profundidade=4): # PARÂMETROS MODIFICADOS
        self.tamanho_populacao = tamanho_populacao
        self.profundidade = profundidade
        self.populacao = [IndividuoPG(profundidade) for _ in range(tamanho_populacao)]
        self.melhor_individuo = None
        self.melhor_fitness = float('-inf')
        self.historico_fitness = []
    
    def avaliar_populacao(self):
        ambiente = Ambiente()
        # Posição inicial do robô pode ser aleatória e segura, ou fixa para consistência nos testes
        x_inicial, y_inicial = ambiente.posicao_segura() 
        robo = Robo(x_inicial, y_inicial)
        
        for individuo in self.populacao:
            fitness_total_individuo = 0
            num_tentativas_avaliacao = 3  # NÚMERO DE TENTATIVAS DE AVALIAÇÃO MODIFICADO
            
            for i in range(num_tentativas_avaliacao):
                # Resetar ambiente com novos obstáculos/recursos para cada tentativa de avaliação do indivíduo,
                # ou usar o mesmo ambiente para todas as tentativas de um indivíduo, mas diferente entre indivíduos.
                # Para maior robustez, idealmente, cada indivíduo é testado em múltiplos cenários.
                ambiente_teste = Ambiente(num_obstaculos=random.randint(4,7), num_recursos=random.randint(4,7)) # Cenário dinâmico
                x_robo_teste, y_robo_teste = ambiente_teste.posicao_segura()
                robo_teste = Robo(x_robo_teste, y_robo_teste) # Novo robô para o teste
                robo_teste.reset(x_robo_teste, y_robo_teste)
                
                # Limpar estado do ambiente de teste
                ambiente_teste.reset()


                while True:
                    sensores = robo_teste.get_sensores(ambiente_teste)
                    
                    aceleracao = individuo.avaliar(sensores, 'aceleracao')
                    rotacao = individuo.avaliar(sensores, 'rotacao')
                    
                    # Aplicar limites mais realistas ou normalizar saídas
                    aceleracao = np.clip(aceleracao, -1.0, 1.0)
                    rotacao = np.clip(rotacao, -0.6, 0.6) # Rotação um pouco maior
                    
                    sem_energia = robo_teste.mover(aceleracao, rotacao, ambiente_teste)
                    
                    if sem_energia or ambiente_teste.passo() or robo_teste.meta_atingida: # Parar se a meta for atingida também
                        break
                
                # FUNÇÃO DE FITNESS MODIFICADA
                fitness_tentativa = 0
                # Bonificação por recursos
                fitness_tentativa += robo_teste.recursos_coletados * 250
                # Bonificação por atingir a meta
                if robo_teste.meta_atingida:
                    fitness_tentativa += 1000
                    # Bonificação adicional por atingir a meta com mais energia e menos tempo
                    fitness_tentativa += (robo_teste.energia * 2)
                    fitness_tentativa -= (ambiente_teste.tempo * 0.5)


                # Penalidade por colisões
                fitness_tentativa -= robo_teste.colisoes * 20
                # Penalidade por energia gasta (se não atingiu a meta)
                if not robo_teste.meta_atingida:
                     fitness_tentativa -= (100 - robo_teste.energia) * 0.5
                # Incentivo à exploração (distância percorrida) se não coletou muitos recursos ou não atingiu a meta
                # if robo_teste.recursos_coletados < 2 and not robo_teste.meta_atingida:
                #     fitness_tentativa += robo_teste.distancia_percorrida * 0.02
                
                
                if robo_teste.meta_atingida and len(ambiente_teste.recursos) > 0:
                    # Penalidade por não coletar recursos se a meta foi atingida
                    fitness_tentativa -= 300 * len(ambiente_teste.recursos)
                    
                if robo_teste.energia < 50:
                    fitness_tentativa -= 150 # Penalidade leve por energia baixa


                # Evitar fitness negativo extremo
                fitness_total_individuo += max(-500, fitness_tentativa) # Fitness pode ser negativo, mas com um piso
            
            individuo.fitness = fitness_total_individuo / num_tentativas_avaliacao
            
            if individuo.fitness > self.melhor_fitness:
                self.melhor_fitness = individuo.fitness
                # Criar uma cópia profunda do melhor indivíduo para evitar que mutações subsequentes o afetem
                self.melhor_individuo = individuo._copiar_arvore(individuo.arvore_aceleracao) # Isso está errado, precisa copiar o objeto
                # Correção:
                novo_melhor = IndividuoPG(individuo.profundidade)
                novo_melhor.arvore_aceleracao = individuo._copiar_arvore(individuo.arvore_aceleracao)
                novo_melhor.arvore_rotacao = individuo._copiar_arvore(individuo.arvore_rotacao)
                novo_melhor.fitness = individuo.fitness
                self.melhor_individuo = novo_melhor

    def selecionar(self):
        # MÉTODO DE SELEÇÃO MODIFICADO: Torneio com um pouco de Roleta
        selecionados = []
        tamanho_torneio = 5  # TAMANHO DO TORNEIO MODIFICADO

        for _ in range(self.tamanho_populacao):
            # Adicionar uma pequena chance de seleção aleatória (para diversidade)
            if random.random() < 0.1: # 10% de chance de pegar um aleatório
                 selecionados.append(random.choice(self.populacao))
            else:
                torneio = random.sample(self.populacao, tamanho_torneio)
                vencedor = max(torneio, key=lambda x: x.fitness)
                selecionados.append(vencedor)
        return selecionados
    
    def evoluir(self, n_geracoes=60): # NÚMERO DE GERAÇÕES MODIFICADO
        if not self.populacao:
            print("População inicial vazia. Abortando evolução.")
            return None, []


        for geracao in range(n_geracoes):
            print(f"\nGeração {geracao + 1}/{n_geracoes}")

            self.avaliar_populacao()

            # Garantir que melhor_individuo não seja None após a primeira avaliação
            if self.melhor_individuo is None and self.populacao:
                 # Se ainda for None, inicializa com o melhor da população atual
                pop_ordenada = sorted(self.populacao, key=lambda ind: ind.fitness, reverse=True)
                if pop_ordenada:
                    melhor_atual = pop_ordenada[0]
                    novo_melhor = IndividuoPG(melhor_atual.profundidade)
                    novo_melhor.arvore_aceleracao = self.melhor_individuo._copiar_arvore(melhor_atual.arvore_aceleracao) if hasattr(self.melhor_individuo, '_copiar_arvore') else melhor_atual.arvore_aceleracao # fallback
                    novo_melhor.arvore_rotacao = self.melhor_individuo._copiar_arvore(melhor_atual.arvore_rotacao) if hasattr(self.melhor_individuo, '_copiar_arvore') else melhor_atual.arvore_rotacao # fallback
                    novo_melhor.fitness = melhor_atual.fitness
                    self.melhor_individuo = novo_melhor
                    self.melhor_fitness = novo_melhor.fitness


            fitness_geracao = [ind.fitness for ind in self.populacao]
            if not fitness_geracao: # Se a população esvaziar por algum motivo
                print("População esvaziada durante a evolução.")
                break
            
            fitness_medio = sum(fitness_geracao) / len(fitness_geracao) if fitness_geracao else 0
            pior_fitness = min(fitness_geracao) if fitness_geracao else 0
            melhor_fitness_atual_geracao = max(fitness_geracao) if fitness_geracao else self.melhor_fitness # Usa o global se a lista estiver vazia


            self.historico_fitness.append(self.melhor_fitness) # Registra o melhor global histórico

            print(f"Melhor fitness global: {self.melhor_fitness:.2f}")
            print(f"Melhor fitness da geração: {melhor_fitness_atual_geracao:.2f}")
            print(f"Fitness médio da geração: {fitness_medio:.2f}, Pior fitness da geração: {pior_fitness:.2f}")

            with open("log.txt", "a") as f:
                f.write(f"Geração {geracao + 1}: Melhor Global={self.melhor_fitness:.2f}, Melhor da Geração={melhor_fitness_atual_geracao:.2f}, Médio={fitness_medio:.2f}, Pior={pior_fitness:.2f}\n")

            selecionados = self.selecionar()
            nova_populacao = []

            # Elitismo: manter o melhor indivíduo global se ele existir
            if self.melhor_individuo:
                # Adicionar uma cópia para evitar que seja modificado por mutação se ele for selecionado como pai
                elite_copia = IndividuoPG(self.melhor_individuo.profundidade)
                elite_copia.arvore_aceleracao = self.melhor_individuo._copiar_arvore(self.melhor_individuo.arvore_aceleracao) if hasattr(self.melhor_individuo, '_copiar_arvore') else self.melhor_individuo.arvore_aceleracao
                elite_copia.arvore_rotacao = self.melhor_individuo._copiar_arvore(self.melhor_individuo.arvore_rotacao) if hasattr(self.melhor_individuo, '_copiar_arvore') else self.melhor_individuo.arvore_rotacao
                elite_copia.fitness = self.melhor_individuo.fitness
                nova_populacao.append(elite_copia)


            # Preencher o resto da população com crossover e mutação
            # Garantir que selecionados não esteja vazio
            if not selecionados:
                print("Nenhum indivíduo selecionado. Repopulando aleatoriamente.")
                selecionados = [IndividuoPG(self.profundidade) for _ in range(self.tamanho_populacao)]


            while len(nova_populacao) < self.tamanho_populacao:
                if len(selecionados) >= 2:
                    pai1, pai2 = random.sample(selecionados, 2)
                elif selecionados: # Se houver apenas um, usa-o duas vezes (ou cria um novo)
                    pai1 = random.choice(selecionados)
                    pai2 = random.choice(self.populacao) # Pega um da população antiga para diversificar
                else: # Se selecionados estiver vazio (não deveria acontecer com o fallback acima)
                    pai1 = IndividuoPG(self.profundidade)
                    pai2 = IndividuoPG(self.profundidade)

                filho = pai1.crossover(pai2)
                filho.mutacao(probabilidade=0.25)  # PROBABILIDADE DE MUTAÇÃO MODIFICADA
                nova_populacao.append(filho)
        
        self.populacao = nova_populacao[:self.tamanho_populacao] # Garante o tamanho correto da população

        # Após a última geração, plotar gráfico
        if self.historico_fitness:
            plt.figure() # Cria uma nova figura para o gráfico de fitness
            plt.plot(self.historico_fitness, label='Melhor Fitness Global por Geração')
            plt.xlabel('Geração')
            plt.ylabel('Fitness')
            plt.title('Evolução do Melhor Fitness Global')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.savefig('grafico_fitness_evolucao.png')
            plt.show(block=False) # Não bloquear para permitir que o resto do código execute
            plt.pause(1) # Pausa para dar tempo de ver o gráfico
            plt.close() # Fecha a figura do gráfico

        return self.melhor_individuo, self.historico_fitness
# =====================================================================
# PARTE 3: EXECUÇÃO DO PROGRAMA (PARA O ALUNO MODIFICAR)
# Esta parte contém a execução do programa e os parâmetros finais.
# =====================================================================

# Executando o algoritmo
if __name__ == "__main__":
    print("Iniciando simulação de robô com programação genética...")
    
    # Criar e treinar o algoritmo genético
    print("Treinando o algoritmo genético...")
    # PARÂMETROS PARA O ALUNO MODIFICAR
    pg = ProgramacaoGenetica(tamanho_populacao=200, profundidade=4)
    melhor_individuo, historico = pg.evoluir(n_geracoes=6)
    
    # Salvar o melhor indivíduo
    print("Salvando o melhor indivíduo...")
    melhor_individuo.salvar('melhor_robo.json')
    
    # Plotar evolução do fitness
    print("Plotando evolução do fitness...")
    plt.figure(figsize=(5, 10))
    plt.plot(historico)
    plt.title('Evolução do Fitness')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.savefig('evolucao_fitness_robo.png')
    plt.close()
    
    # Simular o melhor indivíduo
    print("Simulando o melhor indivíduo...")
    ambiente = Ambiente()
    robo = Robo(ambiente.largura // 2, ambiente.altura // 2)
    simulador = Simulador(ambiente, robo, melhor_individuo)
    
    print("Executando simulação em tempo real...")
    print("A simulação será exibida em uma janela separada.")
    print("Pressione Ctrl+C para fechar a janela quando desejar.")
    simulador.simular() 