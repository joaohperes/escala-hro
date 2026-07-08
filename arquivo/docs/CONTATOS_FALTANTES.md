# 📞 Profissionais com Contato Faltante

## Status
Encontrados **14 profissionais** na escala **SEM telefone registrado**.

---

## Profissionais Faltando Contato

| # | Nome | Setor | Telefone | Email |
|---|------|-------|----------|-------|
| 1 | **Bianca Soder Wolschick** | (não encontrado em extração recente) | ❌ | |
| 2 | **Fabricio Praca Consalter** | Hemodinâmica - Sobreaviso Cardiologia | ❌ | |
| 3 | **Fernando Luiz de Melo Bernardi** | Hemodinâmica - Sobreaviso Cardiologia | ❌ | |
| 4 | **Graziela Fatima Battistel** | UCINCo E Sala de Parto | ❌ | |
| 5 | **Jamile Rosset Mocellin** | Residência de Cirurgia Geral | ❌ | |
| 6 | **Jessica Aparecida Battistel** | UCINCo E Sala de Parto | ❌ | |
| 7 | **João Roberto Munhoz Zorzetto** | Ultrassonografia - Sobreaviso | ❌ | |
| 8 | **Marcelo Eduardo Heinig** | Nefrologia - Sobreaviso | ❌ | |
| 9 | **Marcia Akemi Nishino** | UTI Neonatal - Plantão | ❌ | |
| 10 | **Matheus Toldo Kazerski** | Pronto Socorro HRO - Plantão | ❌ | |
| 11 | **Rodrigo Sponchiado Rocha** | (não encontrado em extração recente) | ❌ | |
| 12 | **Rovani Jose Rinaldi Camargo** | Cirurgia Torácica - Sobreaviso | ❌ | |
| 13 | **Vinicius Rubin** | Urologia Sobreaviso | ❌ | |
| 14 | **Waleska Furini** | Residência de Ginecologia e Obstetrícia | ❌ | |

---

## Como Adicionar os Contatos

### Opção 1: Pedir para os profissionais
Entre em contato com cada profissional listado acima e solicite seu telefone e email.

### Opção 2: Usar script de adição manual
Quando tiver os dados, execute:

```bash
python3 /Users/joaoperes/escalaHRO/add_contacts.py
```

### Opção 3: Editar diretamente
Edite `/Users/joaoperes/escalaHRO/profissionais_autenticacao.json` e adicione os contatos no formato:

```json
{
  "name": "Nome Completo",
  "email": "email@example.com",
  "phone": "(XX) XXXXX-XXXX",
  "last4": "XXXX"
}
```

---

## Notas
- ✅ **Camila Tonini** já foi adicionada: `(49) 99834-2129`
- 🔍 A busca foi realizada em:
  - `/tmp/extracao_inteligente.json` (extração atual)
  - `data/extracao_inteligente_anterior_cache.json` (cache persistente)
  - `escalas_multiplos_dias.json` (escalas históricas)
- 📝 Os dados no arquivo de extração NÃO contêm telefones para esses profissionais

---

## Próximos Passos

1. **Recolher os contatos** via chamadas/mensagens diretas
2. **Atualizar o arquivo** `profissionais_autenticacao.json`
3. **Fazer commit** das mudanças: `git add profissionais_autenticacao.json && git commit -m "Add missing professional contacts"`
4. **Push** para o repositório

---

**Última atualização**: 2025-11-16
**Gerado por**: Scraping Script
