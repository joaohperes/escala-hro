# Guia Rápido de Atualização - Dashboard Final

## Para Atualizar APENAS os Dados (Recomendado)

### Usando o Script Python

```bash
# 1. Certifique-se que tem os dados em /tmp/extracao_inteligente.json
# 2. Execute o script:
python3 /Users/joaoperes/escalaHRO/update_escala_data_only.py
```

Este script:
- ✅ Preserva TODO o código JavaScript
- ✅ Atualiza apenas o JSON de escalas
- ✅ Mantém formatação e funcionalidades
- ✅ Atualiza tanto `index.html` quanto `docs/index.html`

### Manualmente no HTML

Abra `/Users/joaoperes/escalaHRO/dashboard_final.html` e encontre (linha ~442):

```javascript
const escalas = {
    "atual": {
        "data": "05 novembro 2025",
        "data_simples": "05/11/2025",
        "registros": [
            // ADICIONE SEUS DADOS AQUI
            {
                "profissional": "Dr. João Silva",
                "setor": "UTI Adulto",
                "tipo_turno": "Plantão Matutino",
                "horario": "07:00/13:00"
            }
        ],
        "total": 1  // Número de registros
    },
    "anterior": {
        // Mesma estrutura para dia anterior
    }
};
```

## Template de Dados

### Um Profissional

```javascript
{
    "profissional": "Nome Completo do Profissional",
    "setor": "Nome do Setor",
    "tipo_turno": "Descrição do Turno",
    "horario": "07:00/13:00"
}
```

### Exemplo Completo

```javascript
const escalas = {
    "atual": {
        "data": "06 novembro 2025",
        "data_simples": "06/11/2025",
        "registros": [
            {
                "profissional": "Dr. João Silva",
                "setor": "UTI Adulto I",
                "tipo_turno": "Plantão Matutino",
                "horario": "07:00/13:00"
            },
            {
                "profissional": "Dra. Maria Santos",
                "setor": "UTI Adulto I",
                "tipo_turno": "Plantão Vespertino",
                "horario": "13:00/19:00"
            },
            {
                "profissional": "Dr. Pedro Costa",
                "setor": "Pronto Socorro HRO - Plantão",
                "tipo_turno": "P1",
                "horario": "07:00/13:00"
            },
            {
                "profissional": "Dra. Ana Paula",
                "setor": "Pronto Socorro HRO - Plantão",
                "tipo_turno": "P2",
                "horario": "13:00/19:00"
            }
        ],
        "total": 4
    },
    "anterior": {
        "data": "05 novembro 2025",
        "data_simples": "05/11/2025",
        "registros": [
            // Dados do dia anterior
        ],
        "total": 0
    },
    "data_atualizacao": "06/11/2025",
    "hora_atualizacao": "08:30",
    "status_atualizacao": "sucesso"
};
```

## Adicionar Novos Profissionais (Contatos)

Encontre no HTML (linha ~458):

```javascript
const profissionaisData = {
    "professionals": [
        {
            "name": "Dr. João Silva",
            "email": "joao.silva@hospital.com",
            "phone": "(49) 99999-1111",
            "last4": "1111"  // Últimos 4 dígitos para login
        }
        // Adicione mais aqui
    ]
};
```

## Adicionar Novos Ramais

Encontre no HTML (linha ~450):

```javascript
const ramaisData = {
    "departments": [
        {
            "name": "Nome do Departamento",
            "extensions": ["1234", "5678", "9012"]
        }
        // Adicione mais aqui
    ]
};
```

## Dicas Importantes

### 1. Sempre faça backup antes
```bash
cp dashboard_final.html dashboard_final_backup.html
```

### 2. Validação JSON
Antes de salvar, valide seu JSON em: https://jsonlint.com/

### 3. Teste localmente
Abra o arquivo no navegador após editar para verificar erros

### 4. Campos obrigatórios
- ✅ `profissional`: Nome completo
- ✅ `setor`: Nome do setor exato
- ✅ `tipo_turno`: Descrição do turno
- ✅ `horario`: Formato HH:MM/HH:MM

### 5. Nomes de setores consistentes
Use sempre o mesmo nome para o mesmo setor. Exemplos:
- ❌ "UTI Adulto", "UTI adulto", "Uti Adulto"
- ✅ "UTI Adulto I" (sempre o mesmo)

### 6. Classificação automática de turnos
O sistema detecta automaticamente o tipo de turno baseado em:
- Palavras-chave: "matutino", "vespertino", "noturno", "diurno", "sobreaviso"
- Horários: 07:00-13:00 = Matutino, 13:00-19:00 = Vespertino, etc.

## Fluxo de Trabalho Recomendado

### Opção 1: Via Script (Automático)
```bash
# 1. Gerar JSON com extração
python3 extracao_inteligente.py

# 2. Atualizar HTML automaticamente
python3 update_escala_data_only.py

# 3. Verificar resultado
open dashboard_final.html
```

### Opção 2: Manual (Completo Controle)
```bash
# 1. Fazer backup
cp dashboard_final.html dashboard_final_backup_$(date +%Y%m%d).html

# 2. Abrir no editor
code dashboard_final.html  # ou vim, nano, etc

# 3. Localizar const escalas =
# 4. Substituir apenas os dados JSON
# 5. Salvar

# 6. Testar
open dashboard_final.html

# 7. Se funcionar, versionar
git add dashboard_final.html
git commit -m "Update: escalas $(date +%Y-%m-%d)"
git push
```

## Troubleshooting

### Erro: JSON inválido
```
Sintaxe incorreta no JSON
```
**Solução**: Verifique vírgulas, aspas e colchetes em https://jsonlint.com/

### Erro: Nenhum profissional aparece
```
Total: 0
```
**Solução**:
1. Verifique se `registros` tem dados
2. Verifique se `total` está correto
3. Abra Console (F12) para ver erros

### Erro: Busca não funciona
```
Profissionais não aparecem na busca
```
**Solução**: O atributo `data-search` é gerado automaticamente, não precisa editar

### Erro: Setores não aparecem organizados
```
Setores misturados
```
**Solução**: Use nomes de setores consistentes e completos

## Checklist de Atualização

Antes de publicar uma atualização:

- [ ] Backup feito
- [ ] JSON validado
- [ ] Total de profissionais correto
- [ ] Datas atualizadas (data_atualizacao, hora_atualizacao)
- [ ] Teste de abertura no navegador
- [ ] Teste de login
- [ ] Teste de busca
- [ ] Teste de navegação entre dias
- [ ] Teste de modais (Contatos, Ramais)
- [ ] Versionado no git

## Contatos para Suporte

- **Código/Bugs**: Abra issue no repositório
- **Dados**: Verifique com setor de escalas
- **Ramais**: Verifique com recepção/TI

---

**Última atualização**: 05/11/2025
**Arquivo de referência**: `/Users/joaoperes/escalaHRO/dashboard_final.html`
