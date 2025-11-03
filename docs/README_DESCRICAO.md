# 📋 Automação de Escala HRO

**Dashboard executivo para visualização da escala médica da HRO (Associação Hospitalar Lenoir Vargas Ferreira)**

## 🎯 Objetivo Principal

Extrair com **100% de acurácia** as informações de escalas do site `escala.med.br` e exibir em um dashboard interativo e responsivo.

## ✨ Funcionalidades

- ✅ **Extração Inteligente**: Extrai 78+ registros de escalas via Selenium
- ✅ **Dashboard Interativo**: Interface responsiva com filtros de busca e navegação
- ✅ **Publicação Automática**: GitHub Pages + atualizações diárias
- ✅ **Autenticação Segura**: Email/telefone para profissionais, senha para admin
- ✅ **Indicador de Status**: Dot verde/vermelho mostra se atualização deu certo
- ✅ **Lista de Contatos**: Todos os 158 profissionais com WhatsApp clickável
- ✅ **Histórico**: Mantém dados dos últimos 3 dias

## 🌐 Acessar

**Live Dashboard**: https://joaohperes.github.io/escala-hro/

## 📊 Indicador de Status

O dashboard mostra um **dot colorido** ao lado da data de atualização:
- 🟢 **Verde brilhante** = Atualização bem-sucedida
- 🔴 **Vermelho piscando** = Erro na extração/atualização

Passe o mouse sobre o dot para ver detalhes do erro.

## 📁 Estrutura do Projeto

```
escalaHRO/
├── extracao_inteligente.py          # Extração via Selenium
├── converter_inteligente.py         # Converte formato de dados
├── gerar_dashboard_executivo.py     # Gera HTML do dashboard
├── profissionais_autenticacao.json  # 158 profissionais para auth
├── docs/
│   └── index.html                   # Dashboard publicado (GitHub Pages)
└── escala-hro/                      # Versão alternativa/legacy
```

## 🔧 Tecnologias

- **Python 3.9+**: Scripts de extração e processamento
- **Selenium**: Automação de navegador para scrapy
- **HTML/CSS/JS**: Dashboard responsivo e moderno
- **GitHub Pages**: Hospedagem estática
- **GitHub Actions**: Automação diária

## 📋 Dados Extraídos

Cada atualização coleta:
- Nome do profissional
- Email profissional
- Telefone
- Setor/Especialidade
- Tipo de turno
- Horário
- Data

## 🔐 Autenticação

### Profissional
- Email profissional OU
- Últimos 4 dígitos do telefone

### Outro Usuário (Admin/Enfermagem)
- Senha: `HRO-ALVF`

## 📊 Monitoramento

Use o **indicador de status (dot colorido)** para monitorar ao longo da semana:
- Se está verde todos os dias → extração funcionando perfeitamente
- Se aparecer vermelho → investigar o erro (detalhes no tooltip)

## 🚀 Desenvolvimento

Para regenerar o dashboard após mudanças:

```bash
# 1. Executar extração
python3 extracao_inteligente.py

# 2. Converter dados
python3 converter_inteligente.py

# 3. Gerar dashboard
python3 gerar_dashboard_executivo.py

# 4. Publicar
cp /tmp/dashboard_executivo.html docs/index.html
git add docs/index.html
git commit -m "Update dashboard"
git push
```

## 📝 Logs

Todos os scripts geram output detalhado mostrando:
- Quantidade de registros extraídos
- Datas processadas
- Status de sucesso/erro
- Horário de execução

## 🐛 Troubleshooting

**Dashboard não atualiza?**
- Aguarde 5 minutos (cache do GitHub)
- Recarregue com Cmd+Shift+R (limpar cache)

**Dot vermelho apareceu?**
- Hover no dot para ver mensagem de erro
- Verifique conectividade com `escala.med.br`

**Não consegue fazer login?**
- Email/telefone incorretos ou não cadastrado
- Tente "Outro Usuário" com senha `HRO-ALVF`

## 👨‍💻 Autor

Desenvolvido por João Pedro Peres para HRO.

## 📄 Licença

Privado - Uso interno HRO
