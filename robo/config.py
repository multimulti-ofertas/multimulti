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
    "54553190268": "Kit estética automotiva Vonixx",
    "58211739182": "Pomada modeladora em bastão",
    "58261263365": "Capa de silicone para volante",
    "23397749259": "Kit 3 meias esportivas",
    "23998115427": "Par de faróis de milha LED",
    "22193851388": "Chave de fenda testadora",
    "58265705979": "Kit 3 pomadas modeladoras",
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
        "acessorios para carro", "suporte celular carro", "aspirador automotivo", "organizador porta malas",
        "camera veicular", "carregador veicular", "kit limpeza automotiva", "compressor de ar portatil",
        "porta copo carro", "capa de volante", "lampada led farol", "cheirinho para carro",
        "lavadora de alta pressao", "tapete automotivo", "organizador banco carro", "sensor de estacionamento",
        "cera automotiva", "flanela microfibra automotiva", "protetor solar parabrisa", "capa de banco carro",
        "transmissor fm bluetooth carro", "calibrador de pneu digital", "auxiliar de partida bateria",
        "triangulo de seguranca carro", "lixeira para carro", "encosto de cabeca carro", "almofada lombar carro",
        "porta objetos carro", "espelho retrovisor auxiliar", "led interno carro", "pretinho para pneu",
        "shampoo automotivo", "suporte celular moto", "capa para moto", "cadeado moto", "luva motociclista",
        "aromatizante carro", "suporte magnetico celular carro", "carregador wireless carro", "cabo usb veicular",
        "lampada pingo led carro", "capa chave canivete carro", "chaveiro automotivo", "camera de re",
        "alarme automotivo", "trava de volante", "bomba de ar portatil pneu", "cabo auxiliar de partida",
        "cinta de reboque", "kit reparo pneu", "limpa vidro automotivo", "cristalizador de vidro automotivo",
        "politriz automotiva", "boina de polimento", "toalha secagem automotiva", "escova lavagem carro",
        "organizador console carro", "gancho banco carro", "protetor de porta carro", "quebra sol carro",
        "ventilador veicular", "inversor de tensao veicular", "multimidia automotivo", "alto falante automotivo",
        "capa protetora carro", "bau para moto", "retrovisor moto", "intercomunicador moto",
        "capa de chuva motociclista", "balaclava moto", "suporte celular bicicleta moto",
    ],
    "ferramentas": [
        "jogo de chaves", "parafusadeira", "kit ferramentas", "trena laser", "furadeira", "alicate",
        "lanterna tatica", "multimetro", "chave catraca", "maleta de ferramentas", "nivel a laser",
        "serra marmore", "esmerilhadeira", "lixadeira", "caixa organizadora ferramentas", "fita isolante",
        "chave de impacto", "kit brocas", "chave de fenda", "martelo", "estilete profissional",
        "pistola de cola quente", "soprador termico", "ferro de solda", "morsa de bancada",
        "grampeador de parede", "serra tico tico", "chave inglesa", "kit soquetes", "lanterna de cabeca",
        "detector de metais parede", "macaco hidraulico",
        "chave allen kit", "chave torx", "jogo chave combinada", "chave de roda", "alicate de pressao",
        "alicate amperimetro", "testador de tomada", "parafusadeira de impacto", "serra circular", "serra copo",
        "micro retifica", "multiferramenta", "paquimetro digital", "esquadro", "nivel de bolha", "talhadeira",
        "grampo sargento", "rebitadeira", "torquimetro", "saca polia", "pe de cabra", "serrote", "arco de serra",
        "plaina eletrica", "tupia", "pistola de pintura", "aplicador de silicone", "abracadeira nylon",
        "luva de protecao", "oculos de protecao", "cinto porta ferramentas",
        "bolsa de ferramentas", "extensao soquete", "kit bits parafusadeira", "tesoura de poda",
    ],
    "cuidado": [
        "barbeador masculino", "aparador de pelos masculino", "kit barba", "perfume masculino",
        "maquina de cortar cabelo", "pomada modeladora", "hidratante facial masculino",
        "shampoo anticaspa masculino", "protetor solar facial masculino", "desodorante masculino",
        "oleo para barba", "balm para barba", "pente de barba", "escova de cabelo masculina",
        "sabonete facial masculino", "esfoliante facial", "mascara facial carvao", "gel de barbear",
        "espuma de barbear", "pos barba", "perfume arabe masculino", "body splash masculino",
        "colonia masculina", "shampoo para barba", "kit skincare masculino", "cera para cabelo masculino",
        "creme para pentear masculino", "tinta para barba", "aparador de sobrancelha masculino",
        "serum facial masculino", "vitamina c facial", "protetor labial",
        "condicionador masculino", "kit shampoo e condicionador masculino", "tonico capilar", "gel fixador cabelo",
        "spray fixador cabelo", "po modelador cabelo", "pomada efeito matte", "navalha de barbear",
        "laminas de barbear", "aparador de nariz", "maquina de acabamento", "shaver masculino", "cortador de unha",
        "desodorante antitranspirante masculino", "talco para pes", "creme para pes", "perfume contratipo masculino",
        "kit presente masculino perfume", "sabonete liquido masculino", "sabonete em barra masculino",
        "esponja de banho", "escova de dente eletrica", "irrigador oral", "clareador dental",
        "hidratante corporal masculino", "toalha de barbear", "capa de corte barbeiro",
    ],
    "estilo": [
        "camiseta masculina", "relogio masculino", "tenis masculino", "carteira masculina",
        "bermuda masculina", "oculos de sol masculino", "mochila masculina", "kit meia masculina",
        "cueca boxer kit", "bone masculino", "cinto masculino couro", "chinelo masculino",
        "camisa polo masculina", "jaqueta masculina", "calca jeans masculina", "moletom masculino",
        "camisa social masculina", "sapato social masculino", "bota masculina", "sandalia masculina",
        "corrente masculina prata", "pulseira masculina", "anel masculino", "bolsa transversal masculina",
        "shorts tactel masculino", "regata masculina", "camiseta dry fit masculina", "gorro masculino",
        "chapeu bucket", "porta cartao masculino", "necessaire masculina", "gravata",
        "pijama masculino", "calca cargo masculina", "jaqueta corta vento masculina",
        "camiseta oversized masculina", "kit camiseta basica masculina", "camisa de linho masculina",
        "camisa xadrez flanela", "jaqueta jeans masculina", "jaqueta de couro masculina", "colete masculino",
        "blazer masculino", "sueter masculino", "cardigan masculino", "calca alfaiataria masculina",
        "calca jogger masculina", "bermuda jeans masculina", "bermuda sarja masculina", "sunga masculina",
        "short de praia masculino", "tenis casual masculino", "tenis de corrida masculino", "mocassim masculino",
        "sapatenis", "papete masculina", "meia cano alto", "meia invisivel masculina", "relogio digital masculino",
        "smartwatch masculino", "pulseira de couro masculina", "colar masculino", "oculos polarizado",
        "bone aba reta", "carteira slim", "pochete masculina", "mala de viagem", "mochila notebook",
        "bolsa de academia", "suspensorio", "abotoadura", "cueca samba cancao", "regata academia masculina",
        "camiseta compressao masculina", "bermuda academia masculina",
    ],
}

# Regras de seleção
NOTA_MINIMA = 4.6
VENDAS_MINIMAS = 100
VENDAS_MINIMAS_API = 500      # com a API: só produto com +500 vendas (1000 deixava o dia de cuidado com 6 produtos)
DESCONTO_MINIMO = 0           # % OFF mínimo (0 = não exige; o que importa é preço bom + vendas + nota)
PRODUTOS_POR_DIA = 8          # por dia: 4 Reels + 1 feed + 3 só nos stories = 8 stories sem repetir
STORIES_POR_VEZ = 1           # stories postados a cada horário da rotina

# Chave geral: False = o robô continua montando os produtos e a vitrine, mas não publica nada no Instagram.
POSTAR_NO_INSTAGRAM = True

# Narração dos Reels com voz de IA: "piper" (roda no GitHub), "edge" (Microsoft, não oficial) ou None (só música)
VOZ = "edge"

# Zé Multi (personagem 2D, robo/personagem.py) apresentando os Reels narrados. False = Reels sem o Zé.
PERSONAGEM = True
# Teste A/B até esta data (inclusive): metade dos Reels sai sem o Zé, alternando horário a cada dia.
# O produtos.json marca "ze": true/false em cada Reels para comparar as visualizações depois.
TESTE_ZE_ATE = "2026-10-31"

# Rotina diária (horário de Cuiabá). O robô de postagem roda 4x por hora e publica o que estiver
# marcado até aquela hora. Limite do Instagram: 100 publicações por 24h (aqui são 13 por dia).
# 23/out: foco em Reels. Com 5 seguidores, story e foto só chegam a quem já segue; quem traz gente
# nova é o Reels (o do farol LED, 19/out, teve ~1,9 mil visualizações e trouxe os cliques de 20/out).
ROTINA = {h: ["story"] for h in (10, 11, 13, 14, 15, 16, 18, 21)}  # 8 stories (1 por produto do dia)
ROTINA[9] = ["reel"]              # Reels: 09h Cuiabá = 10h Brasília
ROTINA[12] = ["reel"]             # 12h Cuiabá = 13h Brasília
ROTINA[17] = ["reel"]             # 17h Cuiabá = 18h Brasília
ROTINA[20] = ["reel"]             # 20h Cuiabá = 21h Brasília
ROTINA[19] = ["feed"]             # 1 foto no feed: 19h Cuiabá = 20h Brasília
REELS_POR_DIA = sum(t.count("reel") for t in ROTINA.values())
FEEDS_POR_DIA = sum(t.count("feed") for t in ROTINA.values())

# Rotina antiga, só para terminar o dia 14/out sem juntar dois posts no mesmo horário (pode apagar depois)
ROTINA_ANTIGA = {h: ["story"] for h in range(8, 23)}
ROTINA_ANTIGA.update({8: ["feed", "story"], 20: ["feed", "story"], 12: ["reel", "story"], 21: ["reel", "story"]})
NAO_REPETIR_DIAS = None       # None = nunca repete o mesmo produto (nem um muito parecido)
TIPO_FOLGA_DIAS = 7           # o mesmo TIPO só volta depois de 7 dias; se faltar produto pra fechar o dia, completa com tipo recente (só stories)
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
