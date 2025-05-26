import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import json

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
		self.max_tempo = 1000 # Tempo máximo de simulação
		self.meta = self.gerar_meta() # Adicionando a meta
		self.meta_atingida = False # Flag para controlar se a meta foi atingida

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
		max_tentativas = 100 # Número máximo de tentativas para encontrar posição válida

		for _ in range(num_recursos):
			tentativas = 0
			posicao_valida = False

			while not posicao_valida and tentativas < max_tentativas:
				x = random.randint(20, self.largura - 20)
				y = random.randint(20, self.altura - 20)

				# Verificar se a posição está dentro de algum obstáculo
				posicao_valida = True
				for obstaculo in self.obstaculos:
					if (x > obstaculo['x'] and 
						x < obstaculo['x'] + obstaculo['largura'] and
						y > obstaculo['y'] and 
						y < obstaculo['y'] + obstaculo['altura']):
						posicao_valida = False
						break

				tentativas += 1

			# Se encontrou posição válida, adiciona o recurso
			if posicao_valida:
				recursos.append({
					'x': x,
					'y': y,
					'coletado': False
				})
			else:
				# Se não encontrou posição válida, coloca em uma posição segura
				x = self.largura // 2
				y = self.altura // 2
				recursos.append({
					'x': x,
					'y': y,
					'coletado': False
				})

		return recursos

	def gerar_meta(self):
		# Gerar a meta em uma posição segura, longe dos obstáculos
		max_tentativas = 100
		margem = 50 # Margem das bordas

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

				if dist < 50: # 50 pixels de margem extra
					posicao_segura = False
					break

			if posicao_segura:
				return {
					'x': x,
					'y': y,
					'raio': 30 # Raio da meta
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
				if distancia < raio + 10: # 10 é o raio do recurso
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
		margem = 50 # Margem das bordas

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

				if dist < raio_robo + 20: # 20 pixels de margem extra
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
		self.angulo = 0 # em radianos
		self.velocidade = 0
		self.energia = 100
		self.recursos_coletados = 0
		self.colisoes = 0
		self.distancia_percorrida = 0
		self.tempo_parado = 0 # Novo: contador de tempo parado
		self.ultima_posicao = (x, y) # Novo: última posição conhecida
		self.meta_atingida = False # Novo: flag para controlar se a meta foi atingida

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
		if distancia_movimento < 0.1: # Se moveu menos de 0.1 unidades
			self.tempo_parado += 1
			# Forçar movimento após ficar parado por muito tempo
			if self.tempo_parado > 5: # Após 5 passos parado
				aceleracao = max(0.2, aceleracao) # Força aceleração mínima
				rotacao = random.uniform(-0.2, 0.2) # Pequena rotação aleatória
		else:
			self.tempo_parado = 0

		# Atualizar velocidade
		self.velocidade += aceleracao
		self.velocidade = max(0.1, min(5, self.velocidade)) # Velocidade mínima de 0.1

		# Calcular nova posição
		novo_x = self.x + self.velocidade * np.cos(self.angulo)
		novo_y = self.y + self.velocidade * np.sin(self.angulo)

		# Verificar colisão
		if ambiente.verificar_colisao(novo_x, novo_y, self.raio):
			self.colisoes += 1
			self.velocidade = 0.1 # Mantém velocidade mínima mesmo após colisão
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

		plt.style.use('default') # Usar estilo padrão
		plt.ion() # Modo interativo
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
				facecolor='#FF9999', # Vermelho claro
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
					facecolor='#99FF99', # Verde claro
					alpha=0.8
				)
				self.ax.add_patch(circ)

		# Desenhar a meta
		meta_circ = patches.Circle(
			(self.ambiente.meta['x'], self.ambiente.meta['y']),
			self.ambiente.meta['raio'],
			linewidth=2,
			edgecolor='black',
			facecolor='#FFFF00', # Amarelo
			alpha=0.8
		)
		self.ax.add_patch(meta_circ)

		# Criar objetos para o robô e direção (serão atualizados)
		robo_circ = patches.Circle(
			(self.robo.x, self.robo.y),
			self.robo.raio,
			linewidth=1,
			edgecolor='black',
			facecolor='#9999FF', # Azul claro
			alpha=0.8
		)
		self.ax.add_patch(robo_circ)

		# Criar texto para informações
		info_text = self.ax.text(
			10, self.ambiente.altura - 50, # Alterado de 10 para 50 para descer a legenda
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
					facecolor='#FFFF00', # Amarelo
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
					10, self.ambiente.altura - 50, # Alterado de 10 para 50 para descer a legenda
					f"Tempo: {self.ambiente.tempo}\n"
					f"Recursos: {self.robo.recursos_coletados}/{len(ambiente.recursos)}\n"
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
			repeat=True # Permitir que a animação repita
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
		self.max_tamanho_arvore = 50 # Limite máximo de nós por árvore
		self.arvore_aceleracao = None
		self.arvore_rotacao = None
		self.fitness = 0
		# Inicializar as árvores
		self.arvore_aceleracao = self.criar_arvore_aleatoria('aceleracao', profundidade)
		self.arvore_rotacao = self.criar_arvore_aleatoria('rotacao', profundidade)

	def criar_arvore_aleatoria(self, tipo='aceleracao', profundidade_atual=None):
		if profundidade_atual is None:
			profundidade_atual = self.profundidade

		# Se atingiu profundidade máxima ou tamanho máximo, retorna uma folha
		if profundidade_atual <= 0:
			return self.criar_folha()

		# Verificar tamanho atual da árvore
		arvore_atual = self.arvore_aceleracao if tipo == 'aceleracao' else self.arvore_rotacao
		tamanho_atual = self.calcular_tamanho_arvore(arvore_atual) if arvore_atual is not None else 0
		if tamanho_atual >= self.max_tamanho_arvore:
			return self.criar_folha()

		# OPERADORES DISPONÍVEIS PARA O ALUNO MODIFICAR
		operador = random.choice(['+', '-', '*', '/', 'max', 'min', 'abs', 'if_positivo', 'if_negativo', 'sin', 'cos'])

		# Operadores binários
		if operador in ['+', '-', '*', '/', 'max', 'min']:
			return {
				'tipo': 'operador',
				'operador': operador,
				'esquerda': self.criar_arvore_aleatoria(tipo, profundidade_atual - 1),
				'direita': self.criar_arvore_aleatoria(tipo, profundidade_atual - 1)
			}
		# Operadores unários
		elif operador in ['abs', 'sin', 'cos']:
			return {
				'tipo': 'operador',
				'operador': operador,
				'esquerda': self.criar_arvore_aleatoria(tipo, profundidade_atual - 1),
				'direita': None
			}
		# Operadores condicionais
		else: # if_positivo ou if_negativo
			return {
				'tipo': 'operador',
				'operador': operador,
				'esquerda': self.criar_arvore_aleatoria(tipo, profundidade_atual - 1),
				'direita': self.criar_arvore_aleatoria(tipo, profundidade_atual - 1)
			}

	def calcular_tamanho_arvore(self, no):
		if no is None:
			return 0

		# Versão iterativa usando uma pilha
		pilha = [no]
		tamanho = 0

		while pilha:
			no_atual = pilha.pop()
			tamanho += 1

			if no_atual['tipo'] == 'operador':
				if no_atual['esquerda'] is not None:
					pilha.append(no_atual['esquerda'])
				if no_atual['direita'] is not None:
					pilha.append(no_atual['direita'])

		return tamanho

	def criar_folha(self):
		# Aumentar a probabilidade de escolher sensores de recurso e obstáculo
		opcoes = [
			('dist_recurso', 0.2),  # 20% de chance
			('angulo_recurso', 0.2), # 20% de chance
			('dist_obstaculo', 0.2), # 20% de chance
			('dist_meta', 0.08),
			('angulo_meta', 0.08),
			('energia', 0.08),
			('velocidade', 0.08),
			('meta_atingida', 0.08),
			('constante', 0.08)
		]
		
		# Selecionar com base nas probabilidades
		tipos, probabilidades = zip(*opcoes)
		tipo_escolhido = random.choices(tipos, weights=probabilidades, k=1)[0]

		if tipo_escolhido == 'constante':
			# Constantes mais significativas para o problema
			return {
				'tipo': 'folha',
				'valor': random.choice([-1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 5.0, 10.0])
			}
		else:
			return {
				'tipo': 'folha',
				'variavel': tipo_escolhido
			}

	def avaliar(self, sensores, tipo='aceleracao'):
		arvore = self.arvore_aceleracao if tipo == 'aceleracao' else self.arvore_rotacao
		return self.avaliar_no(arvore, sensores)

	def avaliar_no(self, no, sensores):
		if no is None:
			return 0

		# Versão iterativa usando pilha
		pilha = [no]
		resultados = {} # Dicionário para armazenar resultados intermediários

		while pilha:
			no_atual = pilha.pop()

			# Se já temos o resultado, use-o
			if id(no_atual) in resultados:
				continue

			# Se é uma folha, calcule o resultado
			if no_atual['tipo'] == 'folha':
				if 'valor' in no_atual:
					resultados[id(no_atual)] = no_atual['valor']
				elif 'variavel' in no_atual:
					resultados[id(no_atual)] = sensores[no_atual['variavel']]
				continue

			# Se é um operador, verifique se temos os resultados dos filhos
			if no_atual['tipo'] == 'operador':
				# Operadores unários
				if no_atual['operador'] in ['abs', 'sin', 'cos']:
					if no_atual['esquerda'] is None:
						resultados[id(no_atual)] = 0
						continue

					if id(no_atual['esquerda']) not in resultados:
						pilha.append(no_atual)
						pilha.append(no_atual['esquerda'])
						continue

					valor = resultados[id(no_atual['esquerda'])]
					if not np.isfinite(valor):
						valor = 0

					if no_atual['operador'] == 'abs':
						resultados[id(no_atual)] = abs(valor)
					elif no_atual['operador'] == 'sin':
						resultados[id(no_atual)] = np.sin(valor) if np.isfinite(valor) else 0
					else: # cos
						resultados[id(no_atual)] = np.cos(valor) if np.isfinite(valor) else 0
					continue

				# Operadores condicionais
				elif no_atual['operador'] in ['if_positivo', 'if_negativo']:
					if no_atual['esquerda'] is None or no_atual['direita'] is None:
						resultados[id(no_atual)] = 0
						continue

					if id(no_atual['esquerda']) not in resultados:
						pilha.append(no_atual)
						pilha.append(no_atual['esquerda'])
						continue

					if id(no_atual['direita']) not in resultados:
						pilha.append(no_atual)
						pilha.append(no_atual['direita'])
						continue

					valor = resultados[id(no_atual['esquerda'])]
					if no_atual['operador'] == 'if_positivo':
						resultados[id(no_atual)] = resultados[id(no_atual['direita'])] if valor > 0 else 0
					else: # if_negativo
						resultados[id(no_atual)] = resultados[id(no_atual['direita'])] if valor < 0 else 0
					continue

				# Operadores binários
				else:
					if no_atual['esquerda'] is None or no_atual['direita'] is None:
						resultados[id(no_atual)] = 0
						continue

					if id(no_atual['esquerda']) not in resultados:
						pilha.append(no_atual)
						pilha.append(no_atual['esquerda'])
						continue

					if id(no_atual['direita']) not in resultados:
						pilha.append(no_atual)
						pilha.append(no_atual['direita'])
						continue

					esquerda = resultados[id(no_atual['esquerda'])]
					direita = resultados[id(no_atual['direita'])]

					# Proteção contra valores inválidos
					if not np.isfinite(esquerda):
						esquerda = 0
					if not np.isfinite(direita):
						direita = 0

					if no_atual['operador'] == '+':
						resultados[id(no_atual)] = esquerda + direita
					elif no_atual['operador'] == '-':
						resultados[id(no_atual)] = esquerda - direita
					elif no_atual['operador'] == '*':
						resultados[id(no_atual)] = esquerda * direita
					elif no_atual['operador'] == '/':
						resultados[id(no_atual)] = esquerda / direita if abs(direita) > 1e-10 else 0
					elif no_atual['operador'] == 'max':
						resultados[id(no_atual)] = max(esquerda, direita)
					else: # min
						resultados[id(no_atual)] = min(esquerda, direita)

		return resultados.get(id(no), 0) # Retorna 0 se o nó não estiver nos resultados

	def mutacao(self, probabilidade=0.1):
		# PROBABILIDADE DE MUTAÇÃO PARA O ALUNO MODIFICAR
		self.mutacao_no(self.arvore_aceleracao, probabilidade)
		self.mutacao_no(self.arvore_rotacao, probabilidade)

	def mutacao_no(self, no, probabilidade):
		# Versão iterativa usando uma pilha
		pilha = [no]

		while pilha:
			no_atual = pilha.pop()

			if random.random() < probabilidade:
				if no_atual['tipo'] == 'folha':
					if 'valor' in no_atual:
						# Mutação mais suave para constantes
						novo_valor = no_atual['valor'] * random.uniform(0.8, 1.2)
						# Limitar valores extremos
						no_atual['valor'] = max(-10, min(10, novo_valor))
					elif 'variavel' in no_atual:
						no_atual['variavel'] = random.choice(['dist_recurso', 'dist_obstaculo', 'dist_meta', 
							'angulo_recurso', 'angulo_meta', 'energia', 
							'velocidade', 'meta_atingida'])
				else:
					# Mutação mais inteligente para operadores
					if no_atual['operador'] in ['+', '-', '*', '/']:
						no_atual['operador'] = random.choice(['+', '-', '*', '/'])
					elif no_atual['operador'] in ['max', 'min']:
						no_atual['operador'] = random.choice(['max', 'min'])
					elif no_atual['operador'] in ['abs', 'sin', 'cos']:
						no_atual['operador'] = random.choice(['abs', 'sin', 'cos'])
					else: # if_positivo ou if_negativo
						no_atual['operador'] = random.choice(['if_positivo', 'if_negativo'])

			if no_atual['tipo'] == 'operador':
				if no_atual['esquerda'] is not None:
					pilha.append(no_atual['esquerda'])
				if no_atual['direita'] is not None:
					pilha.append(no_atual['direita'])

	def crossover(self, outro):
		novo = IndividuoPG(self.profundidade)
		novo.arvore_aceleracao = self.crossover_no(self.arvore_aceleracao, outro.arvore_aceleracao)
		novo.arvore_rotacao = self.crossover_no(self.arvore_rotacao, outro.arvore_rotacao)
		return novo

	def crossover_no(self, no1, no2):
		# Probabilidade de crossover aumenta com a profundidade
		profundidade_atual = self.calcular_profundidade(no1)
		probabilidade = 0.7 - (0.1 * profundidade_atual) # Diminui a probabilidade com a profundidade

		if random.random() < probabilidade:
			# Escolhe um ponto de crossover aleatório em cada árvore
			ponto1 = self.encontrar_ponto_crossover(no1)
			ponto2 = self.encontrar_ponto_crossover(no2)

			# Realiza o crossover
			if random.random() < 0.5:
				# Troca os nós filhos
				ponto1['esquerda'], ponto2['esquerda'] = ponto2['esquerda'].copy(), ponto1['esquerda'].copy()
				if ponto1['direita'] is not None and ponto2['direita'] is not None:
					ponto1['direita'], ponto2['direita'] = ponto2['direita'].copy(), ponto1['direita'].copy()
			else:
				# Troca os operadores mantendo a estrutura
				if ponto1['tipo'] == 'operador' and ponto2['tipo'] == 'operador':
					ponto1['operador'], ponto2['operador'] = ponto2['operador'], ponto1['operador']

			return no1.copy()
		else:
			# Mantém a árvore original
			return no1.copy()

	def calcular_profundidade(self, no):
		if no is None:
			return 0

		# Versão iterativa usando uma pilha
		pilha = [(no, 1)] # (nó, profundidade_atual)
		profundidade_maxima = 0

		while pilha:
			no_atual, profundidade = pilha.pop()
			profundidade_maxima = max(profundidade_maxima, profundidade)

			if no_atual['tipo'] == 'operador':
				if no_atual['esquerda'] is not None:
					pilha.append((no_atual['esquerda'], profundidade + 1))
				if no_atual['direita'] is not None:
					pilha.append((no_atual['direita'], profundidade + 1))

		return profundidade_maxima

	def encontrar_ponto_crossover(self, no):
		# Encontra um nó aleatório na árvore para fazer o crossover
		if no['tipo'] == 'folha':
			return no

		# Lista de nós candidatos para crossover
		nos_candidatos = []
		self.coletar_nos_candidatos(no, nos_candidatos)

		# Se não houver candidatos, retorna o nó raiz
		if not nos_candidatos:
			return no

		# Escolhe um nó aleatório da lista
		return random.choice(nos_candidatos)

	def coletar_nos_candidatos(self, no, nos_candidatos):
		# Versão iterativa usando uma pilha
		pilha = [no]

		while pilha:
			no_atual = pilha.pop()

			if no_atual['tipo'] == 'operador':
				nos_candidatos.append(no_atual)
				if no_atual['esquerda'] is not None:
					pilha.append(no_atual['esquerda'])
				if no_atual['direita'] is not None:
					pilha.append(no_atual['direita'])

	def copy(self):
		"""Cria uma cópia profunda do indivíduo"""
		novo = IndividuoPG(self.profundidade)
		novo.arvore_aceleracao = self.copiar_arvore(self.arvore_aceleracao)
		novo.arvore_rotacao = self.copiar_arvore(self.arvore_rotacao)
		novo.fitness = self.fitness
		return novo

	def copiar_arvore(self, no):
		"""Cria uma cópia profunda de uma árvore"""
		if no is None:
			return None

		copia = no.copy()
		if copia['tipo'] == 'operador':
			if copia['esquerda'] is not None:
				copia['esquerda'] = self.copiar_arvore(copia['esquerda'])
			if copia['direita'] is not None:
				copia['direita'] = self.copiar_arvore(copia['direita'])
		return copia

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
		self.historico_media_fitness = []  # Novo: histórico da média do fitness
		self.geracoes_sem_melhoria = 0
		self.max_geracoes_sem_melhoria = 15  # Aumentado para dar mais tempo de evolução
		self.ultimo_fitness = float('-inf')
		self.melhorias_minimas = 0.005  # Reduzido para ser mais tolerante a pequenas melhorias

	def avaliar_populacao(self):
		ambiente = Ambiente()
		robo = Robo(ambiente.largura // 2, ambiente.altura // 2)
		recursos_ambiente = len(ambiente.recursos.copy())

		for individuo in self.populacao:
			try:
				ambiente.reset()
				robo.reset(ambiente.largura // 2, ambiente.altura // 2)
				ultima_posicao = (robo.x, robo.y)
				tempo_parado = 0
				distancia_total = 0

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

					# Calcular distância percorrida
					distancia = np.sqrt((robo.x - ultima_posicao[0])**2 + (robo.y - ultima_posicao[1])**2)
					distancia_total += distancia
					ultima_posicao = (robo.x, robo.y)

					# Verificar se está parado
					if distancia < 0.1:
						tempo_parado += 1
					else:
						tempo_parado = 0

					# Verificar fim da simulação
					if sem_energia or ambiente.passo():
						break

				# Bônus por recursos coletados (prioridade máxima)
				recursos_coletados = robo.recursos_coletados

				# Bônus base por recursos (progressivo)
				bonus_recursos = recursos_coletados * 100 # Reduzido de 500 para 100
				# Bônus extra por progresso na coleta
				if recursos_coletados > 0:
					bonus_recursos += recursos_coletados * 50 * (recursos_coletados / recursos_ambiente) # Reduzido de 300 para 50

				# Penalidade por ir para a meta sem coletar todos os recursos
				penalidade_meta_prematura = 0
				if robo.meta_atingida and recursos_coletados < recursos_ambiente:
					penalidade_meta_prematura = 1000 # Reduzido de 5000 para 1000
					# Penalidade adicional baseada na quantidade de recursos faltando
					recursos_faltando = recursos_ambiente - recursos_coletados
					penalidade_meta_prematura += recursos_faltando * 200 # Reduzido de 1000 para 200

				# Penalidades básicas
				penalidade_colisoes = robo.colisoes * 100  # Reduzido de 500 para 100
				penalidade_energia = (100 - robo.energia) * 0.5  # Reduzido de 2 para 0.5
				
				# Novas penalidades e recompensas
				penalidade_tempo_parado = tempo_parado * 10  # Reduzido de 50 para 10
				penalidade_movimento_irregular = abs(robo.velocidade - 2.0) * 20  # Reduzido de 100 para 20
				recompensa_distancia = distancia_total * 0.1  # Reduzido de 0.5 para 0.1
				
				# Penalidade por ficar muito tempo sem coletar recursos
				penalidade_tempo_sem_coleta = 0
				if recursos_coletados == 0:
					penalidade_tempo_sem_coleta = ambiente.tempo * 0.5 # Reduzido de 2 para 0.5

				# Cálculo base do fitness
				fitness = (
					bonus_recursos -
					penalidade_colisoes -
					penalidade_energia -
					penalidade_tempo_parado -
					penalidade_movimento_irregular +
					recompensa_distancia -
					penalidade_tempo_sem_coleta
				)

				# Bônus por completar o objetivo corretamente
				if recursos_coletados == recursos_ambiente:
					if robo.meta_atingida:
						fitness += 2000 # Reduzido de 20000 para 2000
						# Bônus extra por completar rápido
						fitness += max(0, 500 - ambiente.tempo * 2) # Reduzido de 5000 para 500
						# Bônus extra por eficiência energética
						fitness += robo.energia * 2 # Reduzido de 10 para 2

				# Penalidade por tempo (ajustada para incentivar completar rápido)
				fitness -= ambiente.tempo * 0.2 # Reduzido de 1.0 para 0.2
    
				if robo.colisoes == 0:
					fitness *= 2 # Reduzido de 1000 para 2

				# Garantir que o fitness seja um número válido e não negativo
				individuo.fitness = max(0, fitness) if np.isfinite(fitness) else 0

			except Exception as e:
				print(f"Erro na avaliação: {str(e)}")
				individuo.fitness = 0

			# Atualizar melhor indivíduo
			if individuo.fitness > self.melhor_fitness:
				self.melhor_fitness = individuo.fitness
				self.melhor_individuo = individuo.copy()
				self.geracoes_sem_melhoria = 0
			elif individuo.fitness > self.ultimo_fitness * (1 + self.melhorias_minimas):
				self.geracoes_sem_melhoria = 0
			else:
				self.geracoes_sem_melhoria += 1

	def selecionar(self):
		# Seleção por torneio com pressão seletiva variável
		tamanho_torneio = 3  # Reduzido para menos pressão seletiva
		selecionados = []

		# Ordenar população por fitness
		populacao_ordenada = sorted(self.populacao, key=lambda x: x.fitness, reverse=True)

		# Manter os 30% melhores indivíduos (aumentado elitismo)
		n_elite = max(1, int(self.tamanho_populacao * 0.3))
		selecionados.extend(populacao_ordenada[:n_elite])

		# Selecionar o resto da população por torneio
		while len(selecionados) < self.tamanho_populacao:
			# Seleção por torneio com probabilidade proporcional ao fitness
			torneio = random.sample(self.populacao, tamanho_torneio)
			# Calcular probabilidades baseadas no fitness
			fitness_total = sum(ind.fitness for ind in torneio)
			if fitness_total > 0:
				probabilidades = [ind.fitness/fitness_total for ind in torneio]
				vencedor = random.choices(torneio, weights=probabilidades, k=1)[0]
			else:
				vencedor = random.choice(torneio)
			selecionados.append(vencedor.copy())

		return selecionados

	def evoluir(self, n_geracoes=50):
		# Parâmetros ajustados para melhor exploração
		taxa_mutacao = 0.2  # Reduzida para ser mais suave
		taxa_crossover = 0.9  # Aumentada para mais troca de material genético

		for geracao in range(n_geracoes):
			print(f"Geração {geracao + 1}/{n_geracoes}")

			# Avaliar população
			self.avaliar_populacao()

			# Calcular média do fitness da população
			media_fitness = sum(ind.fitness for ind in self.populacao) / len(self.populacao)
			self.historico_media_fitness.append(media_fitness)

			# Registrar melhor fitness
			self.historico_fitness.append(self.melhor_fitness)
			print(f"Melhor fitness: {self.melhor_fitness:.2f}")
			print(f"Média do fitness: {media_fitness:.2f}")

			# Verificar estagnação
			if self.geracoes_sem_melhoria >= self.max_geracoes_sem_melhoria:
				print("Detectada estagnação - aumentando diversidade...")
				# Aumentar taxa de mutação temporariamente
				taxa_mutacao = min(0.4, taxa_mutacao * 1.3)  # Aumento mais suave
				# Adicionar mais indivíduos aleatórios
				n_aleatorios = max(1, int(self.tamanho_populacao * 0.2))  # Reduzido para 20%
				for _ in range(n_aleatorios):
					novo = IndividuoPG(self.profundidade)
					self.populacao.append(novo)
				self.geracoes_sem_melhoria = 0
				print(f"taxa de mutação: {taxa_mutacao}")
			else:
				taxa_mutacao = 0.2  # Resetar taxa de mutação

			# Selecionar indivíduos
			selecionados = self.selecionar()

			# Criar nova população
			nova_populacao = []

			# Elitismo - manter os melhores indivíduos
			n_elite = max(1, int(self.tamanho_populacao * 0.3))  # Aumentado para 30%
			nova_populacao.extend(selecionados[:n_elite])

			# Preencher o resto da população
			while len(nova_populacao) < self.tamanho_populacao:
				# Seleção de pais
				pai1, pai2 = random.sample(selecionados, 2)

				# Crossover
				if random.random() < taxa_crossover:
					filho = pai1.crossover(pai2)
				else:
					filho = pai1.copy()

				# Mutação mais suave
				if random.random() < taxa_mutacao:
					filho.mutacao(probabilidade=0.3)  # Reduzida probabilidade de mutação por nó

				nova_populacao.append(filho)

			self.populacao = nova_populacao
			self.ultimo_fitness = self.melhor_fitness

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
	pg = ProgramacaoGenetica(tamanho_populacao=100, profundidade=2)
	melhor_individuo, historico = pg.evoluir(n_geracoes=50)

	# Salvar o melhor indivíduo
	print("Salvando o melhor indivíduo...")
	melhor_individuo.salvar('melhor_robo.json')

	# Plotar evolução do fitness
	print("Plotando evolução do fitness...")
	plt.figure(figsize=(12, 6))
	plt.plot(historico, label='Melhor Fitness', color='blue', linewidth=2)
	plt.plot(pg.historico_media_fitness, label='Média do Fitness', color='red', linestyle='--', alpha=0.7)
	plt.title('Evolução do Fitness ao Longo das Gerações')
	plt.xlabel('Geração')
	plt.ylabel('Fitness')
	plt.grid(True, linestyle='--', alpha=0.7)
	plt.legend()
	plt.savefig('evolucao_fitness_robo.png', dpi=300, bbox_inches='tight')
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
