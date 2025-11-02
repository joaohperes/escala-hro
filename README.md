# Automação de Escala HRO

Sistema automatizado para extrair a escala diária do escala.med.br e publicar no Notion.

## Funcionalidades

- ✅ **Extração inteligente**: Extrai 78+ registros de escalas via Selenium
- ✅ **Dashboard interativo**: Gera HTML com design responsivo e filtros
- ✅ **Publicação automática**: GitHub Pages + Notion (opcional)
- ✅ **Execução diária**: Automática às 7h da manhã (horário de Brasília)
- ✅ **Processamento em tempo real**: Converte e publica dados em minutos
- ✅ **Busca e filtros**: Encontre profissionais por nome, setor ou turno

## Estrutura do Projeto

```
escalaHRO/
├── extracao_inteligente.py           # Extração de dados via Selenium
├── converter_inteligente.py          # Conversor de formato de dados
├── gerar_dashboard_executivo.py      # Gerador do dashboard HTML
├── publicar_notion.py                # Publicador Notion (opcional)
├── criar_views_notion.py             # Setup inicial Notion (opcional)
├── SCRIPTS_ESSENCIAIS.md             # Documentação dos scripts
├── requirements.txt                  # Dependências Python
├── .github/
│   └── workflows/
│       └── atualizar-escala.yml      # Configuração do GitHub Actions
├── escala-hro/                       # Repositório GitHub Pages
│   └── escala-hro/
│       ├── index.html               # Dashboard publicado
│       └── .github/workflows/        # Workflow do Pages repo
└── README.md                         # Esta documentação
```

## Configuração Inicial

### 1. Criar Database no Notion

1. Acesse seu workspace do Notion
2. Crie uma nova página com um Database (tabela)
3. Configure as seguintes colunas **exatamente com estes nomes**:
   - **Data** (tipo: Title)
   - **Setor** (tipo: Text)
   - **Profissional** (tipo: Text)
   - **Período** (tipo: Text)
   - **Observações** (tipo: Text)

### 2. Obter API Key do Notion

1. Acesse [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Clique em "+ New integration"
3. Dê um nome (ex: "Escala HRO Bot")
4. Selecione o workspace
5. Em "Capabilities", marque:
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
6. Clique em "Submit"
7. **Copie o "Internal Integration Token"** (começa com `secret_...`)

### 3. Conectar a Integration ao Database

1. Abra a página do Database que você criou no Notion
2. Clique nos 3 pontinhos (⋯) no canto superior direito
3. Vá em "Connections" → "Add connections"
4. Selecione "Escala HRO Bot" (ou o nome que você deu)

### 4. Obter ID do Database

Na URL da página do Notion, copie o ID do database:
```
https://www.notion.so/workspace/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...
                              ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                              Este é o Database ID (32 caracteres)
```

### 5. Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com) e faça login
2. Clique em "New repository"
3. Nome: `escala-hro` (ou outro de sua preferência)
4. Marque como **Private** (importante para segurança)
5. Clique em "Create repository"

### 6. Configurar Secrets no GitHub

1. No seu repositório, vá em **Settings** → **Secrets and variables** → **Actions**
2. Clique em "New repository secret" e adicione os seguintes secrets:

   | Nome | Valor |
   |------|-------|
   | `ESCALA_USERNAME` | Login da enfermeira no escala.med.br |
   | `ESCALA_PASSWORD` | Senha do escala.med.br |
   | `NOTION_API_KEY` | Token da integration (secret_...) |
   | `NOTION_DATABASE_ID` | ID do database (32 caracteres) |

### 7. Fazer Upload do Código

No terminal, execute:

```bash
cd /Users/joaoperes/escalaHRO

# Inicializar repositório Git
git init

# Adicionar arquivos
git add .

# Fazer primeiro commit
git commit -m "Configuração inicial da automação de escala"

# Conectar ao repositório remoto (substitua SEU_USUARIO pelo seu usuário do GitHub)
git remote add origin https://github.com/SEU_USUARIO/escala-hro.git

# Enviar código
git branch -M main
git push -u origin main
```

## Como Usar

### Execução Automática

Após a configuração, o sistema rodará **automaticamente todos os dias às 7h da manhã** (horário de Brasília).

Você pode acompanhar as execuções em:
- GitHub → Seu repositório → **Actions**

### Execução Manual (Teste)

Para testar antes de esperar o agendamento:

1. Acesse seu repositório no GitHub
2. Vá em **Actions**
3. Clique no workflow "Atualizar Escala Diária HRO"
4. Clique em "Run workflow" → "Run workflow"

### Verificar Resultados

Após a execução:
1. Abra sua página do Notion
2. Você verá a tabela preenchida com os dados do dia

## Status do Projeto

✅ **100% Funcional e Otimizado**

- ✅ Login automatizado no escala.med.br
- ✅ Extração de 78+ registros de escalas
- ✅ Dashboard interativo publicado no GitHub Pages
- ✅ Conversão inteligente de formatos de dados
- ✅ Publicação opcional no Notion
- ✅ Pipeline totalmente automatizado via GitHub Actions
- ✅ Projeto limpo com apenas 5 scripts essenciais
- ✅ Documentação completa e atualizada

### Teste Local

Para testar no seu computador antes de usar GitHub Actions:

```bash
# Instalar dependências
pip3 install -r requirements.txt

# Criar arquivo .env na raiz do projeto com:
# ESCALA_USERNAME=seu_usuario@hro.org.br
# ESCALA_PASSWORD=sua_senha
# NOTION_API_KEY=secret_...
# NOTION_DATABASE_ID=xxxxx...

# Executar (modo com navegador visível para debug)
python3 scraper.py --no-headless --no-publish

# Executar teste completo (extraction + publicação Notion)
python3 scraper.py

# Ver opções disponíveis
python3 scraper.py --help
```

## Solução de Problemas

### A escala não aparece no Notion

1. Verifique se os secrets estão configurados corretamente no GitHub
2. Vá em Actions e verifique os logs de erro
3. Verifique se a integration está conectada ao database

### Erro de autenticação no escala.med.br

1. Confirme que o usuário e senha estão corretos
2. Teste fazer login manual no site
3. Verifique se o site não mudou a estrutura de login

### Nomes das colunas no Notion

As colunas **devem ter exatamente estes nomes**:
- Data
- Setor
- Profissional
- Período
- Observações

## Manutenção

### Alterar horário de execução

Edite o arquivo [`.github/workflows/daily-escala.yml:7`](.github/workflows/daily-escala.yml#L7):

```yaml
schedule:
  - cron: '0 10 * * *'  # 10h UTC = 7h Brasília
```

Exemplos de horários (em UTC):
- 7h Brasília = `0 10 * * *`
- 8h Brasília = `0 11 * * *`
- 6h Brasília = `0 9 * * *`

### Manter histórico de escalas

Por padrão, o sistema limpa as entradas antigas. Para manter histórico:

Comente a linha em [`scraper.py:193`](scraper.py#L193):

```python
# publisher.limpar_database()  # Comentar esta linha
```

## Segurança

- ✅ Repositório configurado como **Private**
- ✅ Credenciais armazenadas em **GitHub Secrets** (criptografadas)
- ✅ Nunca commitar senhas no código
- ✅ API key do Notion com permissões mínimas necessárias

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs em GitHub Actions
2. Consulte a documentação do Notion API
3. Entre em contato com o administrador do sistema

---

**Desenvolvido para HRO - Hospital Regional de Ourinhos**
