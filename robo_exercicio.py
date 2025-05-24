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
        self.ultimo_recurso_coletado = None
        self.proximo_recurso = None
        self.x_anterior = x
        self.y_anterior = y
    
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
            # Se não houver recursos disponíveis, retorna a meta
            return {'x': ambiente.meta['x'], 'y': ambiente.meta['y'], 'coletado': False}
        
        # Calcular distância até cada recurso
        distancias = []
        for recurso in recursos_disponiveis:
            dist = np.sqrt((self.x - recurso['x'])**2 + (self.y - recurso['y'])**2)
            distancias.append((dist, recurso))
        
        # Ordenar por distância
        distancias.sort(key=lambda x: x[0])
        
        # Se não estiver perseguindo nenhum recurso ou se o recurso atual foi coletado
        if self.proximo_recurso is None or self.proximo_recurso['coletado']:
            self.proximo_recurso = distancias[0][1]
            self.tempo_parado_recurso = 0
            return self.proximo_recurso
        
        # Se estiver perseguindo um recurso, verificar se há um mais próximo
        dist_atual = np.sqrt((self.x - self.proximo_recurso['x'])**2 + (self.y - self.proximo_recurso['y'])**2)
        
        # Se houver um recurso significativamente mais próximo (30% mais próximo)
        if distancias[0][0] < dist_atual * 0.7:
            self.proximo_recurso = distancias[0][1]
            self.tempo_parado_recurso = 0
            return self.proximo_recurso
        
        # Se estiver demorando muito para chegar ao recurso atual (mais de 50 passos)
        if self.tempo_parado_recurso > 50:
            self.proximo_recurso = distancias[0][1]
            self.tempo_parado_recurso = 0
            return self.proximo_recurso
        
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
        
        # Calcular ângulo para o próximo objetivo (recurso ou meta)
        if not self.meta_atingida and len([r for r in ambiente.recursos if not r['coletado']]) == 0:
            # Se todos os recursos foram coletados, mirar na meta
            angulo_objetivo = angulo_meta
            dist_objetivo = dist_meta
        else:
            # Caso contrário, mirar no próximo recurso
            angulo_objetivo = angulo_recurso
            dist_objetivo = dist_recurso
        
        return {
            'dist_recurso': dist_recurso,
            'dist_obstaculo': dist_obstaculo,
            'dist_meta': dist_meta,
            'angulo_recurso': angulo_recurso,
            'angulo_obstaculo': angulo_obstaculo,
            'angulo_meta': angulo_meta,
            'angulo_objetivo': angulo_objetivo,  # Novo sensor
            'dist_objetivo': dist_objetivo,      # Novo sensor
            'energia': self.energia,
            'velocidade': self.velocidade,
            'meta_atingida': self.meta_atingida,
            'x': self.x,
            'y': self.y
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
        # Encontrar o recurso mais próximo
        recurso_atual = self.encontrar_proximo_recurso(ambiente)
        self.tempo_parado_recurso += 1
        
        # Calcular ângulo para o objetivo em radianos
        angulo_objetivo = np.arctan2(recurso_atual['y'] - self.y, recurso_atual['x'] - self.x)
        diferenca_angulo = (angulo_objetivo - self.angulo) % (2 * np.pi)
        
        # Normalizar diferença de ângulo para [-pi, pi]
        if diferenca_angulo > np.pi:
            diferenca_angulo -= 2 * np.pi
        
        # Ajustar rotação para alinhar com o objetivo
        rotacao_base = np.clip(diferenca_angulo / (np.pi/2), -1.0, 1.0)
        # Aumentar o peso da rotação base para curvas mais precisas
        rotacao = (rotacao_base * 0.95 + rotacao * 0.05)  # Aumentado peso da rotação base
        
        # Atualizar ângulo com rotação mais rápida e suave
        self.angulo = (self.angulo + rotacao * 0.4) % (2 * np.pi)  # Aumentado de 0.3 para 0.4
        
        # Atualizar velocidade com aceleração mais agressiva e velocidade máxima maior
        # Força aceleração positiva se estiver parado ou muito lento
        if self.velocidade < 5.0:
            aceleracao = max(aceleracao, 0.8)
        
        # Reduzir velocidade apenas em curvas muito fechadas
        if abs(diferenca_angulo) > np.pi/2:  # 90 graus
            self.velocidade = max(self.velocidade * 0.9, 5.0)  # Reduz 10% mas mantém mínimo de 5.0
        
        self.velocidade = np.clip(self.velocidade + aceleracao * 1.5, 0, 15)  # aceleração 1.5, max 15
        
        # Calcular nova posição usando radianos
        novo_x = self.x + self.velocidade * np.cos(self.angulo)
        novo_y = self.y + self.velocidade * np.sin(self.angulo)
        
        # Verificar colisão antes de atualizar posição
        if not ambiente.verificar_colisao(novo_x, novo_y, self.raio):
            self.x = novo_x
            self.y = novo_y
            self.distancia_percorrida += self.velocidade
        else:
            self.colisoes += 1
            self.velocidade *= 0.8  # Reduz menos a velocidade após colisão
            # Tenta encontrar um ângulo seguro
            angulos_teste = [np.pi/2, -np.pi/2, np.pi*3/4, -np.pi*3/4, np.pi, random.uniform(-np.pi, np.pi)]
            escape = False
            for delta in angulos_teste:
                angulo_teste = (self.angulo + delta) % (2 * np.pi)
                teste_x = self.x + max(self.velocidade, 5.0) * np.cos(angulo_teste)  # velocidade mínima ao escapar
                teste_y = self.y + max(self.velocidade, 5.0) * np.sin(angulo_teste)
                if not ambiente.verificar_colisao(teste_x, teste_y, self.raio):
                    self.angulo = angulo_teste
                    self.x = teste_x
                    self.y = teste_y
                    self.velocidade = max(self.velocidade, 5.0)  # garante velocidade mínima
                    escape = True
                    break
            if not escape:
                # Se não conseguir escapar, tenta dar ré
                back_x = self.x - max(self.velocidade, 5.0) * np.cos(self.angulo)
                back_y = self.y - max(self.velocidade, 5.0) * np.sin(self.angulo)
                if not ambiente.verificar_colisao(back_x, back_y, self.raio):
                    self.x = back_x
                    self.y = back_y
                    self.velocidade = max(self.velocidade, 5.0)
                # Se ainda não conseguir, gira aleatoriamente
                self.angulo = (self.angulo + random.uniform(-np.pi, np.pi)) % (2 * np.pi)
        
        # Verificar coleta de recursos
        for recurso in ambiente.recursos:
            if not recurso['coletado']:
                if self.coletar_recurso(recurso):
                    self.energia = min(100, self.energia + 20)
        
        # Verificar se todos os recursos foram coletados e se a meta foi atingida
        if all(recurso['coletado'] for recurso in ambiente.recursos):
            if ambiente.verificar_atingir_meta(self.x, self.y, self.raio):
                self.meta_atingida = True
                self.velocidade = 0  # Para o robô
                return True  # Retorna True para indicar que a meta foi atingida
        
        # Consumir energia proporcional à velocidade e rotação
        self.energia -= (self.velocidade * 0.1 + abs(rotacao) * 0.05)
        
        # Verificar se ficou sem energia
        if self.energia <= 0:
            return True
        
        # Atualizar tempo parado
        if self.ultima_posicao:
            dist = np.sqrt((self.x - self.ultima_posicao[0])**2 + (self.y - self.ultima_posicao[1])**2)
            if dist < 0.1:
                self.tempo_parado += 1
                # Se ficar parado por muito tempo, força um movimento
                if self.tempo_parado > 5:
                    self.velocidade = 5.0  # aumenta velocidade ao sair do parado
                    self.angulo = (self.angulo + random.uniform(-0.3, 0.3)) % (2 * np.pi)
            else:
                self.tempo_parado = 0
        
        self.ultima_posicao = (self.x, self.y)
        return False

    def calcular_angulo(self, objetivo):
        """Calcula o ângulo entre o robô e o objetivo em graus"""
        dx = objetivo['x'] - self.x
        dy = objetivo['y'] - self.y
        angulo = np.degrees(np.arctan2(dy, dx))
        return angulo
    
    def calcular_distancia(self, objetivo):
        """Calcula a distância entre o robô e o objetivo"""
        return np.sqrt((self.x - objetivo['x'])**2 + (self.y - objetivo['y'])**2)
    
    def coletar_recurso(self, recurso):
        """Verifica se o robô está próximo o suficiente para coletar um recurso"""
        if not recurso['coletado']:
            distancia = np.sqrt((self.x - recurso['x'])**2 + (self.y - recurso['y'])**2)
            if distancia < self.raio + 10:  # 10 é o raio do recurso
                recurso['coletado'] = True
                self.recursos_coletados += 1
                self.energia = min(100, self.energia + 20)  # Recupera energia ao coletar
                return True
        return False

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
        
        # Operadores simplificados focados em navegação
        operador = random.choice(['+', '-', '*', 'if_positivo'])
        
        if operador in ['+', '-', '*']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': IndividuoPG(self.profundidade - 1).arvore_aceleracao
            }
        else:  # if_positivo
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': IndividuoPG(self.profundidade - 1).arvore_aceleracao
            }
    
    def criar_folha(self):
        # Variáveis focadas em navegação
        tipo = random.choice([
            'constante',
            'angulo_objetivo',  # Ângulo para o objetivo
            'dist_objetivo',    # Distância para o objetivo
            'dist_obstaculo',   # Distância para o obstáculo mais próximo
            'energia'           # Energia restante
        ])
        
        if tipo == 'constante':
            return {
                'tipo': 'folha',
                'valor': random.uniform(-1, 1)  # Range reduzido para movimentos mais suaves
            }
        else:
            return {
                'tipo': 'folha',
                'variavel': tipo
            }
    
    def avaliar(self, sensores, tipo='aceleracao'):
        arvore = self.arvore_aceleracao if tipo == 'aceleracao' else self.arvore_rotacao
        valor = self.avaliar_no(arvore, sensores)
        
        # Ajustes específicos para cada tipo de controle
        if tipo == 'aceleracao':
            # Aceleração mais suave
            return max(-1, min(1, valor))
        else:  # rotacao
            # Rotação mais suave
            return max(-0.5, min(0.5, valor))
    
    def avaliar_no(self, no, sensores):
        if no is None:
            return 0
            
        if no['tipo'] == 'folha':
            if 'valor' in no:
                return no['valor']
            elif 'variavel' in no:
                if no['variavel'] == 'constante':
                    return random.uniform(-1, 1)
                return sensores[no['variavel']]
        
        if no['operador'] == 'if_positivo':
            valor = self.avaliar_no(no['esquerda'], sensores)
            if valor > 0:
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
        return 0
    
    def mutacao(self, probabilidade=0.3):
        self.mutacao_no(self.arvore_aceleracao, probabilidade)
        self.mutacao_no(self.arvore_rotacao, probabilidade)
    
    def mutacao_no(self, no, probabilidade):
        if random.random() < probabilidade:
            if no['tipo'] == 'folha':
                if 'valor' in no:
                    no['valor'] = random.uniform(-1, 1)
                elif 'variavel' in no:
                    no['variavel'] = random.choice(['dist_recurso', 'dist_obstaculo', 'energia', 'velocidade'])
            else:
                no['operador'] = random.choice(['+', '-', '*', 'if_positivo'])
        
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
            melhor_fitness = float('-inf')
            
            for _ in range(2):  # Reduzido para 2 tentativas para melhor performance
                # Resetar ambiente
                ambiente.reset()
                robo.reset(ambiente.largura // 2, ambiente.altura // 2)
                recursos = ambiente.recursos.copy()
                objetivo = ambiente.meta
                
                # Variáveis para controle de progresso
                ultima_dist_objetivo = float('inf')
                tempo_sem_progresso = 0
                ultima_posicao = None
                tempo_parado = 0
                recursos_iniciais = len(recursos)
                #fitness_base = 10000  # Aumentado significativamente
                
                # Limitar número de passos
                max_passos = 150
                passos = 0
                
                while passos < max_passos and len(recursos) > 0:
                    # Atualizar sensores
                    sensores = robo.get_sensores(ambiente)
                    
                    # Calcular aceleração e rotação
                    aceleracao = individuo.avaliar(sensores, 'aceleracao')
                    rotacao = individuo.avaliar(sensores, 'rotacao')
                    
                    # Mover robô
                    sem_energia = robo.mover(aceleracao, rotacao, ambiente)
                    
                    # Verificar colisão
                    if ambiente.verificar_colisao(robo.x, robo.y, robo.raio):
                        break
                    
                    # Verificar coleta de recursos
                    recursos_coletados = ambiente.verificar_coleta_recursos(robo.x, robo.y, robo.raio)
                    if recursos_coletados > 0:
                        robo.recursos_coletados += recursos_coletados
                        recursos = [r for r in recursos if not r['coletado']]
                    
                    # Verificar progresso
                    dist_atual = np.sqrt((robo.x - objetivo['x'])**2 + (robo.y - objetivo['y'])**2)
                    if dist_atual < ultima_dist_objetivo:
                        ultima_dist_objetivo = dist_atual
                        tempo_sem_progresso = 0
                    else:
                        tempo_sem_progresso += 1
                    
                    # Verificar se está parado
                    if ultima_posicao and np.sqrt((robo.x - ultima_posicao[0])**2 + (robo.y - ultima_posicao[1])**2) < 0.1:
                        tempo_parado += 1
                    else:
                        tempo_parado = 0
                    ultima_posicao = (robo.x, robo.y)
                    
                    # Parar se ficar muito tempo sem progresso ou parado
                    if tempo_sem_progresso > 20 or tempo_parado > 10:
                        break
                    
                    passos += 1
                
                # Calcular fitness
                #fitness = fitness_base
                fitness = 0

                # Pontuação positiva
                fitness += robo.recursos_coletados * 7500
                if robo.recursos_coletados == recursos_iniciais:
                    fitness += 15000  # Bônus por coletar todos os recursos

                if ambiente.verificar_atingir_meta(robo.x, robo.y, robo.raio):
                    fitness += 20000  # Bônus por atingir a meta

                fitness += robo.energia * 80  # Energia como fator proporcional
                fitness += robo.passos * 10  # 10 pontos por frame onde o robô se move

                # Penalizações (reduzidas)
                fitness -= robo.colisoes * 500
                fitness -= tempo_parado * 25
                fitness -= tempo_sem_progresso * 50
                fitness -= (recursos_iniciais - robo.recursos_coletados) * 1500

                # Penalizar distância até a meta (se não atingiu)
                if not ambiente.verificar_atingir_meta(robo.x, robo.y, robo.raio):
                    dist_final = np.sqrt((robo.x - objetivo['x'])**2 + (robo.y - objetivo['y'])**2)
                    fitness -= dist_final * 5

                # Garantir que o fitness não seja negativo
                fitness = max(fitness, 0)

                melhor_fitness = max(melhor_fitness, fitness)
                
                individuo.fitness = melhor_fitness
            
            # Atualizar melhor indivíduo
            if individuo.fitness > self.melhor_fitness:
                self.melhor_fitness = individuo.fitness
                self.melhor_individuo = copy.deepcopy(individuo)
    
    def selecionar(self):
        # MÉTODO DE SELEÇÃO PARA O ALUNO MODIFICAR
        # Seleção por torneio
        tamanho_torneio = 3  # Aumentado para 3 para melhor seleção
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

            # Elitismo - manter os 2 melhores indivíduos
            melhores = sorted(self.populacao, key=lambda x: x.fitness, reverse=True)[:2]
            nova_populacao.extend(melhores)

            # Preencher o resto da população
            while len(nova_populacao) < self.tamanho_populacao:
                pai1, pai2 = random.sample(selecionados, 2)
                filho = pai1.crossover(pai2)
                filho.mutacao(probabilidade=0.15)  # Reduzido para 0.15 para menos mutações
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
    pg = ProgramacaoGenetica(tamanho_populacao=30, profundidade=2)  # Reduzido população e profundidade
    melhor_individuo, historico = pg.evoluir(n_geracoes=50)  # Aumentado número de gerações
    
    # Salvar o melhor indivíduo
    print("Salvando o melhor indivíduo...")
    melhor_individuo.salvar('melhor_robo.json')
    
    # Plotar evolução do fitness
    print("Plotando evolução do fitness...")
    plt.figure(figsize=(10, 6))  # Aumentado tamanho da figura
    plt.plot(historico)
    plt.title('Evolução do Fitness')
    plt.xlabel('Geracao')
    plt.ylabel('Fitness')
    plt.grid(True)  # Adicionado grid
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

        # Gerar gráficos adicionais com base nos dados do log
    print("Gerando gráficos adicionais...")

    import re

    # Lê o log e extrai os dados
    geracoes, melhores, medios, piores = [], [], [], []
    with open("log.txt", "r", encoding="latin-1") as f:
        for linha in f:
            match = re.search(r"Geração (\d+): Melhor=([-+]?[0-9]*\.?[0-9]+), Médio=([-+]?[0-9]*\.?[0-9]+), Pior=([-+]?[0-9]*\.?[0-9]+)", linha)
            if match:
                geracoes.append(int(match.group(1)))
                melhores.append(float(match.group(2)))
                medios.append(float(match.group(3)))
                piores.append(float(match.group(4)))

    # Gráfico de linha: Diferença entre melhor e pior
    diferencas = np.array(melhores) - np.array(piores)
    plt.figure(figsize=(10, 5))
    plt.plot(geracoes, diferencas, color='#FFA500', label='Diferença Melhor - Pior')  # Laranja
    plt.title('Diferença entre Melhor e Pior Fitness por Geração')
    plt.xlabel('Geração')
    plt.ylabel('Diferença de Fitness')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('diferenca_melhor_pior.png')
    plt.close()

    # Boxplot dos valores de fitness
    df = pd.DataFrame({
        'Melhor': melhores,
        'Médio': medios,
        'Pior': piores
    })
    plt.figure(figsize=(10, 6))
    df.boxplot()
    plt.title("Boxplot dos Valores de Fitness")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('boxplot_fitness.png')
    plt.close()

    # Histograma dos fitness médios
    plt.figure(figsize=(10, 6))
    plt.hist(medios, bins=20, color='skyblue', edgecolor='black')
    plt.title("Histograma dos Valores Médios de Fitness")
    plt.xlabel("Fitness Médio")
    plt.ylabel("Frequência")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('histograma_fitness_medio.png')
    plt.close()

    print("Gráficos salvos: 'diferenca_melhor_pior.png', 'boxplot_fitness.png', 'histograma_fitness_medio.png'")
