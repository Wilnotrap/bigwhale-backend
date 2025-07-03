// Formatadores unificados para garantir consistência em toda a aplicação

/**
 * Formatar valor monetário com precisão consistente
 * @param {number|string} value - Valor a ser formatado
 * @param {boolean} showCurrency - Se deve mostrar o símbolo da moeda
 * @param {boolean} hideValues - Se deve ocultar os valores
 * @returns {string} Valor formatado
 */
export const formatCurrency = (value, showCurrency = true, hideValues = false) => {
  if (hideValues) return showCurrency ? '$***' : '***';
  if (value === null || value === undefined || value === '') return showCurrency ? '$0.00000' : '0.00000';
  
  const numValue = parseFloat(value);
  if (isNaN(numValue)) return showCurrency ? '$0.00000' : '0.00000';
  
  // Usa 5 casas decimais, conforme solicitado
  const formatted = numValue.toFixed(5);
  
  return showCurrency ? `$${formatted}` : formatted;
};

/**
 * Formatar valor numérico puro (sem moeda)
 * @param {number|string} value - Valor a ser formatado
 * @returns {string} Valor formatado
 */
export const formatValue = (value) => {
  return formatCurrency(value, false, false);
};

/**
 * Formatar PnL com sinal e cor
 * @param {number|string} value - Valor do PnL
 * @param {boolean} showCurrency - Se deve mostrar o símbolo da moeda
 * @returns {object} { formatted: string, color: string }
 */
export const formatPnL = (value, showCurrency = true) => {
  const numValue = parseFloat(value) || 0;
  const formatted = formatCurrency(value, showCurrency, false);
  const formattedWithSign = numValue >= 0 ? `+${formatted}` : formatted;
  
  let color;
  if (numValue > 0) color = '#4caf50'; // Verde
  else if (numValue < 0) color = '#f44336'; // Vermelho
  else color = '#757575'; // Cinza
  
  return {
    formatted: formattedWithSign,
    color: color
  };
};

/**
 * Formatar percentual
 * @param {number|string} value - Valor percentual
 * @param {boolean} hideValues - Se deve ocultar os valores
 * @returns {string} Valor formatado como percentual
 */
export const formatPercentage = (value, hideValues = false) => {
  if (hideValues) return '***%';
  if (value === null || value === undefined) return '0%';
  
  const numValue = parseFloat(value);
  if (isNaN(numValue)) return '0%';
  
  // Para percentuais muito pequenos, mostrar mais casas decimais
  if (Math.abs(numValue) < 0.01 && numValue !== 0) {
    return `${numValue >= 0 ? '+' : ''}${numValue.toFixed(6)}%`;
  }
  // Para percentuais pequenos, mostrar 4 casas decimais
  if (Math.abs(numValue) < 1) {
    return `${numValue >= 0 ? '+' : ''}${numValue.toFixed(4)}%`;
  }
  // Para percentuais maiores, mostrar 2 casas decimais
  return `${numValue >= 0 ? '+' : ''}${numValue.toFixed(2)}%`;
};

/**
 * Formatar data e hora
 * @param {string|number} timestamp - Timestamp em milissegundos
 * @returns {string} Data formatada no padrão brasileiro
 */
export const formatDateTime = (timestamp) => {
  if (!timestamp) return '-';
  
  try {
    const date = new Date(parseInt(timestamp));
    if (isNaN(date.getTime())) return '-';
    
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'America/Sao_Paulo'
    });
  } catch (error) {
    return '-';
  }
};

/**
 * Obter cor baseada no valor (positivo/negativo/neutro)
 * @param {number} value - Valor numérico
 * @returns {string} Cor em formato hex
 */
export const getColorByValue = (value) => {
  const numValue = parseFloat(value) || 0;
  if (numValue > 0) return '#4caf50'; // Verde
  if (numValue < 0) return '#f44336'; // Vermelho
  return '#757575'; // Cinza neutro
}; 