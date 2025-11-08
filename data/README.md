# 📁 Diretório de Dados de Fallback

Este diretório contém arquivos de amostra e dados de referência para garantir que o dashboard nunca fica vazio.

## 📄 Arquivos

- **extracao_inteligente_sample.json**: Estrutura de amostra dos dados extraídos
  - Usado como fallback se `/tmp/extracao_inteligente.json` não existir
  - Evita dashboard vazio quando extração falha
  - Estrutura de referência para desenvolvimento

## 🔄 Fluxo de Dados

1. **Primeira tentativa**: `/tmp/extracao_inteligente.json` (dados do dia)
2. **Segunda tentativa**: `/tmp/extracao_inteligente_anterior.json` (dados de ontem)
3. **Terceira tentativa**: `data/extracao_inteligente_sample.json` (fallback)
4. **Última tentativa**: Estrutura vazia (nunca deve chegar aqui)

## 📝 Notas

- Os arquivos em `/tmp` são **temporários** e são limpos quando o GitHub Actions reinicia
- Os arquivos em `data/` são **permanentes** e ficam no repositório
- O `gerar_dashboard_executivo.py` implementa esta lógica de fallback

## 🚨 Se o Dashboard Fica Vazio

1. Verifique se houve erro na extração:
   ```bash
   python3 extracao_inteligente.py
   ```

2. Verifique se os dados estão em `/tmp`:
   ```bash
   ls -la /tmp/extracao_inteligente*.json
   ```

3. Se tudo falhar, dashboard usará `data/extracao_inteligente_sample.json` como fallback

