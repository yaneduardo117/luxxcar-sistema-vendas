# 🏎️ LuxxCar - Sistema Premium de Gestão e Venda Automotiva

Um sistema completo, responsivo e assíncrono para gestão de concessionárias de luxo, desenvolvido como projeto de avaliação prática.

## 🎓 Informações Acadêmicas
* **Instituição:** SENAI
* **Curso:** Técnico em Desenvolvimento de Sistemas
* **Disciplina:** Teste e Manutenção de Sistemas
* **Instrutor:** Rodrigo D'Ávila
* **Desenvolvedor:** Yan Eduardo Oliveira da Silva

---

## ✨ Funcionalidades em Destaque

* **Proteção de Concorrência (Double Spending):** Uso de transações atômicas (`transaction.atomic`) e bloqueio de banco (`select_for_update`) para impedir que dois usuários reservem o mesmo veículo simultaneamente.
* **Motor de Busca e Filtros Assíncronos:** Utilização de **HTMX** para filtrar veículos por marca, segmento e carroceria sem recarregar a página.
* **Galeria de Imagens Dinâmica:** Sistema de upload múltiplo de imagens (Capa + Galeria) integrados nativamente ao CRUD de edição.
* **População Automatizada (Seeder):** Comando nativo customizado (`popular_frota`) que faz requisições HTTP via API e baixa fotos em alta resolução do Unsplash direto para o banco de dados.
* **Painel Administrativo Premium:** Interface de gerenciamento customizada utilizando a biblioteca *Django Jazzmin*.
* **Notificações em Tempo Real:** Sino de alertas integrado ao Dashboard para informar administradores sobre novas reservas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.14 & Django 6.0.2
* **Frontend/UI:** HTML5, Tailwind CSS (CDN), Alpine.js (CDN)
* **Reatividade:** HTMX (CDN)
* **Banco de Dados:** SQLite3
* **Processamento de Imagem:** Pillow

---

## 🚀 Como Executar o Projeto Localmente

Siga o passo a passo abaixo para rodar o sistema no seu ambiente:

**1. Clone o repositório e acesse a pasta:**
```bash
git clone [https://github.com/SEU_USUARIO/luxxcar-sistema-vendas.git](https://github.com/SEU_USUARIO/luxxcar-sistema-vendas.git)
cd luxxcar-sistema-vendas
```

**2. Crie e ative a máquina virtual (.venv):**
```powershell
# No Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\activate
```

**3. Instale as dependências exigidas:**
```bash
pip install -r requirements.txt
```

**4. (Opcional) Reconstruir o Banco de Dados:**
O banco de dados (`db.sqlite3`) já vem populado neste repositório. Porém, caso precise reconstruir a vitrine do zero, execute o script personalizado:
```bash
python manage.py popular_frota
```

**5. Inicie o Servidor:**
```bash
python manage.py runserver
```
O sistema estará disponível em: `http://127.0.0.1:8000/`

---

## 🔐 Credenciais de Acesso (Administrador)
Para acessar o Painel Admin (`http://127.0.0.1:8000/admin/`) e testar as funcionalidades exclusivas de aprovação de vendas e gestão de estoque:

* **E-mail / Usuário:** `admin123@gmail.com`
* **Senha:** `admin1357@A`

---

## 📄 Documentação
O planejamento de testes, relatórios de incidentes resolvidos e o plano de manutenção preventiva e evolutiva estão detalhados no arquivo **`PROJETO_TESTE_MANUTENÇÃO (yan eduardo O.S)`**, localizado na raiz deste repositório.
