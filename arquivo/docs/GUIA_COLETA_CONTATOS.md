# 📞 Guia de Coleta de Contatos Faltantes

## Situação Atual

Você tem **14 profissionais na escala SEM telefone registrado** na base de dados.

O site `escala.med.br` renderiza os dados via JavaScript, então não conseguimos fazer web scraping automático.

## Solução Recomendada

Como os profissionais já estão na escala, seus contatos PODEM estar visíveis no site, mas você precisa:

### Opção 1: Verificar Manualmente no Site (Recomendado)
1. Entre em [escala.med.br](https://escala.med.br)
2. Procure por cada profissional na lista
3. Se tiver um perfil com telefone, copie a informação
4. Adicione ao arquivo de contatos

### Opção 2: Entrar em Contato Direto
1. Ligue ou mande mensagem para o hospital
2. Peça o telefone de cada profissional

### Opção 3: Sistema Automatizado (Futuro)
Quando você souber os telefones, execute:

```bash
python3 /Users/joaoperes/escalaHRO/add_contacts_bulk.py
```

E passe os dados em formato JSON:
```json
[
  {"name": "Profissional", "phone": "(49) 99999-9999"},
  {"name": "Outro Profissional", "phone": "(49) 99888-8888"}
]
```

## Profissionais Faltando Contato

| # | Nome | Setor | Status |
|---|------|-------|--------|
| 1 | Bianca Soder Wolschick | (não encontrado em extração) | ⏳ |
| 2 | Fabricio Praca Consalter | Hemodinâmica - Sobreaviso Cardiologia | ⏳ |
| 3 | Fernando Luiz de Melo Bernardi | Hemodinâmica - Sobreaviso Cardiologia | ⏳ |
| 4 | Graziela Fatima Battistel | UCINCo E Sala de Parto | ⏳ |
| 5 | Jamile Rosset Mocellin | Residência de Cirurgia Geral | ⏳ |
| 6 | Jessica Aparecida Battistel | UCINCo E Sala de Parto | ⏳ |
| 7 | João Roberto Munhoz Zorzetto | Ultrassonografia - Sobreaviso | ⏳ |
| 8 | Marcelo Eduardo Heinig | Nefrologia - Sobreaviso | ⏳ |
| 9 | Marcia Akemi Nishino | UTI Neonatal - Plantão | ⏳ |
| 10 | Matheus Toldo Kazerski | Pronto Socorro HRO - Plantão | ⏳ |
| 11 | Rodrigo Sponchiado Rocha | (não encontrado em extração) | ⏳ |
| 12 | Rovani Jose Rinaldi Camargo | Cirurgia Torácica - Sobreaviso | ⏳ |
| 13 | Vinicius Rubin | Urologia Sobreaviso | ⏳ |
| 14 | Waleska Furini | Residência de Ginecologia e Obstetrícia | ⏳ |

---

## Como Adicionar Contatos

### Método 1: Editar Manualmente
Abra `/Users/joaoperes/escalaHRO/profissionais_autenticacao.json` e adicione:

```json
{
  "name": "Nome Completo",
  "email": "email@example.com",
  "phone": "(49) 99999-9999",
  "last4": "9999"
}
```

### Método 2: Criar Script de Adição
Prepare um arquivo `novos_contatos.json`:

```json
[
  {"name": "Bianca Soder Wolschick", "phone": "(49) 99XXX-XXXX"},
  {"name": "Fabricio Praca Consalter", "phone": "(49) 99XXX-XXXX"}
]
```

Depois execute:
```bash
python3 /Users/joaoperes/escalaHRO/add_contacts_bulk.py novos_contatos.json
```

---

## Por Que Isso é Importante?

✅ **Automação**: Dashboard mostra contatos ao lado do nome
✅ **WhatsApp**: Botões de contato rápido para profissionais
✅ **Busca**: Sistema de busca de profissionais por telefone
✅ **Confiabilidade**: Dados persistem entre atualizações

---

## Próximos Passos

1. **Hoje**: Coletar 2-3 contatos como teste
2. **Esta semana**: Coletar todos os 14 números
3. **Adicionar**: Via arquivo JSON
4. **Commit**: `git add profissionais_autenticacao.json && git commit -m "Add missing professional contacts"`
5. **Deploy**: Push e atualizar Vercel

---

**Última atualização**: 16/11/2025 às 13:10 UTC
**Contatos já adicionados**: Camila Tonini (49) 99834-2129
**Faltando**: 14 profissionais
