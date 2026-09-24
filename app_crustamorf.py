import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from PIL import Image

# Configuração da Página
st.set_page_config(page_title="CrustaMorf - Atlas de Morfologia", page_icon="🦐", layout="wide")

# Inicialização de estado para o Quiz
if 'pontuacao' not in st.session_state:
    st.session_state.pontuacao = 0
if 'quiz_enviado' not in st.session_state:
    st.session_state.quiz_enviado = False

# Cabeçalho Principal
st.title("🦐 CrustaMorf: Plataforma de Morfologia de Crustáceos")
st.markdown("**Universidade Federal Rural de Pernambuco (UFRPE) | Engenharia de Pesca**")
st.markdown("---")

# Menu de Navegação em Abas Superiores / Rádio Lateral
menu = st.sidebar.radio("Navegação do Aplicativo", [
    "📖 Atlas 2D (Completo)", 
    "🧊 3D - Morfologia Externa", 
    "🔬 3D - Estruturas Detalhadas", 
    "🎮 Modo Desafio (Quiz 15 Q)", 
    "🧠 Mapa Mental de Estudos"
])

# Banco de Dados Morfológico Completo
morfologia_db = {
    "Rostro": "Extensão rígida e serrilhada frontal da carapaça. Atua na defesa mecânica e na estabilização hidrodinâmica durante a natação.",
    "Cefalotórax": "Região anterior fusionada (cabeça + tórax) protegida pela carapaça quitinosa. Abriga os principais órgãos vitais (coração, estômago, hepatopâncreas e brânquias).",
    "Abdômen": "Região posterior segmentada em pleômeros musculares. É a principal estrutura de interesse comercial e zootécnico na carcinicultura (a 'carne' do camarão).",
    "Pereiópodes": "Apêndices torácicos (10 patas). Os primeiros pares possuem pinças (quelas) para captura de alimento e defesa; os demais auxiliam na locomoção no fundo.",
    "Pleópodes": "Apêndices abdominais birremes utilizados ativamente para a natação contínua e fixação de ovos nas fêmeas ovígeras.",
    "Telson e Urópodes": "Formam coletivamente o leque caudal. Utilizados no reflexo de escape rápido (natação de fuga para trás por propulsão mecânica).",
    "Antenas e Antênulos": "Apêndices sensoriais cefálicos longos e curtos, respetivamente, responsáveis pela quimiorrecepção, tato e equilíbrio.",
    "Hepatopâncreas": "Órgão glandular interno multiespecializado, responsável pela digestão, absorção de nutrientes, armazenamento de reservas e desintoxicação.",
    "Brânquias": "Órgãos respiratórios foliáceos localizados na cavidade branquial lateral do cefalotórax, essenciais para as trocas gasosas."
}

# Caminho base para os arquivos locais
pasta_atual = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------
# 1. ATLAS 2D (COMPLETO)
# -------------------------------------------------------------
if menu == "📖 Atlas 2D (Completo)":
    st.header("Atlas Morfológico 2D – *Penaeus vannamei*")
    st.markdown("Visualize a ilustração anatômica completa e consulte a lista detalhada das estruturas ao lado.")
    
    col_img, col_lista = st.columns([1.5, 1])
    
    with col_img:
        caminho_2d = os.path.join(pasta_atual, "camarao.jpg")
        try:
            img = Image.open(caminho_2d)
            st.image(img, caption="Ilustração Anatômica Externa e Detalhada", use_container_width=True)
        except FileNotFoundError:
            st.error("⚠️ Arquivo 'camarao.jpg' não encontrado na pasta do projeto.")
            
    with col_lista:
        st.subheader("📋 Lista Morfológica e Funções")
        for est, desc in morfologia_db.items():
            with st.expander(f"📌 {est}"):
                st.write(desc)

# -------------------------------------------------------------
# 2. 3D - MORFOLOGIA EXTERNA
# -------------------------------------------------------------
elif menu == "🧊 3D - Morfologia Externa":
    st.header("Visualizador 3D: Morfologia Externa")
    st.markdown("Interaja livremente: **Gaste o mouse para girar**, **role para aproximar (zoom)** e clique e arraste para mudar o ângulo.")
    
    col_3d, col_info = st.columns([1.6, 1])
    
    with col_3d:
        caminho_3d1 = os.path.join(pasta_atual, "camarao.glb")
        try:
            with open(caminho_3d1, "rb") as f:
                b64_1 = base64.b64encode(f.read()).decode("utf-8")
            
            html_viewer1 = f"""
                <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.1.1/model-viewer.min.js"></script>
                <model-viewer src="data:model/gltf-binary;base64,{b64_1}" 
                    alt="Modelo 3D Externo" auto-rotate camera-controls shadow-intensity="1" 
                    style="width: 100%; height: 500px; background-color: #f0f2f6; border-radius: 12px;">
                </model-viewer>
            """
            components.html(html_viewer1, height=520)
        except FileNotFoundError:
            st.error("⚠️ Arquivo 'camarao.glb' não encontrado. Certifique-se de salvá-lo na pasta.")
            
    with col_info:
        st.subheader("🔍 Guia Externo")
        st.info("Foque sua análise nas regiões de revestimento externo:")
        st.markdown("""
        * **Carapaça:** Proteção do cefalotórax.
        * **Somitos Abdominais:** Articulações flexíveis.
        * **Apêndices Locomotores:** Diferenciação entre pereiópodes e pleópodes.
        * **Leque Caudal:** Mecanismo hidrodinâmico de escape.
        """)
        for k in ["Rostro", "Cefalotórax", "Abdômen", "Pereiópodes", "Pleópodes", "Telson e Urópodes"]:
            with st.expander(k):
                st.write(morfologia_db[k])

# -------------------------------------------------------------
# 3. 3D - ESTRUTURAS DETALHADAS
# -------------------------------------------------------------
elif menu == "🔬 3D - Estruturas Detalhadas":
    st.header("Visualizador 3D: Anatomia Interna / Detalhada")
    st.markdown("Explore camadas internas, órgãos e sistemas de suporte metabólico e respiratório.")
    
    col_3d2, col_info2 = st.columns([1.6, 1])
    
    with col_3d2:
        caminho_3d2 = os.path.join(pasta_atual, "camarao_detalhado.glb")
        try:
            with open(caminho_3d2, "rb") as f:
                b64_2 = base64.b64encode(f.read()).decode("utf-8")
            
            html_viewer2 = f"""
                <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.1.1/model-viewer.min.js"></script>
                <model-viewer src="data:model/gltf-binary;base64,{b64_2}" 
                    alt="Modelo 3D Detalhado" auto-rotate camera-controls shadow-intensity="1" 
                    style="width: 100%; height: 500px; background-color: #eef2f5; border-radius: 12px;">
                </model-viewer>
            """
            components.html(html_viewer2, height=520)
        except FileNotFoundError:
            st.error("⚠️ Arquivo 'camarao_detalhado.glb' não encontrado. Salve-o na pasta do projeto.")
            
    with col_info2:
        st.subheader("🔬 Guia de Órgãos e Sistemas")
        st.info("Estruturas internas de relevância zootécnica e patológica:")
        for k in ["Hepatopâncreas", "Brânquias", "Cefalotórax"]:
            with st.expander(k):
                st.write(morfologia_db[k])

# -------------------------------------------------------------
# 4. MODO DESAFIO (QUIZ COM 15 PERGUNTAS)
# -------------------------------------------------------------
elif menu == "🎮 Modo Desafio (Quiz 15 Q)":
    st.header("Desafio de Morfologia de Crustáceos (15 Questões)")
    st.markdown("Responda todas as perguntas abaixo para testar seu nível de prontidão para as aulas práticas de laboratório.")
    
    questoes = [
        {"p": "Qual estrutura atua como o principal apêndice para a natação contínua no camarão?", "opts": ["Pereiópodes", "Pleópodes", "Antenas", "Rostro"], "certo": "Pleópodes"},
        {"p": "O hepatopâncreas e as brânquias ficam abrigados em qual destas regiões?", "opts": ["Abdômen", "Telson", "Cefalotórax", "Urópodes"], "certo": "Cefalotórax"},
        {"p": "Durante a natação de fuga (reflexo de escape para trás), o camarão utiliza primariamente:", "opts": ["Apenas o Rostro", "Os Pereiópodes", "O leque caudal (Telson + Urópodes)", "Os Pleópodes anteriores"], "certo": "O leque caudal (Telson + Urópodes)"},
        {"p": "Qual é a principal função mecânica do rostro nos peneídeos?", "opts": ["Digestão de alimentos", "Defesa e estabilização hidrodinâmica", "Respiração branquial", "Fixação de ovos"], "certo": "Defesa e estabilização hidrodinâmica"},
        {"p": "Como são tecnicamente chamados os segmentos articulados que compõem o abdômen?", "opts": ["Pleômeros", "Quelípodes", "Quelíceras", "Carapáceas"], "certo": "Pleômeros"},
        {"p": "Qual a principal importância comercial e zootécnica do abdômen?", "opts": ["Filtração de plâncton", "Principal porção muscular consumida e comercializada", "Órgão produtor de hormônios de muda", "Sede do sistema nervoso central"], "certo": "Principal porção muscular consumida e comercializada"},
        {"p": "Os apêndices torácicos chamados pereiópodes exercem funções fundamentais como:", "opts": ["Natação rápida em coluna d'água", "Locomoção bentônica e manipulação de alimento", "Trocas gasosas diretas", "Produção de oócitos"], "certo": "Locomoção bentônica e manipulação de alimento"},
        {"p": "A carapaça rígida dos crustáceos decápodes é endurecida principalmente por:", "opts": ["Queratina e cartilagem", "Quitina impregnada com carbonato de cálcio", "Fibras de celulose pura", "Colágeno desidratado"], "certo": "Quitina impregnada com carbonato de cálcio"},
        {"p": "Qual órgão interno é responsável pela digestão, secreção de enzimas e reserva de nutrientes?", "opts": ["Coração tubular", "Hepatopâncreas", "Gônada imatura", "Brânquia filamentosa"], "certo": "Hepatopâncreas"},
        {"p": "As trocas gasosas (respiração) no camarão ocorrem primordialmente nas:", "opts": ["Brânquias", "Pernas ambulatórias", "Paredes do estômago", "Glândulas verdes"], "certo": "Brânquias"},
        {"p": "O telson e os urópodes combinados formam qual estrutura morfológica de propulsão?", "opts": ["Cadeia ventral", "Leque caudal", "Escafognatito", "MANDÍBULA"], "certo": "Leque caudal"},
        {"p": "Qual par de apêndices cefálicos é mais longo e atua na quimiorrecepção de longo alcance?", "opts": ["Antenas", "Maxilípodes", "Rostro", "Olhos compostos"], "certo": "Antenas"},
        {"p": "Os antênulos situam-se em posição anterior e desempenham papel importante em:", "opts": ["Mastigação pesada", "Equilíbrio e quimiorrecepção fina", "Propulsão de fuga", "Excreção de amônia"], "certo": "Equilíbrio e quimiorrecepção fina"},
        {"p": "O processo de troca periódica do exoesqueleto para permitir o crescimento do animal chama-se:", "opts": ["Metamorfose incompleta", "Ecdise (Muda)", "Encistamento", "Osmorregulação"], "certo": "Ecdise (Muda)"},
        {"p": "Qual estrutura ocular abriga o complexo neurossecretor que controla o ciclo de muda?", "opts": ["Cônica córnea", "Pedúnculo ocular (Órgão X / Glândula do seio)", "Cristalino óptico", "Retina distal"], "certo": "Pedúnculo ocular (Órgão X / Glândula do seio)"}
    ]
    
    with st.form("form_quiz_15"):
        respostas = []
        for i, q in enumerate(questoes):
            st.markdown(f"**Questão {i+1}: {q['p']}**")
            r = st.radio("Escolha a alternativa:", q["opts"], key=f"q_{i}", index=None)
            respostas.append(r)
            st.markdown("---")
            
        enviado = st.form_submit_button("Finalizar e Corrigir Prova")
        
        if enviado:
            acertos = sum(1 for i, r in enumerate(respostas) if r == questoes[i]["certo"])
            st.session_state.pontuacao = acertos
            st.session_state.quiz_enviado = True

    if st.session_state.quiz_enviado:
        pts = st.session_state.pontuacao
        st.subheader("📊 Resultado do Desafio")
        if pts >= 12:
            st.balloons()
            st.success(f"🏆 Excelente! Você acertou {pts} de 15 questões. Domínio total da morfologia!")
        elif pts >= 8:
            st.warning(f"👍 Bom desempenho! Você acertou {pts} de 15. Vale a pena revisar os modelos 3D e o Atlas 2D.")
        else:
            st.error(f"📚 Você acertou {pts} de 15. Recomendamos uma revisão detalhada no material de estudo.")

# -------------------------------------------------------------
# 5. MAPA MENTAL DE ESTUDOS
# -------------------------------------------------------------
elif menu == "🧠 Mapa Mental de Estudos":
    st.header("Mapa Mental: Morfologia e Biologia de Crustáceos")
    st.markdown("Esquema estruturado para revisão rápida de conteúdos cobrados na Engenharia de Pesca.")
    
    st.markdown("""
    O diagrama interativo abaixo sintetiza os eixos de estudo da disciplina:
    """)
    
    # Renderização de Mapa Mental via Mermaid integrado no Streamlit
    mapa_mermaid = """
    ```mermaid
    graph TD
        A[Morfologia de Crustáceos<br>Penaeus vannamei] --> B[Tagmatização]
        A --> C[Sistema Orgânico Interno]
        A --> D[Importância Zootécnica]
        
        B --> B1[Cefalotórax]
        B --> B2[Abdômen / Pleômeros]
        B --> B3[Apêndices]
        
        B1 --> B1a[Rostro & Carapaça]
        B1 --> B1b[Olhos Compostos]
        
        B3 --> B3a[Pereiópodes: Locomoção]
        B3 --> B3b[Pleópodes: Natação]
        B3 --> B3c[Leque Caudal: Fuga]
        
        C --> C1[Hepatopâncreas: Digestão/Reserva]
        C --> C2[Brânquias: Respiração]
        C --> C3[Sistema Endócrino: Muda/Ecdise]
        
        D --> D1[Carcinicultura Comercial]
        D --> D2[Processamento de Filés/Caldas]
    ```
    """
    st.markdown(mapa_mermaid)
    
    st.success("💡 Dica de Estudo: Utilize este mapa mental como guia mestre antes de iniciar as sessões práticas no laboratório de hidrobiologia.")