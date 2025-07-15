import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Corretor de Provas", layout="wide")

st.title("📚 Corretor de Provas - Concurso")

# Campos iniciais
nome_usuario = st.text_input("Digite seu nome:")
nome_prova = st.text_input("Digite o nome da prova:")

# Upload do PDF
pdf_file = st.file_uploader("📂 Faça upload do PDF com questões e gabarito", type=["pdf"])

# Simulação de gabarito (pode melhorar com OCR depois)
st.write("**Exemplo de gabarito:** 1-A, 2-B, 3-C ...")
gabarito_text = st.text_area("Cole o gabarito aqui:")

# Respostas do usuário
respostas_text = st.text_area("Digite suas respostas (Ex: 1-A, 2-B, 3-C)")

if st.button("✅ Corrigir"):
    if not gabarito_text or not respostas_text:
        st.warning("Por favor, insira o gabarito e suas respostas.")
    else:
        # Processar texto em dicionário
        gabarito = dict(item.split("-") for item in gabarito_text.replace(" ", "").split(","))
        respostas = dict(item.split("-") for item in respostas_text.replace(" ", "").split(","))

        questoes = sorted(gabarito.keys(), key=int)
        acertos = 0
        resultados = []

        for q in questoes:
            resp_certa = gabarito[q].upper()
            resp_user = respostas.get(q, "").upper()
            correto = resp_certa == resp_user
            resultados.append([q, resp_user, resp_certa, "✔️" if correto else "❌"])
            if correto:
                acertos += 1

        total = len(questoes)
        perc = round((acertos / total) * 100, 2)
        st.success(f"🎯 Você acertou {acertos} de {total} questões. Desempenho: {perc}%")

        df = pd.DataFrame(resultados, columns=["Questão", "Sua Resposta", "Gabarito", "Status"])
        st.dataframe(df)

        # Botão para baixar Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Resultados')
        st.download_button("📥 Baixar Excel", data=output.getvalue(), file_name="resultado.xlsx")

        # Botão para baixar PDF
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
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        st.download_button("📥 Baixar PDF", data=pdf_output.getvalue(), file_name="relatorio.pdf")
