# Iniciando app no streamlit
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd


st.set_page_config(page_title="Análise de Emendas Parlamentares", page_icon=":bar_chart:", layout="wide")
st.markdown("<h1 style='text-align: center;'>Análise de Emendas Parlamentares</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style="font-size: 16px;">
    Os dados apresentados foram extraídos do portal de dados abertos do <b>Governo Federal</b> e foram atualizados no dia <b>25 de março</b>. 
    A análise contempla informações sobre emendas parlamentares.
    </p>
    """,
    unsafe_allow_html=True
)

base = pd.read_csv('emendas_tratadas.csv', sep=';', encoding='utf-8')

# Tratamento da data e valores
base['Data'] = pd.to_datetime(base['Data'], format='%Y-%m-%d', errors='coerce')
base['Valor Pago'] = base['Valor Pago'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.replace('-', '', regex=False).replace('', '0').astype(float)
base['Mes'] = base['Data'].dt.month
base['Ano'] = base['Data'].dt.year

# Filtro de ano
ano = 2025

# Configurações do Streamlit
# Configuração do menu lateral
st.sidebar.title("Menu de Navegação")
st.sidebar.markdown(
    """
    <p style="font-size: 14px;">
    Utilize o menu abaixo para navegar entre as análises disponíveis.
    </p>
    """,
    unsafe_allow_html=True
)

# Adicionando o seletor de página
pagina = st.sidebar.radio("Selecione a Página", ["Análise Por Autor de Emenda"])

# Informações do autor do projeto
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <p style="font-size: 14px; font-weight: bold;">Desenvolvido por Christian Basilio Oliveira</p>
        <a href="https://www.linkedin.com/in/christianbasilioo/" target="_blank" style="font-size: 12px; color: #0077b5; text-decoration: none;">
            Meu LinkedIn
        </a>
        <p style="font-size: 12px; margin-top: 5px;">Email: <a href="mailto:christian.basilio@example.com" style="color: #0077b5; text-decoration: none;">christian.basilio@example.com</a></p>
    </div>
    """,
    unsafe_allow_html=True
)


if pagina == "Análise Por Autor de Emenda":
    st.write("----")
    # Filtro de autor
    col_seletor1, col_seletor2 = st.columns(2)

    with col_seletor1:
        autor = st.selectbox("Selecione o Autor da Emenda", sorted(base['Autor da Emenda'].unique()), index=sorted(base['Autor da Emenda'].unique()).index("BANCADA DO RIO DE JANEIRO"))

    with col_seletor2:
        grafico_selecionado = st.selectbox(
            "Escolha o tipo de gráfico:",
            ["Órgão e Ação Orçamentária", 'Programa Orçamentário', "Estado Favorecido", "Função Orçamentária", 'Subfunção (Especificação da Área de Atuação)']
        )

    base_autor = base[base['Autor da Emenda'] == autor]

    # Card dinâmico baseado no filtro (versão menor)
    total_pago_autor = base_autor['Valor Pago'].sum()
    total_pago_autor_milhoes = total_pago_autor / 1e6
    st.markdown(
        f"""
        <div style="
            background-color: transparent;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin: 0 auto; /* Centraliza horizontalmente */
            margin-bottom: 10px;
            width: 50%; /* Define o tamanho pela metade */
        ">
            <p style="font-size: 24px; font-weight: bold; color: #4CAF50; margin: 0;">R$ {total_pago_autor_milhoes:,.2f} bilhões</p>
            <p style="font-size: 12px; color: white; margin-top: 3px;">Baseado nos filtros selecionados</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if grafico_selecionado == "Órgão e Ação Orçamentária":
        # Supondo que base_autor já esteja carregado
        sunburst_data = base_autor.groupby([
                'Órgão', 
                'Ação Orçamentária', 
                'Função (Área de Atuação)', 
                'Subfunção (Especificação da Área de Atuação)'
        ]).agg({'Valor Pago': 'sum'}).reset_index()

        st.markdown(f"<h3 style='text-align: center; font-size: 24px;'>Órgão e Ação Orçamentária de {autor} no ano {ano}</h3>", unsafe_allow_html=True)

        fig4 = px.icicle(
            sunburst_data,
            path=[
                'Órgão', 
                'Ação Orçamentária', 
                'Função (Área de Atuação)', 
                'Subfunção (Especificação da Área de Atuação)'
            ],
            values='Valor Pago',
            color='Órgão',  # Adiciona cores distintas para cada órgão
            color_continuous_scale='Viridis'  # Escolhe uma escala de cores
        )

        fig4.update_traces(
            hovertemplate='<b>Órgão:</b> %{parent}<br>' +
                        '<b>Ação Orçamentária:</b> %{label}<br>' +
                        '<b>Valor Pago:</b> R$ %{value:,.2f}<extra></extra>',
            textinfo='label+value+percent entry',
            textfont_size=16,
            textposition='middle center'
        )

        fig4.update_layout(
            title='Distribuição de Valores Pagos por Órgão e Ação Orçamentária',
            margin=dict(t=50, l=10, r=10, b=10),
            font=dict(family="Arial", size=14),
            paper_bgcolor='rgba(0,0,0,0)',
            height=600,
            clickmode='event+select',  # Permite interação clicável
            legend_title_text='Órgão'  # Adiciona título à legenda
        )

        st.plotly_chart(fig4, use_container_width=True)

    elif grafico_selecionado == "Estado Favorecido":
        st.markdown(f"<h3 style='text-align: center;'>Estado Favorecido por {autor} no ano {ano}</h3>", unsafe_allow_html=True)
        ufagg_autor = base_autor.groupby('UF DO FAVORECIDO').agg({'Valor Pago': 'sum'}).reset_index()
        # carregando mapa BR_UF_2023.shp# Formatando para moeda

        fig3 = px.bar(ufagg_autor, x='UF DO FAVORECIDO', y='Valor Pago', text='Valor Pago')
        fig3.update_traces(hovertemplate='R$ %{y:,.2f}', texttemplate='R$ %{text:,.2f}')
        fig3.update_layout(
            margin=dict(t=50),
            font=dict(family="Arial", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, zeroline=False),
        )
        st.plotly_chart(fig3, use_container_width=True)


    elif grafico_selecionado == "Função Orçamentária":
        funcao_autor = base.groupby(['Função (Área de Atuação)', 'Autor da Emenda'])['Valor Pago'].sum().sort_values(ascending=False).reset_index()
        funcao_autor['Função (Área de Atuação)'] = funcao_autor['Função (Área de Atuação)'].str[5:]  # Removendo prefixo
        funcao_autor = funcao_autor[funcao_autor['Autor da Emenda'] == autor]  # Filtrando pelo autor
        st.markdown(f"<h3 style='text-align: center;'>Função Orçamentária de {autor} no ano {ano}</h3>", unsafe_allow_html=True)
        fig5 = px.bar(funcao_autor, x='Função (Área de Atuação)', y='Valor Pago', text='Valor Pago')
        fig5.update_traces(hovertemplate='R$ %{y:,.2f}', texttemplate='R$ %{text:,.2f}')
        fig5.update_layout(
            margin=dict(t=50),
            font=dict(family="Arial", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, zeroline=False),
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    elif grafico_selecionado == "Subfunção (Especificação da Área de Atuação)":
        subfuncao_autor = base.groupby(['Subfunção (Especificação da Área de Atuação)', 'Autor da Emenda'])['Valor Pago'].sum().sort_values(ascending=False).reset_index()
        subfuncao_autor['Subfunção (Especificação da Área de Atuação)'] = subfuncao_autor['Subfunção (Especificação da Área de Atuação)'].str[6:]  # Aplicando filtro nas palavras de subfunção
        subfuncao_autor = subfuncao_autor[subfuncao_autor['Autor da Emenda'] == autor]  # Filtrando pelo autor
        st.markdown(f"<h3 style='text-align: center;'>Subfunção Orçamentária de {autor} no ano {ano}</h3>", unsafe_allow_html=True)
        fig6 = px.bar(subfuncao_autor, x='Subfunção (Especificação da Área de Atuação)', y='Valor Pago', text='Valor Pago')
        fig6.update_traces(hovertemplate='R$ %{y:,.2f}', texttemplate='R$ %{text:,.2f}')
        fig6.update_layout(
            margin=dict(t=50),
            font=dict(family="Arial", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, zeroline=False),
        )
        st.plotly_chart(fig6, use_container_width=True)
    elif grafico_selecionado == "Programa Orçamentário":
        programa_autor = base_autor.groupby('Programa Orçamentário').agg({'Valor Pago': 'sum'}).reset_index()
        programa_autor['Programa Orçamentário'] = programa_autor['Programa Orçamentário'].str[6:]  # Filtrando a coluna
        fig7 = px.pie(
            programa_autor, 
            names='Programa Orçamentário', 
            values='Valor Pago', 
            hole=0.4,  # Define o gráfico como rosca
            title=f"Distribuição por Programa Orçamentário de {autor} no ano {ano}"
        )
        fig7.update_traces(
            hovertemplate='<b>%{label}</b><br>Valor Pago: R$ %{value:,.2f}<br>Percentual: %{percent}',
            textinfo='percent+label',
            textfont_size=8,
            showlegend=False  # Remove as legendas
        )
        fig7.update_layout(
            margin=dict(t=50),
            font=dict(family="Arial", size=7),  # Ajustando o tamanho da fonte
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig7, use_container_width=True)


# Mostrando a base
st.subheader("Base de Dados e Documentos Sem Filtros")
st.dataframe(base, use_container_width=True)

# colocando __main__ para rodar o app
if __name__ == "__main__":
    st.write("----")
    st.markdown(
        """
        <p style="font-size: 12px; text-align: center;">
        Este aplicativo foi desenvolvido para fins educacionais e de análise de dados. 
        Os dados utilizados são de domínio público e foram extraídos do portal de dados abertos do Governo Federal.
        </p>
        """,
        unsafe_allow_html=True
    )
    #