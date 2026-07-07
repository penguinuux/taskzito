# ⚡ Taskzito CLI ⚡

O **Taskzito** é um jornal markdown minimalista e gerenciador de to-do list CLI em Python super leve, focado em alta produtividade para desenvolvedores. Ele armazena suas tarefas e notas em arquivos locais Markdown padrão (`todo.d` e `journal.md`), permitindo fácil visualização e edição em qualquer editor.

---

## ✨ Funcionalidades

1. **To-Do List Integrado (`todo.d`)**: Adicione, liste, alterne o status (toggle entre `[ ]` e `[x]`) e delete tarefas com facilidade.
2. **Jornal Diário (`journal.md`)**: Registre notas rápidas com timestamps de forma contínua durante o dia.
3. **Relatórios Inteligentes**: Marque atividades com hashtags do tipo `#Task123` ou `#Bug456` em suas notas e gere relatórios de progresso agrupados lindamente por dia e tarefas.
4. **Visual Premium**: Estética moderna utilizando ícones Unicode limpos e cores vibrantes ANSI no terminal (sem necessidade de instalar dependências externas).

---

## 🚀 Como Usar

### 📋 To-Do List

*   **Ver Dashboard (Tarefas de hoje + Últimas notas + Dicas)**:
    ```bash
    ./taskzito
    ```
*   **Listar todas as tarefas**:
    ```bash
    ./taskzito todo
    ```
*   **Adicionar uma nova tarefa**:
    ```bash
    ./taskzito add "Minha nova tarefa"
    ```
*   **Alternar status de uma tarefa (Toggle [ ] <-> [x])**:
    ```bash
    ./taskzito toggle <numero_da_tarefa>
    # ou
    ./taskzito check <numero_da_tarefa>
    ```
*   **Remover uma tarefa**:
    ```bash
    ./taskzito del <numero_da_tarefa>
    ```

### 📖 Journal (Diário)

*   **Adicionar uma nota no jornal de hoje**:
    ```bash
    ./taskzito note "Implementando a rota de login #Task42282"
    ```
*   **Visualizar as notas do diário registradas hoje**:
    ```bash
    ./taskzito view
    ```

### 📊 Relatórios

*   **Gerar o relatório cronológico completo de Tasks & Bugs**:
    ```bash
    ./taskzito report
    ```
    Isso lerá seu arquivo `journal.md` e agrupará todas as notas que possuem tags como `#TaskXXXX` ou `#BugXXXX` organizadas por data e ID de tarefa, gerando um resumo limpo e formatado.

*   **Gerar o relatório simplificado (fácil de copiar/colar)**:
    ```bash
    ./taskzito report -s
    # ou
    ./taskzito report --simple
    ```
    Isso gerará uma lista simplificada por dia com as tasks/bugs separadas por vírgula, sem ícones ou formatação ANSI especial.

---

## 📂 Estrutura dos Arquivos

Os arquivos gerados são compatíveis com leitores e renderizadores Markdown comuns:

### `todo.d` (Exemplo)
```markdown
- [x] Criar infraestrutura básica da CLI
- [ ] Adicionar suporte a relatórios do jornal
```

### `journal.md` (Exemplo)
```markdown
# 2026-07-07

- [12:30:07] Iniciado o desenvolvimento do backend da CLI. #Task001
- [12:30:07] Resolvido erro de index out of range ao fazer toggle de tarefas inexistentes. #Bug102
- [12:30:07] Revisão geral do código. #Task001
```

---

## 🛠️ Requisitos

*   Python 3.x
*   Terminal com suporte a cores ANSI e caracteres Unicode (a maioria dos terminais Linux modernos)

---

## 🧪 Como Rodar os Testes

Você pode validar e garantir a integridade de todas as regras de negócio executando a suíte de testes integrada (desenvolvida com a biblioteca padrão `unittest` do Python):

```bash
python3 test_taskzito.py
```
