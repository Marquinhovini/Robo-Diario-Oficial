from flask import Flask, request, jsonify, render_template
import subprocess
import logging
from datetime import datetime

app = Flask(__name__)

# Configuração de logs
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/collect', methods=['POST'])
def collect():
    data = request.json
    
    start_date = data.get('startDate')
    end_date = data.get('endDate')

    # Validação das datas
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        today = datetime.today()

        if start_date_obj > today or end_date_obj > today:
            return jsonify({"success": False, "message": "As datas não podem ser futuras."})

        if start_date_obj > end_date_obj:
            return jsonify({"success": False, "message": "A data inicial não pode ser posterior à data final."})
    except ValueError:
        return jsonify({"success": False, "message": "Formato de data inválido. Use AAAA-MM-DD."})

    try:
        # Chamar o script Python e capturar a saída
        result = subprocess.run(['python', 'diariofuncional.py', start_date, end_date], capture_output=True, text=True)

        # Exibir a saída padrão do subprocesso no console Flask
        print(result.stdout)

        # Verificar se houve "Nenhum dado encontrado" na saída do subprocesso
        if "Nenhum dado encontrado" in result.stdout:
            return jsonify({"success": False, "message": f"SEM EXONERAÇÃO {start_date} até {end_date}."}), 200
        else:
            logging.info(f"Coleta de dados iniciada de {start_date} até {end_date}.")
            return jsonify({"success": True, "message": f"Coleta de dados finalizada com sucesso de {start_date} até {end_date}."}), 200
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao iniciar a coleta de dados: {str(e)}")
        return jsonify({"success": False, "error": str(e), "message": "Ocorreu um erro ao iniciar a coleta de dados."})
    
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        return jsonify({"success": False, "error": str(e), "message": "Ocorreu um erro inesperado."})

if __name__ == '__main__':
    app.run(debug=True)
