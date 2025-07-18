import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  Paper,
  Typography,
  IconButton,
  Collapse,
  Chip
} from '@mui/material';
import {
  FilterList,
  Clear,
  DateRange,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';

const DateFilter = ({ onFilterChange, currentFilters = {} }) => {
  const [expanded, setExpanded] = useState(false);
  const [startDate, setStartDate] = useState(currentFilters.start_date || '');
  const [endDate, setEndDate] = useState(currentFilters.end_date || '');
  const [limit, setLimit] = useState(currentFilters.limit || 100);

  const handleApplyFilter = () => {
    const filters = {};
    
    if (startDate) {
      filters.start_date = startDate;
    }
    
    if (endDate) {
      filters.end_date = endDate;
    }
    
    if (limit && limit !== 100) {
      filters.limit = limit;
    }
    
    onFilterChange(filters);
  };

  const handleClearFilter = () => {
    setStartDate('');
    setEndDate('');
    setLimit(100);
    onFilterChange({});
  };

  const hasActiveFilters = startDate || endDate || (limit && limit !== 100);

  const formatDateForDisplay = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  return (
    <Paper elevation={1} sx={{ mb: 2 }}>
      <Box sx={{ p: 2 }}>
        {/* Header com botão de expandir */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DateRange color="primary" />
            <Typography variant="h6">Filtros de Data</Typography>
            {hasActiveFilters && (
              <Chip
                label="Filtros ativos"
                color="primary"
                size="small"
                variant="outlined"
              />
            )}
          </Box>
          <IconButton onClick={() => setExpanded(!expanded)}>
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

        {/* Mostrar filtros ativos quando colapsado */}
        {!expanded && hasActiveFilters && (
          <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {startDate && (
              <Chip
                label={`De: ${formatDateForDisplay(startDate)}`}
                size="small"
                variant="outlined"
              />
            )}
            {endDate && (
              <Chip
                label={`Até: ${formatDateForDisplay(endDate)}`}
                size="small"
                variant="outlined"
              />
            )}
            {limit && limit !== 100 && (
              <Chip
                label={`Limite: ${limit}`}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        )}

        {/* Formulário de filtros */}
        <Collapse in={expanded}>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Data Inicial"
                  type="datetime-local"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  fullWidth
                  size="small"
                  InputLabelProps={{
                    shrink: true,
                  }}
                  helperText="Trades fechados a partir desta data"
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Data Final"
                  type="datetime-local"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  fullWidth
                  size="small"
                  InputLabelProps={{
                    shrink: true,
                  }}
                  helperText="Trades fechados até esta data"
                />
              </Grid>
              
              <Grid item xs={12} sm={2}>
                <TextField
                  label="Limite"
                  type="number"
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
                  fullWidth
                  size="small"
                  inputProps={{
                    min: 1,
                    max: 1000
                  }}
                  helperText="Máx. de trades"
                />
              </Grid>
              
              <Grid item xs={12} sm={2}>
                <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
                  <Button
                    variant="contained"
                    onClick={handleApplyFilter}
                    startIcon={<FilterList />}
                    fullWidth
                    size="small"
                  >
                    Aplicar
                  </Button>
                  
                  {hasActiveFilters && (
                    <Button
                      variant="outlined"
                      onClick={handleClearFilter}
                      startIcon={<Clear />}
                      fullWidth
                      size="small"
                      color="secondary"
                    >
                      Limpar
                    </Button>
                  )}
                </Box>
              </Grid>
            </Grid>
            
            {/* Dicas de uso */}
            <Box sx={{ mt: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                💡 <strong>Dicas:</strong> Use os filtros para encontrar trades específicos por período. 
                Deixe os campos vazios para ver todos os trades. O limite padrão é 100 trades.
              </Typography>
            </Box>
          </Box>
        </Collapse>
      </Box>
    </Paper>
  );
};

export default DateFilter;