# Dashboard Final - Hospital Regional do Oeste

## Visão Geral

Este é o arquivo HTML **FINAL e COMPLETO** do dashboard de escalas médicas do Hospital Regional do Oeste (HRO). Este arquivo foi criado para ser a **fonte única da verdade** e pode ser usado diretamente sem necessidade de scripts Python para gerar o HTML.

## Localização

**Arquivo:** `/Users/joaoperes/escalaHRO/dashboard_final.html`

## Características Completas

### 1. Interface Moderna
- **Design Dark Theme**: Interface escura e elegante
- **Gradiente Azul no Header**: Visual profissional com logo HRO
- **Responsive**: Funciona perfeitamente em desktop, tablet e mobile
- **Animações Suaves**: Transições e efeitos visuais profissionais

### 2. Sistema de Autenticação
- **Duas abas de login:**
  - **Profissional**: Login com email ou últimos 4 dígitos do telefone
  - **Outro Usuário**: Login com senha (senha padrão: `HRO-ALVF`)
- **Sessão persistente**: Mantém login durante a sessão do navegador
- **Blur no conteúdo**: Conteúdo fica desfocado até autenticar

### 3. Funcionalidades Principais

#### Navegação de Datas
- **Botão "Dia Anterior"**: Visualiza escalas do dia anterior
- **Botão "Hoje"**: Volta para a data atual
- Data exibida de forma destacada

#### Busca Inteligente
- Busca por nome do profissional
- Busca por setor
- Busca por turno
- Filtro em tempo real

#### Organização por Setores
- Setores agrupados e ordenados alfabeticamente
- Expandir/Colapsar individual por setor
- Botão "Minimizar/Expandir" para todos os setores

#### Organização por Turnos
- Setores com múltiplos turnos são automaticamente divididos em colunas
- Turnos ordenados: Matutino → Vespertino → Noturno → Diurno
- Badge colorido indicando tipo de turno (M/V/N/D/S)

#### Informações dos Profissionais
- Nome completo
- Horário de trabalho
- Tipo de turno com badge colorido
- Ícone WhatsApp (quando telefone disponível)
- Link direto para WhatsApp

### 4. Modais Adicionais

#### Modal de Contatos
- Lista completa de profissionais com telefones
- Busca por nome ou telefone
- Links diretos para WhatsApp
- Aviso sobre atualização de dados

#### Modal de Ramais
- Diretório completo de ramais do hospital
- Busca por departamento ou número
- Organizado alfabeticamente

### 5. Estatísticas
- Número total de profissionais escalados
- Número de setores ativos
- Atualizado automaticamente ao trocar de data

### 6. Cores dos Badges de Turno
- **Matutino (M)**: Amarelo (FFC107)
- **Vespertino (V)**: Laranja (FF9800)
- **Noturno (N)**: Azul (5C7CFA)
- **Diurno (D)**: Verde (4CAF50)
- **Sobreaviso (S)**: Roxo (9C27B0)
- **Outro**: Cinza (9E9E9E)

## Como Usar

### Uso Direto (Sem Scripts Python)

1. **Abrir o arquivo:**
   ```bash
   open /Users/joaoperes/escalaHRO/dashboard_final.html
   ```
   ou simplesmente clique duas vezes no arquivo

2. **Fazer login:**
   - Aba "Profissional": Digite email ou últimos 4 dígitos
   - Aba "Outro Usuário": Digite senha `HRO-ALVF`

3. **Navegar:**
   - Use os botões de data para ver diferentes dias
   - Use a busca para filtrar profissionais
   - Clique nos setores para expandir/colapsar
   - Clique nos ícones do WhatsApp para contatar profissionais

### Atualização de Dados

Os dados estão embutidos no JavaScript dentro do HTML. Para atualizar:

1. **Localize a seção de dados** (linha ~442):
   ```javascript
   const escalas = {
       "atual": { ... },
       "anterior": { ... }
   };
   ```

2. **Formato dos dados de escala:**
   ```javascript
   {
       "profissional": "Nome Completo",
       "setor": "Nome do Setor",
       "tipo_turno": "Plantão Matutino",
       "horario": "07:00/13:00"
   }
   ```

3. **Dados de profissionais** (para contatos e autenticação):
   ```javascript
   const profissionaisData = {
       "professionals": [
           {
               "name": "Nome Completo",
               "email": "email@hospital.com",
               "phone": "(49) 99999-9999",
               "last4": "9999"
           }
       ]
   };
   ```

4. **Dados de ramais:**
   ```javascript
   const ramaisData = {
       "departments": [
           {
               "name": "Nome do Departamento",
               "extensions": ["1234", "5678"]
           }
       ]
   };
   ```

### Integração com Script Python

O arquivo `update_escala_data_only.py` pode atualizar apenas os dados JSON, preservando todo o código:

```bash
python3 /Users/joaoperes/escalaHRO/update_escala_data_only.py
```

O script busca o padrão `const escalas = {...};` e substitui apenas o JSON.

## Estrutura do Código

### HTML (Linhas 1-339)
- Meta tags e configuração
- Importação de fontes (Inter e Merriweather)
- CSS embutido completo

### CSS (Linhas 6-338)
- Tema dark completo
- Responsividade mobile
- Estilos de print
- Animações e transições

### JavaScript (Linhas 442-fim)
- Dados embutidos (escalas, profissionais, ramais)
- Funções de autenticação
- Renderização dinâmica
- Filtros e buscas
- Gerenciamento de modais

## Recursos Técnicos

### Dependências Externas
- **Google Fonts**: Inter e Merriweather
- **Sem bibliotecas JavaScript**: Vanilla JS puro
- **Sem frameworks CSS**: CSS customizado

### Compatibilidade
- ✅ Chrome/Edge (versões recentes)
- ✅ Firefox (versões recentes)
- ✅ Safari (versões recentes)
- ✅ Mobile browsers

### Performance
- **Carregamento rápido**: Tudo embutido em um arquivo
- **Sem requests externos**: Exceto fontes do Google
- **Renderização eficiente**: Vanilla JS otimizado

## Personalização

### Cores do Tema

Para alterar as cores principais, edite as variáveis CSS:

```css
/* Background principal */
body {
    background: #1a1a2e;  /* Cor de fundo */
}

/* Header gradiente */
.header {
    background: linear-gradient(135deg, #0d3b66 0%, #1a5490 100%);
}

/* Cards de setores */
.category {
    background: #2d2d44;
    border: 1px solid #3d3d5c;
}
```

### Logo e Título

Para alterar o logo/título no header:

```html
<div class="header-logo">HRO</div>
<h2>Hospital Regional do Oeste</h2>
<p>Escala Médica - ALVF</p>
```

### Senha de Acesso

Para alterar a senha de "Outro Usuário":

```javascript
const senhaCorreta = 'HRO-ALVF';  // Linha ~516
```

## Impressão

O dashboard possui estilos otimizados para impressão:

- **Ctrl+P / Cmd+P**: Abre diálogo de impressão
- **Layout otimizado**: Remove controles e mantém apenas conteúdo
- **Cores preservadas**: Gradientes e badges mantidos
- **Page breaks**: Setores não quebram entre páginas

## Solução de Problemas

### Login não funciona
- Verifique se o email/telefone está cadastrado em `profissionaisData`
- Senha correta: `HRO-ALVF`

### Dados não aparecem
- Verifique se `escalas.atual.registros` tem dados
- Abra o console do navegador (F12) para ver erros

### WhatsApp não abre
- Verifique se o telefone está no formato correto: `(XX) XXXXX-XXXX`
- Telefones devem estar em `profissionaisData`

### Busca não funciona
- O atributo `data-search` é gerado automaticamente
- Busca é case-insensitive e busca em nome, setor e turno

## Backup e Versionamento

**IMPORTANTE**: Este arquivo deve ser versionado e tratado como fonte única da verdade.

```bash
# Fazer backup
cp dashboard_final.html dashboard_final_backup_$(date +%Y%m%d).html

# Versionar com git
git add dashboard_final.html
git commit -m "Update: dashboard final"
git push
```

## Próximos Passos

1. **Atualizar dados**: Use o script Python ou edite manualmente
2. **Testar**: Abra em diferentes navegadores
3. **Publicar**:
   - Copie para servidor web, ou
   - Use GitHub Pages, ou
   - Envie por email/WhatsApp
4. **Manter**: Use este como arquivo fonte para futuras modificações

## Suporte

Para dúvidas ou modificações:
- Edite este arquivo diretamente
- Use o script Python para atualizar apenas dados
- Consulte os comentários no código

---

**Versão**: 1.0
**Data**: 05/11/2025
**Autor**: Claude Code
**Licença**: Uso interno HRO
