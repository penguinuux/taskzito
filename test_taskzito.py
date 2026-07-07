#!/usr/bin/env python3
import os
import sys
import unittest
import importlib.util
import shutil
import re
from datetime import datetime
from io import StringIO

# ==============================================================================
# CARREGAMENTO DINÂMICO DO SCRIPT 'taskzito' SEM EXTENSÃO .py
# ==============================================================================
from importlib.machinery import SourceFileLoader

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'taskzito'))
loader = SourceFileLoader("taskzito", script_path)
spec = importlib.util.spec_from_file_location("taskzito", loader=loader)
taskzito = importlib.util.module_from_spec(spec)
sys.modules["taskzito"] = taskzito
spec.loader.exec_module(taskzito)

# Redireciona os arquivos de dados para arquivos de testes isolados
TEST_TODO_FILE = os.path.join(taskzito.SCRIPT_DIR, "todo_test.d")
TEST_JOURNAL_FILE = os.path.join(taskzito.SCRIPT_DIR, "journal_test.md")

taskzito.TODO_FILE = TEST_TODO_FILE
taskzito.JOURNAL_FILE = TEST_JOURNAL_FILE


class TestTaskzito(unittest.TestCase):
    
    def setUp(self):
        """Prepara o ambiente de testes removendo qualquer resquício anterior."""
        self.clean_test_files()
        
    def tearDown(self):
        """Limpa os arquivos de teste após cada execução."""
        self.clean_test_files()
        
    def clean_test_files(self):
        """Remove os arquivos de dados de teste do disco."""
        for file_path in (TEST_TODO_FILE, TEST_JOURNAL_FILE):
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

    # --------------------------------------------------------------------------
    # TESTES DE INICIALIZAÇÃO DE ARQUIVOS
    # --------------------------------------------------------------------------
    def test_ensure_files_exist(self):
        """Testa se os arquivos de dados são criados automaticamente se não existirem."""
        self.assertFalse(os.path.exists(TEST_TODO_FILE))
        self.assertFalse(os.path.exists(TEST_JOURNAL_FILE))
        
        taskzito.ensure_files_exist()
        
        self.assertTrue(os.path.exists(TEST_TODO_FILE))
        self.assertTrue(os.path.exists(TEST_JOURNAL_FILE))
        self.assertEqual(os.path.getsize(TEST_TODO_FILE), 0)
        self.assertEqual(os.path.getsize(TEST_JOURNAL_FILE), 0)

    # --------------------------------------------------------------------------
    # TESTES DO TO-DO LIST (todo.d)
    # --------------------------------------------------------------------------
    def test_add_todo(self):
        """Testa se as tarefas são adicionadas corretamente no formato markdown."""
        taskzito.ensure_files_exist()
        taskzito.add_todo("Estudar Python")
        taskzito.add_todo("Criar testes unitários")
        
        todos = taskzito.read_todo_file()
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0], "- [ ] Estudar Python")
        self.assertEqual(todos[1], "- [ ] Criar testes unitários")

    def test_parse_todos(self):
        """Testa o parser do arquivo todo.d com metadados de status e índice."""
        lines = [
            "# Cabeçalho Markdown",
            "- [ ] Tarefa Pendente",
            "- [x] Tarefa Concluída",
            "Texto aleatório intermediário",
            "  - [X] Tarefa Indentada Concluída"
        ]
        todos = taskzito.parse_todos(lines)
        
        self.assertEqual(len(todos), 3)
        
        # Primeira tarefa
        self.assertEqual(todos[0]['text'], "Tarefa Pendente")
        self.assertFalse(todos[0]['done'])
        self.assertEqual(todos[0]['line_idx'], 1)
        
        # Segunda tarefa
        self.assertEqual(todos[1]['text'], "Tarefa Concluída")
        self.assertTrue(todos[1]['done'])
        self.assertEqual(todos[1]['line_idx'], 2)
        
        # Terceira tarefa (indentada e case-insensitive [X])
        self.assertEqual(todos[2]['text'], "Tarefa Indentada Concluída")
        self.assertTrue(todos[2]['done'])
        self.assertEqual(todos[2]['line_idx'], 4)

    def test_toggle_todo(self):
        """Testa a inversão de status de tarefas (check/uncheck)."""
        taskzito.ensure_files_exist()
        taskzito.add_todo("Fazer compras")
        taskzito.add_todo("Lavar louça")
        
        # Marca a primeira tarefa
        taskzito.toggle_todo(1)
        todos = taskzito.parse_todos(taskzito.read_todo_file())
        self.assertTrue(todos[0]['done'])
        self.assertFalse(todos[1]['done'])
        
        # Desmarca a primeira tarefa
        taskzito.toggle_todo(1)
        todos = taskzito.parse_todos(taskzito.read_todo_file())
        self.assertFalse(todos[0]['done'])

    def test_delete_todo(self):
        """Testa se as tarefas são removidas mantendo a consistência do arquivo."""
        taskzito.ensure_files_exist()
        taskzito.add_todo("Tarefa 1")
        taskzito.add_todo("Tarefa 2")
        taskzito.add_todo("Tarefa 3")
        
        # Deleta a tarefa central
        taskzito.delete_todo(2)
        
        todos = taskzito.parse_todos(taskzito.read_todo_file())
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0]['text'], "Tarefa 1")
        self.assertEqual(todos[1]['text'], "Tarefa 3")

    # --------------------------------------------------------------------------
    # TESTES DO JORNAL (journal.md)
    # --------------------------------------------------------------------------
    def test_add_journal_note(self):
        """Testa se as notas com timestamp e cabeçalhos de data são salvas."""
        taskzito.ensure_files_exist()
        
        taskzito.add_journal_note("Iniciando a modelagem do DB #Task1001")
        taskzito.add_journal_note("Corrigindo bug na migration #Bug202")
        
        with open(TEST_JOURNAL_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Verifica cabeçalho de data
        self.assertIn(f"# {today_str}", content)
        # Verifica se as notas estão presentes
        self.assertIn("Iniciando a modelagem do DB #Task1001", content)
        self.assertIn("Corrigindo bug na migration #Bug202", content)
        # Verifica se contém formato de timestamp [- [HH:MM:SS]]
        self.assertTrue(re.search(r'- \[\d{2}:\d{2}:\d{2}\]', content))

    # --------------------------------------------------------------------------
    # TESTES DE RELATÓRIO (report / report -s)
    # --------------------------------------------------------------------------
    def test_parse_journal_for_report(self):
        """Testa a extração e agrupamento de hashtags #Task e #Bug do diário."""
        # Cria um arquivo de jornal falso contendo datas e tags variadas
        fake_journal_content = (
            "# 2026-07-06\n"
            "- [10:00:00] Iniciei o dia com #Task4001\n"
            "- [11:30:00] Resolvendo exception na controller #Bug505 e #Task4001\n"
            "\n"
            "# 2026-07-07\n"
            "- [14:00:00] Planejando nova sprint #Task9002\n"
        )
        with open(TEST_JOURNAL_FILE, 'w', encoding='utf-8') as f:
            f.write(fake_journal_content)
            
        report_data = taskzito.parse_journal_for_report()
        
        # Validação do Dia 2026-07-06
        self.assertIn("2026-07-06", report_data)
        self.assertIn("#Task4001", report_data["2026-07-06"])
        self.assertIn("#Bug505", report_data["2026-07-06"])
        
        # Verifica o número de ocorrências por tag
        self.assertEqual(len(report_data["2026-07-06"]["#Task4001"]), 2)
        self.assertEqual(len(report_data["2026-07-06"]["#Bug505"]), 1)
        
        # Validação do Dia 2026-07-07
        self.assertIn("2026-07-07", report_data)
        self.assertIn("#Task9002", report_data["2026-07-07"])
        self.assertEqual(len(report_data["2026-07-07"]["#Task9002"]), 1)

    def test_generate_report_simple_output(self):
        """Testa se o relatório no modo simples (-s / --simple) gera a saída esperada."""
        fake_journal_content = (
            "# 2026-07-07\n"
            "- [09:00:00] Correção de css #Bug12\n"
            "- [10:30:00] Implementado novas views #Task99\n"
            "- [11:00:00] Teste unitário das views #Task99 #Bug12\n"
        )
        with open(TEST_JOURNAL_FILE, 'w', encoding='utf-8') as f:
            f.write(fake_journal_content)
            
        # Captura a saída padrão do console (stdout)
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            taskzito.generate_report(simple=True)
        finally:
            sys.stdout = sys.__stdout__  # Restaura o stdout original
            
        expected_output = "2026-07-07: #Task99, #Bug12\n"
        self.assertEqual(captured_output.getvalue(), expected_output)


if __name__ == "__main__":
    unittest.main()
