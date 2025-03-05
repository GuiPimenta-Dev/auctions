import datetime
import json
from dataclasses import dataclass
from . import utils
from . import excel
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

@dataclass
class Input:
    pass

@dataclass
class Output:
    message: str


def lambda_handler(event, context):
    
    pa_has = utils.consulta_pressao_vista()
    consulta_has = utils.consulta_de_hipertensao()
    hb_glic = utils.consulta_hemoglobina_glicada()
    consulta_dm = utils.consulta_diabetes()
    consulta_pn = utils.consulta_gestantes()
    exames_pn = utils.exame_gestante()
    vacina = utils.vacina_crianca()
  
    todos = {
        "PA HAS": pa_has,
        "Consulta HAS": consulta_has,
        "Hb Glic": hb_glic,
        "Consulta DM": consulta_dm,
        "Consulta PN": consulta_pn,
        "Exames PN": exames_pn,
        "Vacina": vacina
    }
    excel.save_to_excel(todos)
    
    nao_atende = {
        "PA HAS": [item for item in pa_has if item["atende_indicador"] == "Não"],
        "Consulta HAS": [item for item in consulta_has if item["consulta_semestre"] == "Não"],
        "Hb Glic": [item for item in hb_glic if item["atende_indicador"] == "Não"],
        "Consulta DM": [item for item in consulta_dm if item["consulta_semestre"] == "Não"],
        "Consulta PN": [item for item in consulta_pn if item["atende_indicador_1"] == "Não"],
        "Exames PN": [item for item in exames_pn if item["atende_indicador_2"] == "Não"],
        "Vacina": [item for item in vacina if item["atende_indicador_5"] == "Não"]
    }
    
    html_content = "<html><body>"
    html_content += "<h2>Relatório de Pacientes Com Indicadores Não Atendidos</h2>"

    nomes = {
        "PA HAS": "nome",
        "Consulta HAS": "nome_usuario",
        "Hb Glic": "nome",
        "Consulta DM": "nome_usuario",
        "Consulta PN": "gestante_nome",
        "Exames PN": "gestante_nome",
        "Vacina": "nome"
    }

    for category, items in nao_atende.items():
        html_content += f"<h3>{category}</h3>"
        html_content += "<ul>"
        
        for item in items:
            nome_paciente = item.get(nomes[category], "N/A")
            html_content += f"<li>{nome_paciente}</li>"
        
        html_content += "</ul><br>"

    html_content += "</body></html>"
    
    file_binary = excel.generate_excel_binary(todos)
    
    # Configuração do e-mail
    sender_email = "roaletatiana@gmail.com"
    receiver_email = "guialvespimenta27@gmail.com"
    password = "eniu ycej tjfe exkm"  
    
    today = datetime.datetime.now().strftime("%d/%m/%Y")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = f"Relatório de Pacientes - {today}"

    msg.attach(MIMEText(html_content, "html"))
    
    
    # Create attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(file_binary)
    part.add_header("Content-Disposition", f"attachment; filename=relatorio_pacientes-{today}.xlsx")
    part.set_charset("utf-8")  
    msg.attach(part)

    # Enviar e-mail
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
