import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Corretor de Provas - Avançado", layout="wide")

st.title("📚 Corretor de Provas - Concurso")

# Informações do usuário
nome_usuario = st.text_input("Digite seu nome:")
nome_prova = st.text_input("Digite o nome da prova:")

# Upload PDF
pdf_file = st.file_uploader("📂 Faça upload do PDF com questões e gabarito", type=["pdf"])

st.write("**Exemplo de gabarito:** 1-A, 2-B, 3-C ...")
gabarito_text = st.text_area("Cole o gabarito aqui:")

respostas_text = st.text_area("Digite suas respostas (Ex: 1-A, 2-B, 3-C)")

if st.button("✅ Corrigir"):
    if not gabarito_text or not respostas_text:
        st.warning("Por favor, insira o gabarito e suas respostas.")
    else:
        gabarito = dict(item.split("-") for item in gabarito_text.replace(" ", "").split(","))
        respostas = dict(item.split("-") for item in respostas_text.replace(" ", "").split(","))

        questoes = sorted(gabarito.keys(), key=int)
        acertos = 0
        erros = 0
        resultados = []

        for q in questoes:
            resp_certa = gabarito[q].upper()
            resp_user = respostas.get(q, "").upper()
            correto = resp_certa == resp_user
            resultados.append([q, resp_user, resp_certa, "✔️" if correto else "❌"])
            if correto:
                acertos += 1
            else:
                erros += 1

        total = len(questoes)
        perc = round((acertos / total) * 100, 2)

        st.success(f"🎯 Você acertou {acertos} de {total} questões. Desempenho: {perc}%")

        df = pd.DataFrame(resultados, columns=["Questão", "Sua Resposta", "Gabarito", "Status"])
        st.dataframe(df)

        # Gráfico de pizza
        fig, ax = plt.subplots()
        ax.pie([acertos, erros], labels=['Acertos', 'Erros'], autopct='%1.1f%%', colors=['green', 'red'])
        ax.axis('equal')
        st.pyplot(fig)

        # Recomendações básicas
        if erros > 0:
            st.warning(f"🔍 Você errou {erros} questões. Recomenda-se revisar os tópicos dessas questões.")

        # Botão Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
        st.download_button("📥 Baixar Excel", data=output.getvalue(), file_name="resultado.xlsx")

        # PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Relatório de Desempenho - {nome_usuario}", ln=True, align='C')
        pdf.cell(200, 10, f"Prova: {nome_prova}", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, f"Acertos: {acertos}/{total} ({perc}%)", ln=True)
        pdf.ln(5)
        for row in resultados:
            pdf.cell(200, 10, f"Q{row[0]} - Sua: {row[1]} | Gabarito: {row[2]} | {row[3]}", ln=True)
        if erros > 0:
            pdf.ln(10)
            pdf.cell(200, 10, "Sugestão: Revisar os tópicos das questões erradas.", ln=True)
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        st.download_button("📥 Baixar PDF", data=pdf_output.getvalue(), file_name="relatorio.pdf")
