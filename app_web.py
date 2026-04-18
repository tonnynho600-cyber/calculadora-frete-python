import streamlit as st
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import requests

# Função para buscar cidade pelo CEP (ViaCEP)
def buscar_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        if "erro" not in dados:
            return dados['localidade'], dados['uf']
    return None, None

# Função para obter coordenadas (Latitude e Longitude)
def obter_coordenadas(cidade, uf):
    geolocator = Nominatim(user_agent="calculadora_frete_log")
    location = geolocator.geocode(f"{cidade}, {uf}, Brazil")
    if location:
        return (location.latitude, location.longitude)
    return None

st.set_page_config(page_title="Sistema Logístico Pro", layout="wide")
st.markdown("---")

st.title("🚚 Calculadora de Frete Inteligente")
st.subheader("Cálculo Automático por CEP e Análise de Rota")

# Entradas
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        cep_origem = st.text_input("CEP Origem (ex: 01001000)")
    with col2:
        cep_destino = st.text_input("CEP Destino (ex: 30140010)")
    with col3:
        valor_carga = st.number_input("Valor da Carga (R$)", min_value=0.0)

if st.button("Analisar Rota e Frete"):
    if cep_origem and cep_destino and valor_carga > 0:
        with st.spinner('Buscando rotas e cidades...'):
            # Buscar cidades
            cid_origem, uf_origem = buscar_cep(cep_origem)
            cid_destino, uf_destino = buscar_cep(cep_destino)

            if cid_origem and cid_destino:
                # Coordenadas para calcular distância
                coord_origem = obter_coordenadas(cid_origem, uf_origem)
                coord_destino = obter_coordenadas(cid_destino, uf_destino)

                if coord_origem and coord_destino:
                    # Distância Geodésica (Linha reta) + Margem de 20% para rodovia
                    distancia = geodesic(coord_origem, coord_destino).km * 1.2
                    
                    # Lógica de Prazo (Ex: 1 dia a cada 300km + 1 dia fixo)
                    prazo = int(distancia / 300) + 1

                    # Cálculos Financeiros
                    custo_km = distancia * 2.50
                    ad_valorem = valor_carga * 0.01
                    frete_total = custo_km + ad_valorem
                    percentual = (frete_total / valor_carga) * 100

                    # Resultados
                    st.divider()
                    res1, res2, res3 = st.columns(3)
                    res1.info(f"**Origem:** {cid_origem} - {uf_origem}")
                    res2.info(f"**Destino:** {cid_destino} - {uf_destino}")
                    res3.warning(f"**Prazo Estimado:** {prazo} dias úteis")

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Distância (estimada)", f"{distancia:.0f} km")
                    m2.metric("Total do Frete", f"R$ {frete_total:.2f}")
                    m3.metric("Representatividade", f"{percentual:.2f}%")
                else:
                    st.error("Erro ao converter cidades em coordenadas.")
            else:
                st.error("Um ou ambos os CEPs não foram encontrados.")
    else:
        st.warning("Preencha todos os campos corretamente.")