import os
import base64
import streamlit as st
from PIL import Image, ImageDraw

# Tentativa opcional de carregar coordenadas interativas (funciona mesmo se não instalado)
try:
    from streamlit_image_coordinates import streamlit_image_coordinates
    HAS_COORDS = True
except ImportError:
    HAS_COORDS = False

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA E MODO ANTI-DISTRAÇÃO
# ==============================================================================
st.set_page_config(
    page_title="CrustaMorf 2.0 | UFRPE",
    page_icon="🦐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ESTILIZAÇÃO CSS (BIO-MARINE UI & FOCO COGNITIVO)
# ==============================================================================
st.markdown("""
<style>
    /* Ocultar menus desnecessários do Streamlit para evitar distrações em aula */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Cartões Pedagógicos e Destaques */
    .stCard {
        background-color: #112240;
        border-left: 5px solid #00E5FF;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #E6F1FF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stCard h4 {
        color: #00E5FF;
        margin-top: 0;
    }
    .badge-tagma {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        background-color: #00E5FF;
        color: #0A192F;
        margin-bottom: 8px;
    }
    .alerta-clinico {
        background-color: #2D1B2E;
        border-left: 5px solid #FF6B6B;
        padding: 14px;
        border-radius: 8px;
        color: #FFDADA;
        margin-top: 10px;
    }
    .dica-bancada {
        background-color: #132A13;
        border-left: 5px solid #4ECDC4;
        padding: 14px;
        border-radius: 8px;
        color: #E8F8F5;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BASE DE DADOS ANATÔMICA E ZOOTÉCNICA (PENAEUS VANNAMEI)
# ==============================================================================
ESTRUTURAS = {
    "Rostro (Rostrum)": {
        "tagma": "Cefalotórax",
        "coords": (120, 140),
        "funcao": "Projeção rígida anterior da carapaça com dentes dorsais e ventrais. Atua na estabilização hidrodinâmica e defesa mecânica.",
        "importancia_zootecnica": "Essencial para identificação taxonômica (fórmula rostral em P. vannamei geralmente apresenta 7-10 dentes dorsais e 2-4 ventrais). Deformidades ou quebras indicam estresse nutricional ou alta densidade de estocagem.",
        "dica_lab": "Conte os dentes dorsais e ventrais com auxílio de uma lupa estereoscópica para confirmar a espécie."
    },
    "Cefalotórax (Carapaça)": {
        "tagma": "Cefalotórax",
        "coords": (260, 160),
        "funcao": "Fusão da cabeça e tórax recoberta pelo exoesqueleto quitinoso calcificado, protegendo órgãos vitais e câmaras branquiais.",
        "importancia_zootecnica": "Manchas brancas circulares na face interna da carapaça são o principal sinal clínico do Vírus da Mancha Branca (WSSV). Carapaça mole pode indicar alcalinidade baixa na água do viveiro.",
        "dica_lab": "Pressione levemente a lateral da carapaça para avaliar a rigidez do estado de muda (intermuda vs. pós-muda)."
    },
    "Antênulas e Antenas": {
        "tagma": "Cefalotórax",
        "coords": (90, 210),
        "funcao": "Apêndices sensoriais primários responsáveis pela quimiorrecepção (olfato/paladar subaquático), equilíbrio (estatocisto na base antenular) e mecanorrecepção.",
        "importancia_zootecnica": "Antenas quebradas, curtas ou com necroses escuras (melanização) são o primeiro bioindicador de deterioração da qualidade do fundo do viveiro ou infecção bacteriana (Vibriose).",
        "dica_lab": "Observe se o comprimento das antenas ultrapassa o corpo; antenas íntegras indicam excelente manejo sanitário."
    },
    "Pereiópodes (Patas Ambulatórias)": {
        "tagma": "Cefalotórax",
        "coords": (280, 290),
        "funcao": "Cinco pares de apêndices torácicos usados para caminhar no substrato, escavar e capturar alimento (os 3 primeiros pares são quelados na subordem Dendrobranchiata).",
        "importancia_zootecnica": "A presença de quelas nos 3 primeiros pares diferencia os camarões marinhos peneídeos dos carídeos (como o Macrobrachium rosenbergii, que possui quela apenas nos 2 primeiros pares).",
        "dica_lab": "Use uma pinça fina para estender os 5 pares e identificar as micro-quelas nos 3 primeiros pares."
    },
    "Hepatopâncreas (Glândula Digestiva)": {
        "tagma": "Sistemas Internos",
        "coords": (250, 175),
        "funcao": "Principal órgão metabólico: atua na secreção de enzimas digestivas, absorção de nutrientes, armazenamento de lipídios e desintoxicação.",
        "importancia_zootecnica": "Órgão-alvo da Necrose Hepatopancreática Aguda (AHPND/EMS) e Vibrioses. Em animais saudáveis, apresenta coloração marrom-dourada e volume cheio; quando pálido ou atrofiado, indica inanição ou infecção severa.",
        "dica_lab": "Em pós-larvas e juvenis translúcidos, avalie a cor e o preenchimento lipídico contra a luz."
    },
    "Brânquias (Dendrobrânquias)": {
        "tagma": "Sistemas Internos",
        "coords": (295, 210),
        "funcao": "Estruturas ramificadas localizadas na câmara branquial responsáveis pelas trocas gasosas (O₂/CO₂), excreção de amônia e osmorregulação.",
        "importancia_zootecnica": "Brânquias escurecidas (amareladas ou pretas) indicam acúmulo de matéria orgânica em suspensão, protozoários epibiontes (Zoothamnium) ou estresse por nitrito/amônia.",
        "dica_lab": "Rebata a borda ventro-lateral da carapaça (branquiostegito) para expor a estrutura ramificada das dendrobrânquias."
    },
    "Abdômen (Pleômeros)": {
        "tagma": "Abdômen",
        "coords": (450, 150),
        "funcao": "Composto por 6 segmentos musculares articulados que abrigam o intestino médio e a musculatura flexora rápida para natação de fuga.",
        "importancia_zootecnica": "Principal parte comercializável do camarão. Opacidade muscular esbranquiçada (necrose muscular) pode ocorrer por choque térmico, hipóxia ou infecção pelo vírus IMNV (Mionecrose Infecciosa).",
        "dica_lab": "Verifique a transparência do músculo abdominal e a linha escura dorsal correspondente ao trato intestinal cheio."
    },
    "Pleópodes (Patas Natatórias)": {
        "tagma": "Abdômen",
        "coords": (440, 270),
        "funcao": "Cinco pares de apêndices abdominais birremes adaptados para natação contínua. No macho, o 1º par é modificado em Petasma (órgão copulador).",
        "importancia_zootecnica": "Fundamental para sexagem em reprodutores: machos apresentam o Petasma (1º par de pleópodes unido), enquanto fêmeas possuem o Télico entre os últimos pereiópodes.",
        "dica_lab": "Inspecione o 1º par abdominal ventralmente para determinar o sexo do exemplar na bancada."
    },
    "Telson e Urópodes (Leque Caudal)": {
        "tagma": "Leque Caudal",
        "coords": (620, 220),
        "funcao": "O Telson (espinho central) e os Urópodes (abas laterais) formam o leque caudal, responsável pela propulsão explosiva para trás na reação de escape.",
        "importancia_zootecnica": "Bordas avermelhadas ou corroídas (erosão do leque caudal) são sinais clássicos de estresse ambiental ou infecção bacteriana secundária no cultivo.",
        "dica_lab": "Abra os urópodes em formato de leque e observe a integridade das cerdas marginais."
    }
}

# ==============================================================================
# CASOS CLÍNICOS DE CULTIVO (PBL - APRENDIZAGEM BASEADA EM PROBLEMAS)
# ==============================================================================
CASOS_CLINICOS = [
    {
        "titulo": "Caso 1: Mortalidade Súbita e Pontos Calcários",
        "cenario": "Em uma fazenda de carcinicultura no litoral de Pernambuco, os camarões (P. vannamei) passaram a nadar erraticamente próximos às bordas do viveiro e reduziram o consumo de ração. Na inspeção de bancada, você observa pontos circulares esbranquiçados incrustados na face interna da carapaça.",
        "pergunta": "Qual estrutura anatômica deve ser inspecionada prioritariamente e qual é a suspeita diagnóstica principal?",
        "opcoes": [
            "A) Cefalotórax (Carapaça) — Suspeita de Vírus da Mancha Branca (WSSV).",
            "B) Pleópodes — Suspeita de deficiência de cálcio na água.",
            "C) Rostro — Suspeita de canibalismo por alta densidade.",
            "D) Telson — Suspeita de Mionecrose Infecciosa (IMNV)."
        ],
        "correta": 0,
        "explicacao": "Correto! Depósitos circulares de sais de cálcio na cutícula interna da carapaça (Cefalotórax) são o sinal patognomônico clássico do Vírus da Mancha Branca (WSSV)."
    },
    {
        "titulo": "Caso 2: Camarões Letárgicos e Intestino Vazio",
        "cenario": "Durante a biometria semanal de juvenis de 4g, você nota que diversos indivíduos estão com o trato intestinal vazio e apresentam uma mancha pálida e encolhida na região póstero-dorsal do cefalotórax.",
        "pergunta": "Qual órgão interno está atrofiado e qual sua função comprometida?",
        "opcoes": [
            "A) Coração dorsal — Bombeamento de hemolinfa.",
            "B) Hepatopâncreas — Digestão enzimática, reserva lipídica e metabolismo.",
            "C) Estatocisto — Equilíbrio hidrodinâmico.",
            "D) Petasma — Maturação reprodutiva."
        ],
        "correta": 1,
        "explicacao": "Exato! O Hepatopâncreas é o centro metabólico e digestivo do camarão. Sua palidez e atrofia indicam parada alimentar e possível infecção entérica (como Vibriose ou AHPND)."
    },
    {
        "titulo": "Caso 3: Diferenciação Taxonômica Rápida na Bancada",
        "cenario": "Um estudante precisa separar rapidamente exemplares de Penaeus vannamei (Dendrobranchiata) de camarões de água doce Macrobrachium rosenbergii (Pleocyemata/Caridea) misturados no laboratório.",
        "pergunta": "Qual característica morfológica externa confirma que o exemplar é um peneídeo (P. vannamei)?",
        "opcoes": [
            "A) Presença de quelas apenas nos 2 primeiros pares de pereiópodes.",
            "B) Presença de quelas nos 3 primeiros pares de pereiópodes e 2º somito abdominal não sobrepondo o 1º.",
            "C) Ausência total de rostro.",
            "D) Presença de brânquias do tipo filobrânquia."
        ],
        "correta": 1,
        "explicacao": "Perfeito! Os camarões da subordem Dendrobranchiata (como P. vannamei) possuem os 3 primeiros pares de pereiópodes quelados e brânquias dendrobrânquias, além da pleura do 2º segmento abdominal não sobrepor a do 1º."
    }
]

# ==============================================================================
# BANCO DE 15 QUESTÕES DO MODO DESAFIO (QUIZ)
# ==============================================================================
QUESTOES_QUIZ = [
    {"q": "1. Quantos pares de pereiópodes (patas ambulatórias) possui o camarão Penaeus vannamei?", "opts": ["3 pares", "4 pares", "5 pares", "6 pares"], "ans": 2, "exp": "Os decápodes possuem 5 pares de pereiópodes (10 patas torácicas)."},
    {"q": "2. Em P. vannamei, quantos pares de pereiópodes terminam em quela (pinça)?", "opts": ["Apenas o 1º par", "Os 2 primeiros pares", "Os 3 primeiros pares", "Todos os 5 pares"], "ans": 2, "exp": "Na subordem Dendrobranchiata (família Penaeidae), os 3 primeiros pares de pereiópodes são quelados."},
    {"q": "3. Qual é o nome do órgão copulador masculino localizado no 1º par de pleópodes?", "opts": ["Télico", "Petasma", "Escafocerito", "Estatocisto"], "ans": 1, "exp": "O Petasma é formado pela união dos endopoditos do 1º par de pleópodes nos machos."},
    {"q": "4. Onde se localiza o Télico, estrutura receptora de espermatóforos nas fêmeas?", "opts": ["Na face ventral do tórax, entre os últimos pares de pereiópodes", "Na ponta do rostro", "Junto ao telson", "No 3º par de pleópodes"], "ans": 0, "exp": "O télico situa-se nos esternitos torácicos entre o 4º e 5º par de pereiópodes."},
    {"q": "5. Qual tipo de brânquia caracteriza a subordem do camarão marinho P. vannamei?", "opts": ["Tricobrânquia", "Filobrânquia", "Dendrobrânquia", "Lamelibrânquia"], "ans": 2, "exp": "Dendrobrânquias possuem eixo principal com ramificações secundárias em formato de árvore."},
    {"q": "6. Qual apêndice atua como estabilizador hidrodinâmico (leme) na base da segunda antena?", "opts": ["Escafocerito (Exopodito antenal)", "Mandíbula", "Maxilípede", "Urópode"], "ans": 0, "exp": "O escafocerito (escamas antenais) funciona como estabilizador durante o nado e salto para trás."},
    {"q": "7. Qual a principal função dos pleópodes localizados no abdômen?", "opts": ["Trituração de alimentos", "Natação contínua para frente", "Escavação pesada", "Defesa contra predadores"], "ans": 1, "exp": "Os pleópodes são apêndices abdominais birremes especializados na natação."},
    {"q": "8. O leque caudal do camarão é formado pela combinação de quais estruturas?", "opts": ["Rostro e Antênulas", "Telson central e dois pares de Urópodes laterais", "Quinto par de pleópodes e carapaça", "Petasma e Télico"], "ans": 1, "exp": "O telson mediano junto aos urópodes laterais compõe o leque caudal propulsor."},
    {"q": "9. Qual estrutura sensorial localizada na base das antênulas é responsável pelo equilíbrio espacial do camarão?", "opts": ["Olho composto", "Estatocisto", "Hepatopâncreas", "Glândula antenal"], "ans": 1, "exp": "O estatocisto contém um estatólito interno que informa a orientação gravitacional ao sistema nervoso."},
    {"q": "10. Onde fica localizada a Glândula Antenal (Glândula Verde), responsável pela excreção e osmorregulação?", "opts": ["No telson", "Na base das antenas (cefalotórax)", "No 6º segmento abdominal", "Nas brânquias"], "ans": 1, "exp": "Situa-se na região anterior do cefalotórax, abrindo-se num poro excretor na base da segunda antena."},
    {"q": "11. O que indica uma coloração avermelhada ou necrose escura (melanização) nas extremidades dos apêndices?", "opts": ["Crescimento acelerado normal", "Resposta imune a lesões físicas ou infecção bacteriana (ex: Vibrio)", "Prontidão para reprodução", "Excesso de oxigênio dissolvido"], "ans": 1, "exp": "A melanização ocorre pela ativação do sistema profenoloxidase em resposta a patógenos ou traumas."},
    {"q": "12. Quantos segmentos (somitos/pleômeros) compõem o abdômen de um camarão peneídeo?", "opts": ["4 segmentos", "5 segmentos", "6 segmentos", "8 segmentos"], "ans": 2, "exp": "O abdômen dos decápodes é formado por 6 somitos articulados antes do telson."},
    {"q": "13. Qual órgão interno ocupa grande parte do cefalotórax e é o principal indicador do estado nutricional do camarão?", "opts": ["Coração", "Hepatopâncreas", "Cordão nervoso ventral", "Ceco posterior"], "ans": 1, "exp": "O hepatopâncreas armazena lipídios e glicogênio, refletindo diretamente a saúde nutricional."},
    {"q": "14. Como o P. vannamei é classificado quanto ao tipo de télico nas fêmeas?", "opts": ["Télico aberto", "Télico fechado", "Sem télico", "Télico interno abdominal"], "ans": 0, "exp": "Penaeus vannamei pertence ao grupo de camarões de télico aberto, exigindo cópula com a fêmea em estado de carapaça dura."},
    {"q": "15. Qual reação comportamental/anatômica é acionada pela contração rápida da musculatura abdominal e abertura do leque caudal?", "opts": ["Forrageamento lento", "Ecdise (Muda)", "Reação de fuga explosiva para trás (Caridoid escape reaction)", "Acasalamento"], "ans": 2, "exp": "A flexão abdominal rápida projeta o camarão para trás em alta velocidade para escapar de predadores."}
]

# ==============================================================================
# FUNÇÕES UTILITÁRIAS (IMAGEM DE FALLBACK E RENDERIZAÇÃO 3D/AR)
# ==============================================================================
def carregar_imagem_2d():
    """Carrega camarao.jpg ou gera um diagrama esquemático automático caso o arquivo não exista."""
    if os.path.exists("camarao.jpg"):
        return Image.open("camarao.jpg")
    
    # Gera imagem esquemática de segurança para que o app nunca trave sem o arquivo
    img = Image.new("RGB", (750, 380), color=(10, 25, 47))
    draw = ImageDraw.Draw(img)
    draw.rectangle([15, 15, 735, 365], outline=(0, 229, 255), width=2)
    # Desenho estilizado dos tagmas
    draw.ellipse([160, 110, 350, 240], fill=(20, 60, 110), outline=(0, 229, 255), width=3) # Cefalotórax
    draw.polygon([(70, 150), (165, 130), (165, 165)], fill=(0, 180, 216)) # Rostro
    draw.ellipse([350, 120, 580, 220], fill=(28, 85, 140), outline=(0, 229, 255), width=3) # Abdômen
    draw.polygon([(580, 160), (670, 210), (640, 250)], fill=(0, 229, 255)) # Leque caudal
    draw.text((210, 40), "DIAGRAMA INTERATIVO - PENAEUS VANNAMEI", fill=(0, 229, 255))
    draw.text((195, 165), "CEFALOTORAX", fill=(255, 255, 255))
    draw.text((425, 165), "ABDOMEN", fill=(255, 255, 255))
    draw.text((590, 255), "TELSON", fill=(255, 255, 255))
    return img

def renderizar_modelo_3d(arquivo_glb, titulo_modelo):
    """Renderiza modelo .glb com suporte a rotação 360 e Realidade Aumentada (AR) via Google Model-Viewer."""
    if not os.path.exists(arquivo_glb):
        st.warning(f"⚠️ Arquivo `{arquivo_glb}` não encontrado na pasta raiz do projeto.")
        st.info("💡 **Como ativar:** Coloque o arquivo `.glb` na mesma pasta do `app_crustamorf.py` para visualizar em 3D e Realidade Aumentada.")
        return

    with open(arquivo_glb, "rb") as f:
        dados_b64 = base64.b64encode(f.read()).decode("utf-8")

    html_3d = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <div style="background: radial-gradient(circle, #112240 0%, #0A192F 100%); border-radius: 12px; padding: 15px; border: 1px solid #00E5FF;">
        <model-viewer 
            src="data:model/gltf-binary;base64,{dados_b64}"
            alt="{titulo_modelo}"
            camera-controls
            auto-rotate
            ar
            ar-modes="webxr scene-viewer quick-look"
            shadow-intensity="1"
            exposure="1.1"
            style="width: 100%; height: 520px; background-color: transparent;">
            <button slot="ar-button" style="background-color: #00E5FF; color: #0A192F; border-radius: 8px; border: none; padding: 10px 18px; position: absolute; bottom: 16px; right: 16px; font-weight: bold; cursor: pointer;">
                📱 Projetar na Bancada (Realidade Aumentada)
            </button>
        </model-viewer>
    </div>
    """
    st.components.v1.html(html_3d, height=560)

# ==============================================================================
# BARRA LATERAL E CONTROLE DE FOCO EM AULA
# ==============================================================================
with st.sidebar:
    st.title("🦐 CrustaMorf 2.0")
    st.caption("Engenharia de Pesca & Aquicultura — **UFRPE**")
    st.markdown("---")
    
    modo_foco = st.toggle("🎯 Modo Foco (Aula Prática)", value=False, help="Simplifica a interface e exibe o roteiro rápido de inspeção de bancada.")
    
    modulo = st.radio(
        "Selecione o Módulo de Estudo:",
        [
            "📖 1. Atlas 2D & Clínica Zootécnica",
            "🧊 2. Laboratório 3D & Realidade Aumentada",
            "🩺 3. Simulador de Diagnóstico (PBL)",
            "🎮 4. Modo Desafio (Quiz 15 Questões)",
            "🧠 5. Mapa Mental & Roteiro de Bancada"
        ]
    )
    
    st.markdown("---")
    if modo_foco:
        st.success("✅ **Modo Foco Ativo:** Siga o checklist abaixo durante a análise do espécime na lupa.")
        st.checkbox("1. Contar fórmula rostral (D/V)")
        st.checkbox("2. Inspecionar transparência da carapaça")
        st.checkbox("3. Verificar 3 pares de pereiópodes quelados")
        st.checkbox("4. Identificar sexo (Petasma vs. Télico)")
        st.checkbox("5. Avaliar integridade do leque caudal")
    else:
        st.info("💡 **Dica:** Ative o *Modo Foco* acima durante as aulas de laboratório para habilitar o checklist de bancada.")

# ==============================================================================
# MÓDULO 1: ATLAS 2D INTERATIVO E IMPORTÂNCIA ZOOTÉCNICA
# ==============================================================================
if modulo == "📖 1. Atlas 2D & Clínica Zootécnica":
    st.header("📖 Atlas Morfológico 2D & Diagnóstico Zootécnico")
    st.write("Explore as estruturas anatômicas do *Penaeus vannamei*, compreendendo sua função biológica e como avaliar a saúde do cultivo.")

    col_filtro1, col_filtro2 = st.columns([1, 2])
    with col_filtro1:
        filtro_tagma = st.selectbox(
            "Filtrar por Região Corporal (Tagma):",
            ["Todas as Regiões", "Cefalotórax", "Abdômen", "Leque Caudal", "Sistemas Internos"]
        )
    
    estruturas_filtradas = {
        k: v for k, v in ESTRUTURAS.items()
        if filtro_tagma == "Todas as Regiões" or v["tagma"] == filtro_tagma
    }
    
    with col_filtro2:
        estrutura_selecionada = st.selectbox(
            "Selecione a Estrutura para Inspeção Detalhada:",
            list(estruturas_filtradas.keys())
        )

    col_img, col_info = st.columns([1.2, 1])

    with col_img:
        img_base = carregar_imagem_2d().copy()
        draw = ImageDraw.Draw(img_base)
        
        # Desenhar marcador luminoso na estrutura selecionada
        x, y = ESTRUTURAS[estrutura_selecionada]["coords"]
        raio = 16
        draw.ellipse([x - raio, y - raio, x + raio, y + raio], outline=(0, 229, 255), width=4)
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 107, 107))
        
        st.image(img_base, caption=f"Foco Anatômico: {estrutura_selecionada}", use_container_width=True)

    with col_info:
        dados = ESTRUTURAS[estrutura_selecionada]
        st.markdown(f"""
        <div class="stCard">
            <span class="badge-tagma">{dados['tagma']}</span>
            <h4>🔎 {estrutura_selecionada}</h4>
            <p><strong>⚙️ Função Biológica:</strong><br>{dados['funcao']}</p>
        </div>
        <div class="alerta-clinico">
            <strong>🩺 Importância Zootécnica & Sinais Clínicos:</strong><br>{dados['importancia_zootecnica']}
        </div>
        <div class="dica-bancada">
            <strong>🔬 Roteiro de Prática (Na Lupa):</strong><br>{dados['dica_lab']}
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# MÓDULO 2: VISUALIZADOR 3D E REALIDADE AUMENTADA (AR)
# ==============================================================================
elif modulo == "🧊 2. Laboratório 3D & Realidade Aumentada":
    st.header("🧊 Visualizador 3D Interativo & Realidade Aumentada (AR)")
    st.write("Gire o modelo em 360°, aplique zoom para observar a inserção dos apêndices ou projete o camarão na bancada pelo celular.")

    aba_ext, aba_int = st.tabs(["🦐 Morfologia Externa (camarao.glb)", "🔬 Estruturas Internas/Detalhadas (camarao_detalhado.glb)"])

    with aba_ext:
        col_3d, col_roteiro = st.columns([2.2, 1])
        with col_3d:
            renderizar_modelo_3d("camarao.glb", "Morfologia Externa - Penaeus vannamei")
        with col_roteiro:
            st.subheader("🎯 Missão de Inspeção 3D")
            st.caption("Marque cada estrutura à medida que a localizar rotacionando o modelo 3D:")
            st.checkbox("Localizar o Rostro denteado na porção anterior")
            st.checkbox("Diferenciar os 5 pares de Pereiópodes torácicos")
            st.checkbox("Observar os 5 pares de Pleópodes abdominais")
            st.checkbox("Inspecionar a articulação do 6º segmento com o Telson")

    with aba_int:
        renderizar_modelo_3d("camarao_detalhado.glb", "Anatomia Detalhada - Penaeus vannamei")

# ==============================================================================
# MÓDULO 3: SIMULADOR DE CASOS CLÍNICOS (APRENDIZAGEM ATIVA - PBL)
# ==============================================================================
elif modulo == "🩺 3. Simulador de Diagnóstico (PBL)":
    st.header("🩺 Simulador de Diagnóstico Clínico em Aquicultura")
    st.write("Aplique os conhecimentos de morfologia para diagnosticar problemas reais em fazendas de camarão e laboratórios de larvicultura.")

    for i, caso in enumerate(CASOS_CLINICOS):
        with st.expander(f"📋 {caso['titulo']}", expanded=(i == 0)):
            st.markdown(f"**Cenário de Campo:** {caso['cenario']}")
            resposta_caso = st.radio(
                caso["pergunta"],
                caso["opcoes"],
                key=f"caso_{i}",
                index=None
            )
            if resposta_caso:
                if caso["opcoes"].index(resposta_caso) == caso["correta"]:
                    st.success(f"✅ {caso['explicacao']}")
                else:
                    st.error("❌ Diagnóstico incorreto. Reavalie a relação entre o sinal morfológico descrito e a função do órgão.")

# ==============================================================================
# MÓDULO 4: MODO DESAFIO (QUIZ GAMIFICADO DE 15 QUESTÕES)
# ==============================================================================
elif modulo == "🎮 4. Modo Desafio (Quiz 15 Questões)":
    st.header("🎮 Modo Desafio: Avaliação de Morfologia de Crustáceos")
    st.write("Responda às 15 questões para testar seu domínio antes da prova prática de laboratório.")

    if "respostas_quiz" not in st.session_state:
        st.session_state.respostas_quiz = {}

    respondidas = len(st.session_state.respostas_quiz)
    st.progress(respondidas / len(QUESTOES_QUIZ), text=f"Progresso: {respondidas}/{len(QUESTOES_QUIZ)} questões respondidas")

    acertos = 0
    for idx, item in enumerate(QUESTOES_QUIZ):
        st.markdown(f"#### {item['q']}")
        escolha = st.radio(
            "Selecione a alternativa correta:",
            item["opts"],
            key=f"quiz_q_{idx}",
            index=None
        )
        if escolha:
            st.session_state.respostas_quiz[idx] = escolha
            if item["opts"].index(escolha) == item["ans"]:
                acertos += 1
                st.success(f"✔️ **Correto!** {item['exp']}")
            else:
                correta_txt = item["opts"][item["ans"]]
                st.error(f"❌ **Incorreto.** A resposta certa é **{correta_txt}**. {item['exp']}")
        st.markdown("---")

    if respondidas == len(QUESTOES_QUIZ):
        nota = (acertos / len(QUESTOES_QUIZ)) * 10
        st.subheader(f"🏆 Resultado Final: {acertos}/15 acertos (Nota: {nota:.1f})")
        if acertos >= 13:
            st.balloons()
            st.success("🌟 **Nível Especialista em Carcinologia!** Você está 100% preparado para a aula prática.")
        elif acertos >= 9:
            st.info("👍 **Bom Desempenho!** Revise apenas os detalhes de apêndices e sistemas internos no Atlas 2D.")
        else:
            st.warning("📚 **Continue Praticando!** Utilize o Mapa Mental e o Atlas 2D para reforçar a função de cada tagma.")

# ==============================================================================
# MÓDULO 5: MAPA MENTAL & TABELA COMPARATIVA TAXONÔMICA
# ==============================================================================
elif modulo == "🧠 5. Mapa Mental & Roteiro de Bancada":
    st.header("🧠 Síntese Estrutural & Comparativo Taxonômico")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
        <div class="stCard">
            <h4>1. Tagma: Cefalotórax (Fusão Cabeça + Tórax)</h4>
            <ul>
                <li><strong>Sensorial:</strong> Olhos compostos pedunculados, Antênulas (com estatocisto) e Antenas (com escafocerito).</li>
                <li><strong>Bucal:</strong> Mandíbulas, Maxílulas, Maxilas e 3 pares de Maxilípedes.</li>
                <li><strong>Locomoção Torácica:</strong> 5 pares de Pereiópodes (3 primeiros pares quelados em <em>P. vannamei</em>).</li>
                <li><strong>Órgãos Internos:</strong> Hepatopâncreas, Coração dorsal, Dendrobrânquias e Glândula Antenal.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
        <div class="stCard">
            <h4>2. Tagma: Abdômen (Pleón) & Leque Caudal</h4>
            <ul>
                <li><strong>Segmentação:</strong> 6 somitos musculares revestidos por pleuras laterais.</li>
                <li><strong>Locomoção Natatória:</strong> 5 pares de Pleópodes birremes.</li>
                <li><strong>Dimorfismo Sexual:</strong> Macho com <em>Petasma</em> (1º pleópode) | Fêmea com <em>Télico aberto</em> (tórax ventral).</li>
                <li><strong>Propulsão de Fuga:</strong> Telson central pontiagudo + 2 pares de Urópodes formando o leque caudal.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📊 Diferenciação Prática em Laboratório: Peneídeos vs. Carídeos")
    st.table({
        "Característica Anatômica": [
            "Subordem",
            "Pereiópodes Quelados (Pinças)",
            "Pleura do 2º Segmento Abdominal",
            "Tipo de Brânquia",
            "Comportamento Reprodutivo"
        ],
        "Camarão Marinho (Penaeus vannamei)": [
            "Dendrobranchiata",
            "Nos 3 primeiros pares (1º, 2º e 3º)",
            "Sobrepõe apenas o 3º segmento",
            "Dendrobrânquia (ramificada)",
            "Desova livre na água (não incuba ovos no abdômen)"
        ],
        "Camarão da Malásia (Macrobrachium rosenbergii)": [
            "Pleocyemata (Infraordem Caridea)",
            "Apenas nos 2 primeiros pares (1º e 2º)",
            "Expandida: sobrepõe o 1º e o 3º segmento",
            "Filobrânquia (lamelar)",
            "Fêmea incuba os ovos aderidos aos pleópodes"
        ]
    })