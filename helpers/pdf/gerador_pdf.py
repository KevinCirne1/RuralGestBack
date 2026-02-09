from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os

def gerar_pdf_solicitacao(solicitacao, tipo_doc, nome_arquivo):
    """
    Gera um ficheiro PDF físico com os dados da solicitação.
    Salva na pasta 'documentos_gerados' (cria se não existir).
    """
    # Garante que a pasta existe
    output_folder = "documentos_gerados"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    caminho_completo = os.path.join(output_folder, nome_arquivo)
    
    c = canvas.Canvas(caminho_completo, pagesize=A4)
    width, height = A4
    
    # --- Cabeçalho ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "Prefeitura Municipal de Pirpirituba")
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, height - 2.8*cm, "Secretaria de Agricultura - RuralGest")
    
    c.line(2*cm, height - 3.2*cm, 19*cm, height - 3.2*cm)
    
    # --- Título ---
    c.setFont("Helvetica-Bold", 14)
    titulo = "PROTOCOLO DE SOLICITAÇÃO" if tipo_doc == "PROTOCOLO" else "RELATÓRIO DE CONCLUSÃO DE SERVIÇO"
    c.drawCentredString(width / 2, height - 5*cm, titulo)
    doc_num = solicitacao.agricultor.numero_documento if solicitacao.agricultor.numero_documento else "Não Informado"
    # --- Dados ---
    c.setFont("Helvetica", 12)
    y = height - 7*cm
    
    def escrever_linha(label, valor):
        nonlocal y
        c.drawString(2.5*cm, y, f"{label}: {valor}")
        y -= 1*cm

    escrever_linha("Protocolo Nº", str(solicitacao.id))
    escrever_linha("Data", solicitacao.data_solicitacao.strftime("%d/%m/%Y"))
    escrever_linha("Agricultor", solicitacao.agricultor.nome)
    escrever_linha("CPF", solicitacao.agricultor.cpf)
    escrever_linha("Nº Documento/Residência", doc_num)
    escrever_linha("Propriedade", solicitacao.propriedade.terreno)
    escrever_linha("Serviço Solicitado", solicitacao.servico.nome_servico)
    escrever_linha("Status Atual", solicitacao.status)
    
    if solicitacao.operador:
        escrever_linha("Técnico Responsável", solicitacao.operador.nome)
    
    if tipo_doc == "RELATORIO_FINAL":
        y -= 1*cm
        c.drawString(2.5*cm, y, "Declaro que o serviço foi executado conforme solicitado.")
        
        # Linha de assinatura
        y -= 4*cm
        c.line(5*cm, y, 16*cm, y)
        c.drawCentredString(width / 2, y - 0.5*cm, "Assinatura do Agricultor")
    
    # --- Rodapé ---
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(2*cm, 2*cm, f"Gerado automaticamente pelo sistema RuralGest.")
    c.drawString(2*cm, 1.5*cm, f"Hash de Segurança: {str(solicitacao.id * 12345)}") # Simulação de hash
    
    c.save()
    return caminho_completo