# Onde a extração roda (e por quê)

**Desde 16/08/2026 a extração precisa sair de uma rede brasileira.**

## O que aconteceu

O pipeline rodava em runner hospedado do GitHub Actions (`ubuntu-latest`), que
sai dos EUA. Em 16/08/2026 as execuções começaram a falhar no login com
`NoSuchElementException`: o campo de e-mail não existia na página.

A causa não era o seletor. O CloudFront do `escala.med.br` passou a responder a
requisições vindas de fora do Brasil com o `index.html` (2829 bytes,
`x-cache: Error from cloudfront`) **no lugar de qualquer arquivo pedido** —
`scripts/vendor.*.js`, `scripts/scripts.*.js`, CSS, até o `favicon.ico`. Sem os
bundles, o AngularJS nunca inicializa, o `ui-view` fica vazio e nenhum campo do
formulário existe. Testado no runner com vários User-Agents (nenhum, curl,
Chrome completo, com Referer): todos bloqueados. Da mesma máquina no Brasil, os
mesmos URLs devolvem o bundle real de ~1,5 MB.

## Como está montado hoje

| Peça | Onde roda | Papel |
|---|---|---|
| `Atualizar Escala Diária HRO` | runner self-hosted num VPS brasileiro (label `escala-br`) | extrai, gera o dashboard e faz push |
| `Vigia da atualização da escala` | runner hospedado do GitHub | 07h22 BRT, confere se o site publicou a data de hoje e abre issue se não |
| Vercel | — | publica automaticamente a cada push em `main` |

A variável de repositório `RUNNER_LABEL` decide onde o job roda:

- `RUNNER_LABEL=escala-br` → runner próprio (situação normal)
- variável ausente → volta para `ubuntu-latest`, que **vai falhar** enquanto o
  bloqueio existir, mas falha de forma visível em vez de ficar enfileirado

## Provisionar (ou reprovisionar) o VPS

```bash
./scripts/provisionar_runner_br.sh
```

O wizard cria a VM com você, confirma que aquele IP recebe os arquivos reais do
`escala.med.br`, instala Python/Chrome/chromedriver, registra o runner como
serviço, seta `RUNNER_LABEL` e roda o workflow para validar.

## Diagnóstico quando o login voltar a falhar

O job sobe um artifact `error-logs` com screenshot, HTML, console do navegador e
lista de recursos carregados de cada tentativa de login. Se o console acusar
`Uncaught SyntaxError: Unexpected token '<'` nos arquivos de `escala.med.br`, é
de novo o bloqueio por origem da requisição — confira de onde o job rodou.

## Se o bloqueio for removido

Se o `escala.med.br` voltar a atender de qualquer lugar, basta
`gh variable delete RUNNER_LABEL` para o pipeline voltar aos runners do GitHub, e
o VPS pode ser desligado.
