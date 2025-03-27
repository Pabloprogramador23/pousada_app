### [2024-03-26] Atualização da Lógica de Preços e Desconto por Diária

**Arquivos Modificados:**
- `pousada_app/reservas/models.py`
- `pousada_app/reservas/views.py`
- `pousada_app/reservas/templates/reservas/check_in_direto.html`
- `pousada_app/reservas/templates/reservas/check_in.html`

**Objetivo:**
Implementar uma nova lógica de preços e permitir descontos por diária no sistema de reservas.

**Alterações:**
1. Nova lógica de preços:
   - Valor base de R$140,00 para 1-2 pessoas
   - Adicional de R$70,00 por pessoa extra (acima de 2)
   - Valor mínimo de diária de R$100,00 (após desconto)

2. Adição do campo de desconto por diária no modelo Reserva
3. Implementação de interfaces para aplicar descontos no check-in direto e no check-in de reservas existentes
4. Atualização dos cálculos de valor total considerando o desconto

**Conversa:**
- **Pergunta:** "Quero que o preço de todos os quartos seja de 140,00 pra uma ou duas pessoas, ai se eu adicionar mais que isso eu quero que fvá aumentando 70,00 por pessoa."
- **Resposta:** "Implementaremos a lógica para que o preço base seja R$140,00 para 1-2 pessoas e aumente R$70,00 por pessoa adicional."
- **Pergunta:** "No check-in do recepcionista eu quero que tenho uma opção de desconto por diária"
- **Resposta:** "Adicionaremos um campo onde o recepcionista pode inserir um valor de desconto a ser aplicado por diária."
- **Decisão:** Implementamos campos de desconto nos formulários de check-in e check-in direto, e atualizamos o modelo e a lógica de cálculo do sistema.

**Resultados:**
- O sistema agora calcula automaticamente o preço da diária com base no número de pessoas
- Recepcionistas podem aplicar descontos diretamente no momento do check-in
- O valor total é recalculado automaticamente quando um desconto é aplicado
- O histórico da reserva registra os descontos aplicados

### [2024-03-26] Correção de Validação para Reservas Duplicadas

**Arquivos Modificados:**
- `pousada_app/reservas/models.py`
- `pousada_app/reservas/views.py`

**Objetivo:**
Corrigir um problema que permitia criar múltiplas reservas para o mesmo quarto no mesmo período.

**Alterações:**
1. Melhoria na função `verificar_disponibilidade`:
   - Busca mais precisa de quartos já reservados no período
   - Melhores mensagens de log para diagnóstico

2. Aprimoramento do método `clean()` na classe `Reserva`:
   - Verificação rigorosa de sobreposição de reservas
   - Mensagens de erro detalhadas sobre conflitos

3. Validações adicionais em `processar_check_in_direto`:
   - Verificação de datas inválidas (check-in após check-out, datas passadas)
   - Mensagens de erro detalhadas mostrando a reserva conflitante

4. Verificações extras em `realizar_check_in`:
   - Verificação de reservas conflitantes que possam ter sido criadas posteriormente
   - Alerta quando a data de check-in é anterior à data atual

**Conversa:**
- **Problema identificado:** "O sistema permitiu que eu conseguisse criar duas reservas com a mesma pessoa pro mesmo quarto"
- **Decisão:** Implementar validações mais rigorosas para impedir a criação de reservas sobrepostas para o mesmo quarto, mesmo quando feitas pelo mesmo hóspede.

**Resultados:**
- O sistema agora impede completamente a criação de reservas sobrepostas para o mesmo quarto
- As mensagens de erro são detalhadas e informativas, mostrando exatamente qual é o conflito
- A validação ocorre em todos os pontos do sistema onde uma reserva pode ser criada ou atualizada

### [2024-03-26] Adição de Botões de Cancelamento e Check-out no Calendário

**Arquivos Modificados:**
- `pousada_app/reservas/views.py`
- `pousada_app/reservas/urls.py`
- `pousada_app/financeiro/templates/financeiro/calendario.html`

**Objetivo:**
Implementar funcionalidades de cancelamento de reservas e check-out diretamente no calendário, para melhorar a usabilidade do sistema.

**Alterações:**
1. Adição de duas novas funções no backend:
   - `cancelar_reserva_ajax`: Para cancelar reservas via requisição AJAX
   - `checkout_reserva_ajax`: Para realizar check-out via requisição AJAX

2. Criação de modais:
   - Modal de cancelamento que solicita o motivo
   - Modal de check-out que permite adicionar observações

3. Aprimoramento do modal de detalhes do dia:
   - Adição de botões de ação (Detalhes, Cancelar, Check-out)
   - Botões condicionais baseados no status da reserva
   - Formatação melhorada para as informações exibidas

4. Atualização da view de detalhes do dia para incluir informações adicionais

**Conversa:**
- **Requisito do usuário:** "Ótimo, agora eu notei que não tem um botão de cancelar as reservas. Eu quero que esse botão fique no calendário, e no calendário também eu quero um botão pra realizar o checkout"
- **Decisão:** Implementar botões de ação no modal de detalhes do dia que é exibido ao clicar em uma data no calendário.

**Resultados:**
- Agora é possível cancelar reservas e realizar check-out diretamente a partir do calendário
- Os botões são exibidos apenas quando a ação é aplicável ao status atual da reserva
- A interface do calendário tornou-se mais funcional e completa
- Feedback visual é exibido quando as ações são realizadas com sucesso

### [2024-03-26] Melhorias Visuais no Calendário de Reservas

**Arquivos Modificados:**
- `pousada_app/reservas/views.py`
- `pousada_app/financeiro/templates/financeiro/calendario.html`

**Objetivo:**
Melhorar a visualização do calendário de reservas, tornando-o mais intuitivo e informativo, com destaque visual para os diferentes status de reservas e quartos ocupados.

**Alterações:**
1. Aprimoramento visual dos eventos no calendário:
   - Modificação do título para incluir número do quarto e status da reserva
   - Cores específicas e estilos CSS para cada status (pendente, confirmada, em andamento, etc.)
   - Melhor contraste com cores de texto adequadas para cada fundo

2. Adição de legenda de status:
   - Legenda com cores e descrições dos diferentes status
   - Posicionamento abaixo do calendário para fácil referência

3. Tooltip aprimorado:
   - Layout estruturado com cabeçalho, corpo e rodapé
   - Ícones para cada tipo de informação
   - Destaque para informações essenciais
   - Dica para o usuário sobre como acessar ações

4. Ajustes de responsividade:
   - Melhor visualização em dispositivos móveis
   - Textos que se adaptam ao espaço disponível

**Conversa:**
- **Problema identificado:** "Falta só marcar no calendário as cores de forma a ser mais visual."
- **Decisão:** Implementar um sistema de cores mais intuitivo e informativo, com legendas e tooltips aprimorados.

**Resultados:**
- Identificação mais rápida do status de cada reserva através das cores e estilos
- Visualização imediata de quais quartos estão ocupados em cada período
- Interface mais agradável e profissional
- Melhor experiência do usuário com informações mais acessíveis

### [2024-03-26] Correções no Calendário e na Lógica de Check-out

**Arquivos Modificados:**
- `pousada_app/reservas/views.py`
- `pousada_app/financeiro/templates/financeiro/calendario.html`

**Objetivo:**
Corrigir dois problemas importantes: (1) a falta de destaque visual para dias com reservas no calendário e (2) a possibilidade indevida de realizar check-out de reservas que ainda não tiveram check-in ou são futuras.

**Alterações:**
1. Melhoria visual no calendário:
   - Adição de classe CSS para destacar dias com reservas
   - Implementação de indicador numérico mostrando quantidade de reservas por dia
   - Estilização para tornar visualmente mais evidente os dias com reservas

2. Correção na lógica de check-out:
   - Implementação de verificações para impedir check-out de reservas que não tiveram check-in
   - Validação para evitar check-out de reservas com data de check-in futura
   - Mensagens de erro detalhadas explicando por que o check-out não é possível

3. Atualização da interface:
   - O botão de check-out agora só é exibido para reservas que podem realmente ter check-out
   - Adição de novas flags nos dados de reserva: `tem_checkin` e `pode_checkout`
   - Correção na formatação das observações do check-out para evitar erros

**Conversa:**
- **Problema identificado 1:** "Note que no calendário dia 28 tem reservas mas não está colorido"
- **Problema identificado 2:** "É possível fazer o check-out de uma reserva que ainda nem aconteceu. No caso o check-out é quando o quarto já está ocupado com o hóspede e ele vai embora"
- **Decisão:** Implementar destacamento visual para dias com reservas e corrigir a lógica de check-out para garantir que só seja possível realizar check-out de quartos realmente ocupados.

**Resultados:**
- Maior clareza visual no calendário, facilitando a identificação de dias com reservas
- Lógica de negócio corrigida para impedir operações que não fazem sentido
- Melhor experiência do usuário com botões de ação que só aparecem quando realmente podem ser utilizados
- Prevenção de erros na geração de histórico e status de quartos 

### [2024-03-27] Implementação de Testes e Correções no Sistema de Pagamentos

- **Arquivos Modificados**:
  - `pousada_app/financeiro/templates/financeiro/calendario.html`
  - `pousada_app/reservas/models.py`
  - `pousada_app/reservas/views.py`
  - `pousada_app/financeiro/forms.py`
  - `pousada_app/financeiro/tests.py`
  - `pousada_app/reservas/tests.py`
  - `pousada_app/quartos/tests.py`

- **Objetivo**:
  Implementar testes automatizados para validar o sistema de pagamentos e corrigir inconsistências identificadas durante a análise.

- **Mudanças Realizadas**:
  1. **Correções no Sistema de Pagamentos**:
     - Corrigidos os parâmetros enviados na API de pagamento AJAX (`calendario.html`)
     - Adicionados métodos ao modelo `Reserva` para centralizar o cálculo de saldos pendentes
     - Atualizada a lógica para permitir pagamentos para reservas em andamento
     - Corrigida a criação de registros de receita para todos os status permitidos

  2. **Implementação de Testes Automatizados**:
     - Criados testes para o módulo de pagamentos (validação de limites, registro correto)
     - Criados testes para o modelo de reserva (cálculo de valores, verificação de status)
     - Criados testes para check-in e check-out
     - Criados testes para o módulo de quartos (disponibilidade, preços com desconto)

- **Resultados**:
  Implementamos testes automatizados abrangentes que validam as funcionalidades críticas da aplicação, especialmente o sistema de pagamentos. As correções realizadas garantem maior consistência no registro de pagamentos e melhor integração entre os módulos.

- **Conversa**:
  - Pergunta: "Posso testar? Ou tem mais algum erro para consertar?"
  - Resposta: "Você pode testar o sistema. Os problemas identificados são potenciais incongruências que podem causar erros em determinadas situações, mas o fluxo básico deve funcionar. Sugiro corrigir os problemas mais críticos antes de testar."
  - Decisão: Foram implementadas correções para os problemas mais críticos antes dos testes.

### [2024-03-28] Melhorias no Sistema de Pagamentos e Implementação de Notificações

- **Arquivos Modificados/Criados**:
  - `pousada_app/reservas/views.py`
  - `pousada_app/reservas/urls.py`
  - `pousada_app/financeiro/templates/financeiro/calendario.html`
  - `pousada_app/reservas/templates/reservas/detalhe_reserva.html`
  - `pousada_app/notificacoes/models.py`

- **Objetivo**:
  Implementar melhorias no sistema de pagamentos e adicionar um sistema de notificações para alertar sobre pagamentos pendentes, check-ins e check-outs.

- **Mudanças Realizadas**:
  1. **Otimizações de Performance**:
     - Reduzida a repetição de cálculos na view `detalhes_dia` usando consultas agrupadas
     - Implementada pré-carga de pagamentos para melhorar o desempenho

  2. **Melhorias de Usabilidade**:
     - Adicionada confirmação visual ao registrar pagamentos através de um modal específico
     - Implementado histórico detalhado de pagamentos na interface de detalhes da reserva
     - Adicionados efeitos visuais para botões e indicadores de status de pagamento

  3. **Integração e Notificações**:
     - Criado módulo de notificações para alertar sobre pagamentos pendentes
     - Implementadas notificações para check-in e check-out programados para o dia atual
     - Adicionada funcionalidade para registrar pagamentos diretamente na página de detalhes da reserva

- **Resultados**:
  As melhorias implementadas tornaram o sistema mais eficiente, com melhor experiência do usuário e uma integração mais forte entre os módulos de reservas e financeiro. O novo sistema de notificações permite que os usuários sejam alertados sobre ações importantes a serem tomadas, como receber pagamentos pendentes ou realizar check-ins programados.

- **Decisões Técnicas**:
  - Utilizamos GenericForeignKey para permitir que o sistema de notificações se relacione com qualquer modelo
  - Implementamos métodos de classe para facilitar a criação de notificações específicas
  - Otimizamos as consultas ao banco de dados para reduzir o número de queries e melhorar o desempenho 

### [2024-03-28] Correção do Dashboard Financeiro e Calendário

- **Arquivos Modificados**:
  - `pousada_app/financeiro/views.py`

- **Objetivo**:
  Corrigir o problema dos dashboards financeiros e calendário não exibirem dados reais, mostrando valores zerados mesmo quando existem dados no banco de dados.

- **Mudanças Realizadas**:
  1. **Dashboard Financeiro**:
     - Substituição dos valores simulados por consultas reais ao banco de dados
     - Implementação de consultas para buscar pagamentos, receitas e despesas dentro do período selecionado
     - Correção do cálculo de receitas e despesas por mês para o gráfico de 6 meses
     - Adição de consultas para dados reais de ocupação, alertas e próximos pagamentos

  2. **Calendário de Reservas**:
     - Remoção de código de eventos simulados que estava substituindo os dados reais
     - Garantia de que o calendário utiliza corretamente as chamadas AJAX para buscar as reservas

- **Resultados**:
  O dashboard financeiro agora exibe os valores reais de receitas, despesas e saldo para o período selecionado. O gráfico de 6 meses mostra os dados históricos corretos e o resumo de ocupação reflete a situação atual dos quartos. O calendário de reservas exibe corretamente todas as reservas cadastradas no sistema.

- **Conversa**:
  - Problema reportado: "Nas dashboards e no calendário não aparecem os dados criados, é tudo 0 reais e o calendário não tem referências de reservas"
  - Causa identificada: As views estavam utilizando dados simulados/hardcoded em vez de buscar dados do banco de dados
  - Solução: Atualização das views para usar consultas reais ao banco de dados em vez de dados simulados

## 2024-05-25: Implementação do Sistema de Notificações

**Arquivos modificados/criados:**
- `pousada_app/notificacoes/models.py`
- `pousada_app/notificacoes/views.py`
- `pousada_app/notificacoes/urls.py`
- `pousada_app/notificacoes/admin.py`
- `pousada_app/notificacoes/apps.py`
- `pousada_app/notificacoes/signals.py`
- `pousada_app/notificacoes/templatetags/notificacoes_tags.py`
- `pousada_app/notificacoes/templates/notificacoes/listar.html`
- `pousada_app/notificacoes/templates/notificacoes/partials/notificacao_item.html`
- `pousada_app/notificacoes/templates/notificacoes/partials/menu_notificacoes.html`
- `pousada_app/pousada_app/templates/base/base.html`
- `pousada_app/pousada_app/urls.py`
- `pousada_app/reservas/models.py`
- `pousada_app/quartos/models.py`

**Objetivo:**
Implementar um sistema completo de notificações para alertar os usuários sobre eventos importantes do sistema, como novas reservas, pagamentos, alterações de status, check-ins pendentes e outras informações relevantes para a gestão da pousada.

**Alterações realizadas:**

1. **Criação do módulo de notificações:**
   - Modelo `Notificacao` para armazenar mensagens com título, conteúdo, categoria, tipo, status de leitura e links de ação
   - Categorias definidas: reserva, pagamento, hospede, quarto, sistema
   - Tipos de notificação: info, success, warning, danger
   
2. **Sistema de sinais para automação:**
   - Implementação de sinais (signals) para criar notificações automaticamente em eventos do sistema
   - Monitoramento de alterações em reservas, pagamentos, hóspedes e quartos
   - Notificações especiais para check-ins programados para hoje e amanhã
   
3. **Interface para visualização:**
   - Página de listagem de notificações com filtros por categoria e status
   - Menu dropdown no cabeçalho com contador de notificações não lidas
   - Tags de template para exibir contadores e listas de notificações
   - Funcionalidade para marcar notificações como lidas individualmente ou em grupo
   
4. **Modificações em modelos existentes:**
   - Adição de campo `status_anterior` em `Reserva` e `Quarto` para rastrear mudanças de status
   - Ajustes nas relações entre modelos para facilitar a criação de notificações
   
5. **AJAX e experiência do usuário:**
   - Endpoints JSON para atualização em tempo real das notificações
   - Indicadores visuais para novidades (badges e ícones)
   - Redirecionamentos diretos para as telas relevantes aos eventos notificados

**Resumo da conversa:**
O usuário solicitou a implementação de um sistema de notificações para melhorar a gestão da pousada. Desenvolvemos um sistema completo que monitora automaticamente eventos importantes como reservas, pagamentos e mudanças de status, notificando os usuários através de um menu dropdown no cabeçalho e uma página de listagem detalhada. 

A solução incluiu:
- Um modelo para armazenar diferentes tipos de notificações
- Um sistema de sinais para detectar eventos importantes automaticamente
- Tags de template para fácil integração em qualquer página
- Uma interface amigável para visualizar e gerenciar notificações
- Integração com os modelos existentes para monitoramento eficiente

O resultado é um sistema que mantém os usuários informados sobre eventos importantes sem que precisem verificar manualmente diferentes seções do sistema, melhorando a eficiência operacional da pousada. 

### [2024-03-26] Correções de Bugs e Templates Ausentes
- **Arquivos modificados/criados:**
  - `pousada_app/reservas/templates/reservas/confirmar.html` (novo)
  - `pousada_app/reservas/templates/reservas/cancelar.html` (novo)
  - `pousada_app/website/templates/website/quartos_lista.html` (novo)
  - `pousada_app/website/templates/website/quartos_categoria.html` (novo)
  - `pousada_app/website/templates/website/pagina.html` (novo)
  - `pousada_app/quartos/templates/quartos/quarto_list.html` (novo)
  - `pousada_app/quartos/templates/quartos/limpeza_manutencao_form.html` (novo)
  - `pousada_app/financeiro/templates/financeiro/pagamento_form.html` (novo)
  - `pousada_app/financeiro/templates/financeiro/pagamento_detail.html` (novo)
  - `pousada_app/reservas/views.py` (corrigido)
  - `pousada_app/notificacoes/models.py` (corrigido)
  - `pousada_app/quartos/models.py` (corrigido)
  - `pousada_app/financeiro/views.py` (adicionado método registrar_pagamento_ajax)
  - `pousada_app/financeiro/urls.py` (adicionada URL para pagamento via AJAX)

- **Objetivo:**
  - Resolver problemas e inconsistências identificados na aplicação
  - Criar templates ausentes que eram referenciados em views
  - Corrigir problemas de modelo e funções

- **Problemas corrigidos:**
  1. Adicionados templates ausentes que estavam listados como faltantes
  2. Corrigido o método `realizar_check_in` para usar `quantidade_adultos` e `quantidade_criancas` em vez de `acompanhantes`
  3. Corrigidos métodos `notificar_check_in_hoje` e `notificar_check_out_hoje` no modelo de notificações para comparar corretamente campos DateTime, usando `__date`
  4. Corrigidas URLs referenciadas em notificações para apontarem para os caminhos corretos
  5. Corrigido redirecionamento em `processar_check_in_direto` para usar `financeiro:calendario` em vez de `reservas:calendario`
  6. Melhorada a sincronização entre `status` e `disponivel` no modelo Quarto para evitar inconsistências
  7. Adicionado método `registrar_pagamento_ajax` no app financeiro
  8. Ajustada a URL para registrar pagamentos via AJAX

- **Conversa:**
  - Problema identificado: "Quero que você analise profundamente a aplicação e analise todas as templates e os respectivos modelos para achar falhas, e para achar templates que não existem mas que você colocou caminhos"
  - Diagnóstico realizado identificando problemas como templates ausentes, inconsistências nos modelos, erros nas URLs e problemas no tratamento de datas.
  - Implementada uma solução abrangente para resolver todos os problemas identificados. 