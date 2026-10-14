"""Configurações do robô MultiMulti. Edite aqui para mudar temas, palavras e regras."""
import os

# Dias temáticos (0 = segunda ... 6 = domingo)
CALENDARIO = {
    0: "carro",
    1: "ferramentas",
    2: "cuidado",
    3: "estilo",
    4: "top",      # sexta: top da semana (mistura tudo)
    5: "top",
    6: "top",
}

# Nome que aparece no selo da arte
SELO = {"carro": "Carro", "ferramentas": "Ferramentas", "cuidado": "Cuidado", "estilo": "Estilo"}
EMOJI = {"carro": "🚗", "ferramentas": "🔧", "cuidado": "🧔", "estilo": "👟"}

# Palavras buscadas na Shopee por categoria (o robô sorteia algumas por dia)
PALAVRAS = {
    "carro": [
        "acessorios para carro", "suporte celular carro", "aspirador automotivo",
        "organizador porta malas", "camera veicular", "carregador veicular",
        "kit limpeza automotiva", "compressor de ar portatil", "porta copo carro",
        "capa de volante", "lampada led farol",
    ],
    "ferramentas": [
        "jogo de chaves", "parafusadeira", "kit ferramentas", "trena laser",
        "furadeira", "alicate", "lanterna tatica", "multimetro", "chave catraca",
        "maleta de ferramentas", "nivel a laser",
    ],
    "cuidado": [
        "barbeador masculino", "aparador de pelos masculino", "kit barba",
        "perfume masculino", "maquina de cortar cabelo", "pomada modeladora",
        "hidratante facial masculino", "shampoo anticaspa masculino", "protetor solar facial masculino",
    ],
    "estilo": [
        "camiseta masculina", "relogio masculino", "tenis masculino", "carteira masculina",
        "bermuda masculina", "oculos de sol masculino", "mochila masculina", "kit meia masculina",
        "cueca boxer kit", "bone masculino",
    ],
}

# Regras de seleção
NOTA_MINIMA = 4.6
VENDAS_MINIMAS = 100
DESCONTO_MINIMO = 10          # % OFF
PRODUTOS_POR_DIA = 8          # por dia: 2 no feed + 2 em Reels + 4 só nos stories (todos na vitrine)
STORIES_POR_VEZ = 1           # stories postados a cada horário da rotina

# Chave geral: False = o robô continua montando os produtos e a vitrine, mas não publica nada no Instagram.
# (Desligada em 14/out: a Meta pediu confirmação da conta de desenvolvedor e bloqueou a API.)
POSTAR_NO_INSTAGRAM = False

# Rotina diária (horário de Cuiabá). O robô de postagem roda de hora em hora e publica o que estiver
# marcado para aquela hora. Limite do Instagram: 50 publicações por 24h (aqui são 19 por dia).
ROTINA = {h: ["story"] for h in range(8, 23)}   # 1 story por hora, das 08h às 22h (15 por dia)
ROTINA[8] = ["feed", "story"]    # 1º post do feed
ROTINA[20] = ["feed", "story"]   # 2º post do feed (12h depois)
ROTINA[12] = ["reel", "story"]   # 1º Reels
ROTINA[21] = ["reel", "story"]   # 2º Reels
NAO_REPETIR_DIAS = None       # None = nunca repete o mesmo produto (nem um muito parecido)
GUARDAR_MIDIA_DIAS = 10       # apaga vídeos/imagens antigos para o repositório não crescer demais

# Endereços
PAGES_URL = os.environ.get("PAGES_URL", "https://multimulti-ofertas.github.io/multimulti").rstrip("/")
INSTAGRAM = "@multimulti.ofertas"

HASHTAGS_FIXAS = "#achadosmasculinos #achadinhosshopee #shopee #achadinhos #ofertas #multimulti"
HASHTAGS = {
    "carro": "#carro #acessoriosautomotivos",
    "ferramentas": "#ferramentas #façavocêmesmo",
    "cuidado": "#barba #cuidadosmasculinos",
    "estilo": "#modamasculina #estilomasculino",
}
