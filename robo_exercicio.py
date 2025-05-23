import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import json
import time
import pandas as pd
import copy

# =====================================================================
# PARTE 1: ESTRUTURA DA SIMULAÇÃO (NÃO MODIFICAR)
# Esta parte contém a estrutura básica da simulação, incluindo o ambiente,
# o robô e a visualização. Não é recomendado modificar esta parte.
# =====================================================================

class Ambiente:
    def __init__(self, largura=800, altura=600, num_obstaculos=5, num_recursos=7):
        self.largura = largura
        self.altura = altura
        self.obstaculos = self.gerar_obstaculos(num_obstaculos)
        self.recursos = self.gerar_recursos(num_recursos)
        self.tempo = 0
        self.max_tempo = 500  # Aumentado para 500
        self.meta = self.gerar_meta()  # Adicionando a meta
        self.meta_atingida = False  # Flag para controlar se a meta foi atingida
    
    def posicao_valida(self, x, y, raio, lista_objetos):
        """Verifica se uma posição é válida (não sobrepõe outros objetos)"""
        # Verificar bordas
        if x - raio < 0 or x + raio > self.largura or y - raio < 0 or y + raio > self.altura:
            return False
        
        # Verificar sobreposição com outros objetos
        for obj in lista_objetos:
            if 'largura' in obj:  # É um obstáculo
                if (x + raio > obj['x'] and 
                    x - raio < obj['x'] + obj['largura'] and
                    y + raio > obj['y'] and 
                    y - raio < obj['y'] + obj['altura']):
                    return False
            else:  # É um recurso ou meta
                dist = np.sqrt((x - obj['x'])**2 + (y - obj['y'])**2)
                if dist < raio + 20:  # 20 é a margem de segurança
                    return False
        return True
    
    def gerar_obstaculos(self, num_obstaculos):
        obstaculos = []
        max_tentativas = 100
        
        for _ in range(num_obstaculos):
            tentativas = 0
            while tentativas < max_tentativas:
                x = random.randint(50, self.largura - 50)
                y = random.randint(50, self.altura - 50)
                largura = random.randint(20, 100)
                altura = random.randint(20, 100)
                
                # Verificar se o obstáculo é válido
                if self.posicao_valida(x, y, max(largura, altura)/2, obstaculos):
                    obstaculos.append({
                        'x': x,
                        'y': y,
                        'largura': largura,
                        'altura': altura
                    })
                    break
                tentativas += 1
            
            if tentativas == max_tentativas:
                print("Aviso: Não foi possível gerar todos os obstáculos desejados")
        
        return obstaculos
    
    def gerar_recursos(self, num_recursos):
        recursos = []
        max_tentativas = 100
        
        for _ in range(num_recursos):
            tentativas = 0
            while tentativas < max_tentativas:
                x = random.randint(20, self.largura - 20)
                y = random.randint(20, self.altura - 20)
                
                # Verificar se o recurso é válido
                if self.posicao_valida(x, y, 10, self.obstaculos + recursos):  # 10 é o raio do recurso
                    recursos.append({
                        'x': x,
                        'y': y,
                        'coletado': False
                    })
                    break
                tentativas += 1
            
            if tentativas == max_tentativas:
                print("Aviso: Não foi possível gerar todos os recursos desejados")
        
        return recursos
    
    def gerar_meta(self):
        max_tentativas = 100
        margem = 50
        
        for _ in range(max_tentativas):
            x = random.randint(margem, self.largura - margem)
            y = random.randint(margem, self.altura - margem)
            
            # Verificar se a posição da meta é válida
            if self.posicao_valida(x, y, 30, self.obstaculos + self.recursos):  # 30 é o raio da meta
                return {
                    'x': x,
                    'y': y,
                    'raio': 30
                }
        
        # Se não encontrar uma posição válida, retorna o centro
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
        self.tempo_parado = 0
        self.ultima_posicao = (x, y)
        self.meta_atingida = False
        self.ultimo_recurso_coletado = None  # Novo: rastrear último recurso coletado
        self.proximo_recurso = None  # Novo: rastrear próximo recurso alvo
    
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
        self.ultimo_recurso_coletado = None
        self.proximo_recurso = None
    
    def encontrar_proximo_recurso(self, ambiente):
        recursos_disponiveis = [r for r in ambiente.recursos if not r['coletado']]
        if not recursos_disponiveis:
            return None
        
        # Calcular distância e ângulo para cada recurso disponível
        distancias_angulos = []
        for recurso in recursos_disponiveis:
            # Calcular distância
            dist = np.sqrt((recurso['x'] - self.x)**2 + (recurso['y'] - self.y)**2)
            
            # Calcular ângulo
            dx = recurso['x'] - self.x
            dy = recurso['y'] - self.y
            angulo = np.arctan2(dy, dx) - self.angulo
            
            # Normalizar ângulo
            while angulo > np.pi:
                angulo -= 2 * np.pi
            while angulo < -np.pi:
                angulo += 2 * np.pi
            
            # Verificar se há obstáculos no caminho (menos restritivo)
            tem_obstaculo = False
            for obstaculo in ambiente.obstaculos:
                # Só penaliza se o obstáculo estiver realmente entre o robô e o recurso
                cx = obstaculo['x'] + obstaculo['largura']/2
                cy = obstaculo['y'] + obstaculo['altura']/2
                proj = ((cx - self.x) * dx + (cy - self.y) * dy) / (dx**2 + dy**2)
                if 0 < proj < 1:
                    px = self.x + proj * dx
                    py = self.y + proj * dy
                    dist_obstaculo = np.sqrt((px - cx)**2 + (py - cy)**2)
                    if dist_obstaculo < max(obstaculo['largura'], obstaculo['altura'])/2 + 10:  # só penaliza se realmente está no caminho
                        tem_obstaculo = True
                        break
            
            # Adicionar à lista com peso baseado na distância e ângulo
            peso = dist * (1 + abs(angulo))
            if tem_obstaculo:
                peso *= 1.1  # Penalização menor
            
            distancias_angulos.append((peso, dist, angulo, recurso))
        
        # Escolher o recurso com menor peso
        if distancias_angulos:
            self.proximo_recurso = min(distancias_angulos, key=lambda x: x[0])[3]
        else:
            self.proximo_recurso = None
        
        return self.proximo_recurso

    def get_sensores(self, ambiente):
        # Encontrar próximo recurso
        proximo_recurso = self.encontrar_proximo_recurso(ambiente)
        
        # Distância até o próximo recurso
        dist_recurso = float('inf')
        angulo_recurso = 0
        if proximo_recurso:
            dist_recurso = np.sqrt((self.x - proximo_recurso['x'])**2 + (self.y - proximo_recurso['y'])**2)
            dx = proximo_recurso['x'] - self.x
            dy = proximo_recurso['y'] - self.y
            angulo_recurso = np.arctan2(dy, dx) - self.angulo
            # Normalizar para [-pi, pi]
            while angulo_recurso > np.pi:
                angulo_recurso -= 2 * np.pi
            while angulo_recurso < -np.pi:
                angulo_recurso += 2 * np.pi
        
        # Distância até o obstáculo mais próximo e seu ângulo
        dist_obstaculo = float('inf')
        angulo_obstaculo = 0
        for obstaculo in ambiente.obstaculos:
            centro_x = obstaculo['x'] + obstaculo['largura'] / 2
            centro_y = obstaculo['y'] + obstaculo['altura'] / 2
            dist = np.sqrt((self.x - centro_x)**2 + (self.y - centro_y)**2)
            dx = centro_x - self.x
            dy = centro_y - self.y
            angulo = np.arctan2(dy, dx) - self.angulo
            while angulo > np.pi:
                angulo -= 2 * np.pi
            while angulo < -np.pi:
                angulo += 2 * np.pi
            if dist < dist_obstaculo:
                dist_obstaculo = dist
                angulo_obstaculo = angulo
        
        # Distância até a meta
        dist_meta = np.sqrt((self.x - ambiente.meta['x'])**2 + (self.y - ambiente.meta['y'])**2)
        dx_meta = ambiente.meta['x'] - self.x
        dy_meta = ambiente.meta['y'] - self.y
        angulo_meta = np.arctan2(dy_meta, dx_meta) - self.angulo
        while angulo_meta > np.pi:
            angulo_meta -= 2 * np.pi
        while angulo_meta < -np.pi:
            angulo_meta += 2 * np.pi
        
        return {
            'dist_recurso': dist_recurso,
            'dist_obstaculo': dist_obstaculo,
            'dist_meta': dist_meta,
            'angulo_recurso': angulo_recurso,
            'angulo_obstaculo': angulo_obstaculo,
            'angulo_meta': angulo_meta,
            'energia': self.energia,
            'velocidade': self.velocidade,
            'meta_atingida': self.meta_atingida,
            'x': self.x,  # Novo sensor
            'y': self.y   # Novo sensor
        }

    def verificar_colisao_futura(self, ambiente, x, y, raio, angulo, distancia=25):  # Zona de alerta reduzida
        """Verifica se haverá colisão em uma determinada direção"""
        # Verificar colisão com as bordas
        if x - raio < 0 or x + raio > ambiente.largura or y - raio < 0 or y + raio > ambiente.altura:
            return True
        
        # Verificar colisão com obstáculos
        for obstaculo in ambiente.obstaculos:
            # Calcular a distância até o obstáculo
            centro_x = obstaculo['x'] + obstaculo['largura'] / 2
            centro_y = obstaculo['y'] + obstaculo['altura'] / 2
            dist = np.sqrt((x - centro_x)**2 + (y - centro_y)**2)
            
            # Se estiver muito próximo, verificar colisão
            if dist < distancia:
                # Calcular a distância do ponto até o obstáculo
                dist_x = max(obstaculo['x'] - x, 0, x - (obstaculo['x'] + obstaculo['largura']))
                dist_y = max(obstaculo['y'] - y, 0, y - (obstaculo['y'] + obstaculo['altura']))
                dist_min = np.sqrt(dist_x**2 + dist_y**2)
                
                if dist_min < raio + 5:  # Margem de segurança reduzida
                    return True
        return False

    def encontrar_angulo_seguro(self, ambiente, angulo_objetivo, raio=15):
        """Encontra um ângulo seguro para evitar obstáculos"""
        # Lista de ângulos para testar (em radianos)
        angulos_teste = [
            0,              # Direto
            np.pi/8,        # 22.5° direita
            -np.pi/8,       # 22.5° esquerda
            np.pi/6,        # 30° direita
            -np.pi/6,       # 30° esquerda
            np.pi/4,        # 45° direita
            -np.pi/4,       # 45° esquerda
            np.pi/3,        # 60° direita
            -np.pi/3,       # 60° esquerda
            np.pi/2,        # 90° direita
            -np.pi/2,       # 90° esquerda
            np.pi,          # 180° (voltar)
        ]
        
        # Ordenar ângulos por proximidade do ângulo objetivo
        angulos_teste.sort(key=lambda a: abs((angulo_objetivo + a) % (2*np.pi) - angulo_objetivo))
        
        # Testar cada ângulo
        for angulo in angulos_teste:
            angulo_teste = angulo_objetivo + angulo
            # Normalizar ângulo
            while angulo_teste > np.pi:
                angulo_teste -= 2 * np.pi
            while angulo_teste < -np.pi:
                angulo_teste += 2 * np.pi
            
            # Verificar se o ângulo é seguro
            novo_x = self.x + 50 * np.cos(angulo_teste)
            novo_y = self.y + 50 * np.sin(angulo_teste)
            if not self.verificar_colisao_futura(ambiente, novo_x, novo_y, raio, angulo_teste):
                return angulo_teste
        
        # Se nenhum ângulo funcionar, tentar um ângulo aleatório
        return angulo_objetivo + random.uniform(-np.pi/4, np.pi/4)

    def mover(self, aceleracao, rotacao, ambiente):
        sensores = self.get_sensores(ambiente)
        
        # Atualizar ângulo
        self.angulo += rotacao
        
        # Verificar se o robô está parado
        distancia_movimento = np.sqrt((self.x - self.ultima_posicao[0])**2 + (self.y - self.ultima_posicao[1])**2)
        if distancia_movimento < 0.1:
            self.tempo_parado += 1
            if self.tempo_parado > 2:
                # Forçar movimento aleatório para sair do lugar
                self.angulo += random.choice([-1, 1]) * (np.pi / 2)
                aceleracao = 1.0
                rotacao = 0
        else:
            self.tempo_parado = 0
        
        # Atualizar velocidade
        self.velocidade += aceleracao
        self.velocidade = max(1.0, min(8.0, self.velocidade))
        
        # Calcular nova posição
        novo_x = self.x + self.velocidade * np.cos(self.angulo)
        novo_y = self.y + self.velocidade * np.sin(self.angulo)
        
        # Verificar colisão
        if ambiente.verificar_colisao(novo_x, novo_y, self.raio):
            self.colisoes += 1
            self.velocidade = 1.0
            # Girar ±90° para tentar sair do obstáculo
            self.angulo += random.choice([-1, 1]) * (np.pi / 2)
            # Recalcular objetivo APENAS após colisão
            self.encontrar_proximo_recurso(ambiente)
            aceleracao = 1.0
            rotacao = 0
        else:
            # Verificar colisão futura
            if self.proximo_recurso:
                dx = self.proximo_recurso['x'] - self.x
                dy = self.proximo_recurso['y'] - self.y
                angulo_objetivo = np.arctan2(dy, dx)
                if self.verificar_colisao_futura(ambiente, novo_x, novo_y, self.raio, self.angulo):
                    self.angulo = self.encontrar_angulo_seguro(ambiente, angulo_objetivo)
                    self.velocidade = max(1.0, self.velocidade * 0.9)
            self.distancia_percorrida += np.sqrt((novo_x - self.x)**2 + (novo_y - self.y)**2)
            self.x = novo_x
            self.y = novo_y
        
        self.ultima_posicao = (self.x, self.y)
        
        # Verificar coleta de recursos
        recursos_coletados = ambiente.verificar_coleta_recursos(self.x, self.y, self.raio)
        if recursos_coletados > 0:
            self.recursos_coletados += recursos_coletados
            self.energia = min(100, self.energia + 20 * recursos_coletados)
            for recurso in ambiente.recursos:
                if recurso['coletado'] and (self.ultimo_recurso_coletado is None or 
                    recurso['x'] != self.ultimo_recurso_coletado['x'] or 
                    recurso['y'] != self.ultimo_recurso_coletado['y']):
                    self.ultimo_recurso_coletado = recurso
                    self.proximo_recurso = None
                    # Recalcular objetivo APENAS após coletar
                    self.encontrar_proximo_recurso(ambiente)
                    break
        
        # Verificar se atingiu a meta
        if not self.meta_atingida and ambiente.verificar_atingir_meta(self.x, self.y, self.raio):
            self.meta_atingida = True
            self.energia = min(100, self.energia + 50)
        
        # Consumir energia
        self.energia -= 0.1 + 0.05 * self.velocidade + 0.1 * abs(rotacao)
        self.energia = max(0, self.energia)
        
        return self.energia <= 0

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
    def __init__(self, profundidade=3):
        self.profundidade = profundidade
        self.arvore_aceleracao = self.criar_arvore_aleatoria()
        self.arvore_rotacao = self.criar_arvore_aleatoria()
        self.fitness = 0
    
    def criar_arvore_aleatoria(self):
        if self.profundidade == 0:
            return self.criar_folha()
        
        # OPERADORES DISPONÍVEIS PARA O ALUNO MODIFICAR
        operador = random.choice(['+', '-', '*', '/', 'max', 'min', 'abs', 'if_positivo', 'if_negativo'])
        if operador in ['+', '-', '*', '/']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': IndividuoPG(self.profundidade - 1).arvore_aceleracao
            }
        elif operador in ['max', 'min']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': IndividuoPG(self.profundidade - 1).arvore_aceleracao
            }
        elif operador == 'abs':
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': None
            }
        else:  # if_positivo ou if_negativo
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': IndividuoPG(self.profundidade - 1).arvore_aceleracao
            }
    
    def criar_folha(self):
        # VARIÁVEIS DISPONÍVEIS PARA O ALUNO MODIFICAR
        tipo = random.choice(['constante', 'dist_recurso', 'dist_obstaculo', 'dist_meta', 'angulo_recurso', 'angulo_meta', 'energia', 'velocidade', 'meta_atingida', 'x', 'y'])
        if tipo == 'constante':
            return {
                'tipo': 'folha',
                'valor': random.uniform(-5, 5)  # VALOR ALEATÓRIO PARA O ALUNO MODIFICAR
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
            return 0
            
        if no['tipo'] == 'folha':
            if 'valor' in no:
                return no['valor']
            elif 'variavel' in no:
                return sensores[no['variavel']]
        
        if no['operador'] == 'abs':
            return abs(self.avaliar_no(no['esquerda'], sensores))
        elif no['operador'] == 'if_positivo':
            valor = self.avaliar_no(no['esquerda'], sensores)
            if valor > 0:
                return self.avaliar_no(no['direita'], sensores)
            else:
                return 0
        elif no['operador'] == 'if_negativo':
            valor = self.avaliar_no(no['esquerda'], sensores)
            if valor < 0:
                return self.avaliar_no(no['direita'], sensores)
            else:
                return 0
        
        esquerda = self.avaliar_no(no['esquerda'], sensores)
        direita = self.avaliar_no(no['direita'], sensores) if no['direita'] is not None else 0
        
        if no['operador'] == '+':
            return esquerda + direita
        elif no['operador'] == '-':
            return esquerda - direita
        elif no['operador'] == '*':
            return esquerda * direita
        elif no['operador'] == '/':
            return esquerda / direita if direita != 0 else 0
        elif no['operador'] == 'max':
            return max(esquerda, direita)
        else:  # min
            return min(esquerda, direita)
    
    def mutacao(self, probabilidade=0.3):
        # PROBABILIDADE DE MUTAÇÃO PARA O ALUNO MODIFICAR
        self.mutacao_no(self.arvore_aceleracao, probabilidade)
        self.mutacao_no(self.arvore_rotacao, probabilidade)
    
    def mutacao_no(self, no, probabilidade):
        if random.random() < probabilidade:
            if no['tipo'] == 'folha':
                if 'valor' in no:
                    no['valor'] = random.uniform(0, 10)  # VALOR ALEATÓRIO PARA O ALUNO MODIFICAR
                elif 'variavel' in no:
                    no['variavel'] = random.choice(['dist_recurso', 'dist_obstaculo', 'dist_meta', 'angulo_recurso', 'angulo_meta', 'energia', 'velocidade', 'meta_atingida'])
            else:
                no['operador'] = random.choice(['+', '-', '*', '/', 'max', 'min', 'abs', 'if_positivo', 'if_negativo'])
        
        if no['tipo'] == 'operador':
            self.mutacao_no(no['esquerda'], probabilidade)
            if no['direita'] is not None:
                self.mutacao_no(no['direita'], probabilidade)
    
    def crossover(self, outro):
        novo = IndividuoPG(self.profundidade)
        novo.arvore_aceleracao = self.crossover_subarvore(self.arvore_aceleracao, outro.arvore_aceleracao)
        novo.arvore_rotacao = self.crossover_subarvore(self.arvore_rotacao, outro.arvore_rotacao)
        return novo

    def crossover_subarvore(self, arv1, arv2):
        # Crossover por sub-árvore aleatória
        if random.random() < 0.7:  # 70% de chance de crossover
            # Copiar as árvores para não modificar os pais
            arv1_copia = copy.deepcopy(arv1)
            arv2_copia = copy.deepcopy(arv2)
            # Obter todos os nós possíveis
            nos_arv1 = self.listar_nos(arv1_copia)
            nos_arv2 = self.listar_nos(arv2_copia)
            # Escolher um nó aleatório de cada
            no1 = random.choice(nos_arv1)
            no2 = random.choice(nos_arv2)
            # Trocar sub-árvores
            self.trocar_subarvore(no1, no2)
            return arv1_copia
        else:
            # Sem crossover, retorna cópia de um dos pais
            return copy.deepcopy(random.choice([arv1, arv2]))

    def listar_nos(self, arvore):
        # Retorna uma lista de todos os nós da árvore
        nos = [arvore]
        if arvore.get('tipo') == 'operador':
            nos += self.listar_nos(arvore['esquerda'])
            if arvore['direita'] is not None:
                nos += self.listar_nos(arvore['direita'])
        return nos

    def trocar_subarvore(self, no1, no2):
        # Troca o conteúdo de no1 com no2
        no1.clear()
        no1.update(copy.deepcopy(no2))
    
    def salvar(self, arquivo):
        with open(arquivo, 'w') as f:
            json.dump({
                'arvore_aceleracao': self.arvore_aceleracao,
                'arvore_rotacao': self.arvore_rotacao
            }, f)
    
    @classmethod
    def carregar(cls, arquivo):
        with open(arquivo, 'r') as f:
            dados = json.load(f)
            individuo = cls()
            individuo.arvore_aceleracao = dados['arvore_aceleracao']
            individuo.arvore_rotacao = dados['arvore_rotacao']
            return individuo

class ProgramacaoGenetica:
    def __init__(self, tamanho_populacao=50, profundidade=3):
        # PARÂMETROS PARA O ALUNO MODIFICAR
        self.tamanho_populacao = tamanho_populacao
        self.profundidade = profundidade
        self.populacao = [IndividuoPG(profundidade) for _ in range(tamanho_populacao)]
        self.melhor_individuo = None
        self.melhor_fitness = float('-inf')
        self.historico_fitness = []
    
    def avaliar_populacao(self):
        ambiente = Ambiente()
        robo = Robo(ambiente.largura // 2, ambiente.altura // 2)
        
        for individuo in self.populacao:
            fitness = 0
            
            # Simular 5 tentativas (aumentado)
            for _ in range(5):
                ambiente.reset()
                robo.reset(ambiente.largura // 2, ambiente.altura // 2)
                
                while True:
                    # Obter sensores
                    sensores = robo.get_sensores(ambiente)
                    
                    # Avaliar árvores de decisão
                    aceleracao = individuo.avaliar(sensores, 'aceleracao')
                    rotacao = individuo.avaliar(sensores, 'rotacao')
                    
                    # Limitar valores
                    aceleracao = max(-1, min(1, aceleracao))
                    rotacao = max(-0.5, min(0.5, rotacao))
                    
                    # Mover robô
                    sem_energia = robo.mover(aceleracao, rotacao, ambiente)
                    
                    # Verificar fim da simulação
                    if sem_energia or ambiente.passo():
                        break
                
                # Calcular fitness com nova fórmula
                fitness_tentativa = 0
                
                # 1. Pontos por recursos coletados
                fitness_tentativa += robo.recursos_coletados * 600
                
                # 2. Pontos por atingir a meta
                if robo.meta_atingida:
                    fitness_tentativa += 2000
                
                # 3. Pontos por eficiência energética
                fitness_tentativa += robo.energia * 5
                
                # 4. Pontos por distância percorrida (incentiva movimento)
                fitness_tentativa += robo.distancia_percorrida * 0.2
                
                # 5. Bônus por se aproximar do recurso/meta
                if ambiente.recursos:
                    min_dist_recurso = min([np.sqrt((robo.x - r['x'])**2 + (robo.y - r['y'])**2) for r in ambiente.recursos if not r['coletado']], default=0)
                    fitness_tentativa += max(0, 200 - min_dist_recurso)  # Bônus por se aproximar
                dist_meta = np.sqrt((robo.x - ambiente.meta['x'])**2 + (robo.y - ambiente.meta['y'])**2)
                fitness_tentativa += max(0, 200 - dist_meta)  # Bônus por se aproximar da meta
                
                # 6. Penalidades
                # Penalidade por colisões
                fitness_tentativa -= robo.colisoes * 100
                
                # Penalidade por ficar parado (limitada)
                fitness_tentativa -= min(robo.tempo_parado * 2, 400)  # Penalidade maior
                
                # Penalidade por distância da meta (se não atingiu)
                if not robo.meta_atingida:
                    fitness_tentativa -= min(dist_meta * 0.1, 800)  # Penalidade maior
                
                # Penalidade por tempo de simulação (limitada)
                fitness_tentativa -= min(ambiente.tempo * 0.1, 500)
                
                # Bônus por completar rápido
                if robo.meta_atingida and robo.recursos_coletados == len(ambiente.recursos):
                    tempo_bonus = max(0, 1000 - ambiente.tempo)
                    fitness_tentativa += tempo_bonus * 2
                
                fitness += max(0, fitness_tentativa)
            
            individuo.fitness = fitness / 5  # Média das 5 tentativas
            
            # Atualizar melhor indivíduo
            if individuo.fitness > self.melhor_fitness:
                self.melhor_fitness = individuo.fitness
                self.melhor_individuo = individuo
    
    def selecionar(self):
        # MÉTODO DE SELEÇÃO PARA O ALUNO MODIFICAR
        # Seleção por torneio
        tamanho_torneio = 2  # Reduzido para 2 para mais diversidade
        selecionados = []
        
        for _ in range(self.tamanho_populacao):
            torneio = random.sample(self.populacao, tamanho_torneio)
            vencedor = max(torneio, key=lambda x: x.fitness)
            selecionados.append(vencedor)
        
        return selecionados
    
    def evoluir(self, n_geracoes=50):
        # NÚMERO DE GERAÇÕES PARA O ALUNO MODIFICAR

        for geracao in range(n_geracoes):
            print(f"\nGeração {geracao + 1}/{n_geracoes}")

            # Avaliar população
            self.avaliar_populacao()

            # Registrar métricas
            fitness_geracao = [ind.fitness for ind in self.populacao]
            fitness_medio = sum(fitness_geracao) / len(fitness_geracao)
            pior_fitness = min(fitness_geracao)
            melhor_fitness = self.melhor_fitness

            # Adicionar ao histórico
            self.historico_fitness.append(melhor_fitness)

            # Mostrar na tela
            print(f"Melhor fitness: {melhor_fitness:.2f}")
            print(f"Fitness médio: {fitness_medio:.2f}, Pior fitness: {pior_fitness:.2f}")

            # Escrever no log
            with open("log.txt", "a") as f:
                f.write(f"Geração {geracao + 1}: Melhor={melhor_fitness:.2f}, Médio={fitness_medio:.2f}, Pior={pior_fitness:.2f}\n")

            # Selecionar indivíduos
            selecionados = self.selecionar()

            # Criar nova população
            nova_populacao = []

            # Elitismo - manter o melhor indivíduo
            nova_populacao.append(self.melhor_individuo)

            # Preencher o resto da população
            while len(nova_populacao) < self.tamanho_populacao:
                pai1, pai2 = random.sample(selecionados, 2)
                filho = pai1.crossover(pai2)
                filho.mutacao(probabilidade=0.2)  # Aumentado para 0.2
                nova_populacao.append(filho)

        self.populacao = nova_populacao

        # Após a última geração, gerar gráfico
        plt.plot(self.historico_fitness, label='Melhor Fitness')
        plt.xlabel('Geração')
        plt.ylabel('Fitness')
        plt.title('Evolução do Melhor Fitness')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.savefig('grafico_fitness.png')
        plt.show()

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
    pg = ProgramacaoGenetica(tamanho_populacao=15, profundidade=4)
    melhor_individuo, historico = pg.evoluir(n_geracoes=8)
    
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