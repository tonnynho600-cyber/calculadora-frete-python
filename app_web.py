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
    try:
        location = geolocator.geocode(f"{cidade}, {uf}, Brazil")
        if location:
            return (location.latitude, location.longitude)
    except:
        return None
    return None

st.set_page_config(page_title="Sistema Logístico Pro", layout="wide")
st.title("🚚 Calculadora de Frete Inteligente")

# Seletor de Tipo de Entrada
metodo_busca = st.radio("Selecione o método de busca:", ["Por CEP", "Por Cidade/UF"], horizontal=True)

with st.container():
    col1, col2, col3 = st.columns(3)
    
    if metodo_busca == "Por CEP":
        with col1:
            origem_input = st.text_input("CEP Origem (ex: 01001000)")
        with col2:
            destino_input = st.text_input("CEP Destino (ex: 30140010)")
    else:
        with col1:
            origem_input = st.text_input("Cidade Origem (ex: São Paulo)")
            uf_origem_input = st.text_input("UF Origem (ex: SP)", max_chars=2).upper()
        with col2:
            destino_input = st.text_input("Cidade Destino (ex: Belo Horizonte)")
            uf_destino_input = st.text_input("UF Destino (ex: MG)", max_chars=2).upper()
            
    with col3:
        valor_carga = st.number_input("Valor da Carga (R$)", min_value=0.0)

if st.button("Analisar Rota e Frete"):
    cid_origem, uf_origem = None, None
    cid_destino, uf_destino = None, None

    with st.spinner('Processando localização...'):
        if metodo_busca == "Por CEP":
            if origem_input and destino_input:
                cid_origem, uf_origem = buscar_cep(origem_input)
                cid_destino, uf_destino = buscar_cep(destino_input)
        else:
            if origem_input and uf_origem_input and destino_input and uf_destino_input:
                cid_origem, uf_origem = origem_input, uf_origem_input
                cid_destino, uf_destino = destino_input, uf_destino_input

        if cid_origem and cid_destino and valor_carga > 0:
            coord_origem = obter_coordenadas(cid_origem, uf_origem)
            coord_destino = obter_coordenadas(cid_destino, uf_destino)

            if coord_origem and coord_destino:
                distancia = geodesic(coord_origem, coord_destino).km * 1.2
                prazo = int(distancia / 300) + 1
                custo_km = distancia * 2.50
                ad_valorem = valor_carga * 0.01
                frete_total = custo_km + ad_valorem
                percentual = (frete_total / valor_carga) * 100

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
                st.error("Não foi possível encontrar as coordenadas para esses locais.")
        else:
            st.warning("Verifique se os dados de origem/destino e o valor da carga estão corretos.")