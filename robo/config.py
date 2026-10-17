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

# Exceções por data (AAAA-MM-DD → tema). Ex.: quando a planilha de um tema está fraca.
TEMA_EM = {
    "2026-10-15": "top",   # quinta: estilo estava fraco na planilha → mistura os mais vendidos
}

# Nomes escritos à mão quando o nome automático fica estranho (itemId → nome curto)
NOMES = {
    "23797686527": "Relógio digital masculino",
    "22336506478": "Pincéis de limpeza automotiva",
    "9310112081": "Nível a laser",
    "23399440533": "Cheirinho de carro novo spray",
    "16280432664": "Borracha protetora de porta 10m",
    "57201143767": "Cola para tênis e sapatos",
    "22394340005": "Tinta para couro e sapato",
    "21098003892": "Porta-óculos para carro",
    "23294438614": "Maleta para furadeira",
    "19798290134": "Cadarço chato para tênis",
    "20098534951": "Protetor de porta (Honda)",
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
VENDAS_MINIMAS_API = 1000     # com a API dá para ser exigente: só produto com +1 mil vendas
DESCONTO_MINIMO = 10          # % OFF
PRODUTOS_POR_DIA = 12         # por dia: 2 no feed + 2 em Reels + 8 só nos stories = 12 stories sem repetir
STORIES_POR_VEZ = 1           # stories postados a cada horário da rotina

# Chave geral: False = o robô continua montando os produtos e a vitrine, mas não publica nada no Instagram.
POSTAR_NO_INSTAGRAM = True

# Rotina diária (horário de Cuiabá). O robô de postagem roda de hora em hora e publica o que estiver
# marcado para aquela hora. Limite do Instagram: 50 publicações por 24h (aqui são 19 por dia).
# Horários em CUIABÁ (Brasília = +1h). Escolhidos em 14/out pelos estudos de 2026 (almoço e noite).
ROTINA = {h: ["story"] for h in range(9, 21)}   # 1 story por hora: 09h–20h Cuiabá = 10h–21h Brasília (12 por dia)
ROTINA[11] = ["feed", "story"]   # feed: 11h Cuiabá = 12h Brasília
ROTINA[19] = ["feed", "story"]   # feed: 19h Cuiabá = 20h Brasília
ROTINA[12] = ["reel", "story"]   # Reels: 12h Cuiabá = 13h Brasília
ROTINA[20] = ["reel", "story"]   # Reels: 20h Cuiabá = 21h Brasília

# Rotina antiga, só para terminar o dia 14/out sem juntar dois posts no mesmo horário (pode apagar depois)
ROTINA_ANTIGA = {h: ["story"] for h in range(8, 23)}
ROTINA_ANTIGA.update({8: ["feed", "story"], 20: ["feed", "story"], 12: ["reel", "story"], 21: ["reel", "story"]})
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
