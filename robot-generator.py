import random
import requests
from datetime import date, timedelta
import pandas as pd

# Parâmetros de configuração
qtd_total_alunos_param = 120
qtd_alunos_by_sala_param = int(qtd_total_alunos_param / 4)
initial_calendar_param = date(2023, 1, 1)
final_calendar_param = date(2025, 12, 31)

# Gerador de IDs consolidado
class IdentityGenerator:
    def __init__(self):
        self.id_count = 0

    def get_next_identity(self):
        self.id_count += 1
        return self.id_count

generator = IdentityGenerator()

# Funções utilitárias para gerar dados de alunos
def ra_generate():
    return "".join([str(random.randint(0, 9)) for _ in range(11)])

def name_generate():
    try:
        response = requests.get("https://randomuser.me/api/", timeout=5)
        response.raise_for_status()
        data = response.json()
        nome = data["results"][0]["name"]
        return f"{nome['first']} {nome['last']}"
    except (requests.RequestException, KeyError, IndexError):
        return "Nome Desconhecido"

def generate_alunos():
    return [
        {
            "id": generator.get_next_identity(),
            "ra": ra_generate(),
            "nome": name_generate(),
            "ativo": True
        }
        for _ in range(qtd_total_alunos_param)
    ]

def generate_disciplinas():
    nomes_disciplinas = ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Educação Física", "Inglês"]
    return [
        {
            "id": generator.get_next_identity(),
            "codigo": f'D{str(random.randint(100, 9999))}',
            "nome": nome
        }
        for nome in nomes_disciplinas
    ]

def generate_turmas():
    nomes_turmas = ["6º Ano", "7º Ano", "8º Ano", "9º Ano"]
    return [
        {
            "id": generator.get_next_identity(),
            "codigo": f'T{str(random.randint(100, 9999))}',
            "nome": nome
        }
        for nome in nomes_turmas
    ]

def gerar_calendario(inicio, fim):
    calendario_list = []
    current_date = inicio
    while current_date <= fim:
        calendario_list.append({
            "id": generator.get_next_identity(), 
            "data_completa": current_date.strftime("%d/%m/%Y")
        })
        current_date += timedelta(days=1)
    return calendario_list

def get_calendar_id_by_date(calendario_model, compare: date):
    for data in calendario_model:
        if data['data_completa'] == compare.strftime("%d/%m/%Y"):
            return data['id']
    return None 

def generate_register_dates(feriados, inicio, fim):
    register_date = []
    current_date = inicio
    while current_date <= fim:
        if current_date.weekday() < 5 and current_date not in feriados and current_date.month not in [1, 7, 12]:
            register_date.append(current_date)
        current_date += timedelta(days=1)
    return register_date

def generate_frequence_model(register_date, disciplinas_ids, turmas_ids):
    frequence_model = []
    for data in register_date:
        for turma_id in turmas_ids:
            total_alunos_presentes = random.randint(int(qtd_alunos_by_sala_param / 2), qtd_alunos_by_sala_param)
            total_alunos_ausentes = qtd_alunos_by_sala_param - total_alunos_presentes

            total_ausentes = int(qtd_alunos_by_sala_param * 0.1)
            total_alunos_ausentes = min(total_alunos_ausentes, total_ausentes)
            total_alunos_presentes = qtd_alunos_by_sala_param - total_alunos_ausentes

            frequence_model.append({
                "id": generator.get_next_identity(),
                "disciplina_id": random.choice(disciplinas_ids),
                "turma_id": turma_id,
                "data_registro_id": get_calendar_id_by_date(calendario_model, data),
                "total_alunos_presentes": total_alunos_presentes,
                "total_alunos_ausentes": total_alunos_ausentes
            })
    return frequence_model

def generate_frequence_aluno_model(frequence_model, alunos_ids):
    frequence_aluno_model = []
    aluno_id_count = 0

    for frequence in frequence_model:
        frequence_id = frequence["id"]
        total_alunos_presentes = frequence["total_alunos_presentes"]

        for i in range(qtd_alunos_by_sala_param):
            is_present = i < total_alunos_presentes
            frequence_aluno_model.append({
                "frequence_id": frequence_id,
                "aluno_id": alunos_ids[aluno_id_count],
                "presenca": is_present,
                "mensagem": '' if is_present else 'O aluno não estava presente na sala hoje, aconteceu alguma coisa?'
            })
            aluno_id_count += 1

            # Reinicia o contador de alunos se atingir o total
            if aluno_id_count >= len(alunos_ids):
                aluno_id_count = 0

    return frequence_aluno_model

from random import uniform

def generate_notas(alunos_ids, disciplinas_ids, turmas_ids, start_year, end_year):
    notas_model = []

    for ano in range(start_year, end_year + 1):
        for semestre in [1, 2]: 
            for aluno_id in alunos_ids:
                for disciplina_id in disciplinas_ids:
                    for turma_id in turmas_ids:

                        media_nota = round(uniform(4.0, 10.0), 1)
                        recuperacao = media_nota < 7.0

                        notas_model.append({
                            "aluno_id": aluno_id,
                            "disciplina_id": disciplina_id,
                            "turma_id": turma_id,
                            "ano": ano,
                            "semestre": semestre,
                            "media_nota": media_nota,
                            "recuperacao": recuperacao
                        })

    return notas_model


# Executando as funções para gerar os dados completos
alunos_model = generate_alunos()
disciplinas_model = generate_disciplinas()
turmas_model = generate_turmas()
calendario_model = gerar_calendario(initial_calendar_param, final_calendar_param)

# Datas letivas e lista de feriados
feriados = [date(2023, 4, 21), date(2023, 5, 1), date(2023, 6, 15), date(2023, 9, 7), date(2023, 10, 12), date(2023, 11, 2), date(2023, 11, 15), date(2023, 12, 25)]
register_date = generate_register_dates(feriados, date(2023, 2, 1), date.today())

# Gerando frequência e frequência por aluno
disciplinas_ids = [disciplina["id"] for disciplina in disciplinas_model]
turmas_ids = [turma["id"] for turma in turmas_model]
frequence_model = generate_frequence_model(register_date, disciplinas_ids, turmas_ids)
alunos_ids = [aluno["id"] for aluno in alunos_model]
frequence_aluno_model = generate_frequence_aluno_model(frequence_model, alunos_ids)
notas_model = generate_notas(alunos_ids, disciplinas_ids, turmas_ids, 2023, date.today().year)

###################################################################################

# Save data in excel

df_alunos = pd.DataFrame(alunos_model)
df_disciplinas = pd.DataFrame(disciplinas_model)
df_turmas = pd.DataFrame(turmas_model)
df_calendario = pd.DataFrame(calendario_model)
df_frequence = pd.DataFrame(frequence_model)
df_frequence_aluno = pd.DataFrame(frequence_aluno_model)
df_notas = pd.DataFrame(notas_model)

with pd.ExcelWriter("attendance-school-management.xlsx") as writer:
    df_alunos.to_excel(writer, sheet_name='dim_aluno', index=False)
    df_disciplinas.to_excel(writer, sheet_name='dim_disciplina', index=False)
    df_turmas.to_excel(writer, sheet_name='dim_turma', index=False)
    df_calendario.to_excel(writer, sheet_name='dim_calendario', index=False)
    df_frequence.to_excel(writer, sheet_name='fato_frequencia', index=False)
    df_frequence_aluno.to_excel(writer, sheet_name='dim_frequencia_aluno', index=False)
    df_notas.to_excel(writer, sheet_name='fato_notas', index=False)