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