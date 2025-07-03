import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { TrendingUp, TrendingDown, ShowChart } from '@mui/icons-material';

const OpenOrdersCard = ({ stats }) => {
  const totalRoe = stats.open_positions.total_roe_percentage || 0;
  const roeColor = totalRoe >= 0 ? 'success.main' : 'error.main';
  const formattedRoe = `${totalRoe >= 0 ? '+' : ''}${totalRoe.toFixed(2)}%`;

  return (
    <Card sx={{ bgcolor: '#333', color: 'white', height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Ordens Abertas</Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', mt: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <TrendingUp sx={{ color: 'success.main', mr: 1.5 }} />
            <Typography variant="body1">
              {stats.open_positions.positive_count} Positivas
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingDown sx={{ color: 'error.main', mr: 1.5 }} />
            <Typography variant="body1">
              {stats.open_positions.negative_count} Negativas
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
            <ShowChart sx={{ color: roeColor, mr: 1.5 }} />
            <Typography variant="body1" sx={{ color: roeColor, fontWeight: 'bold' }}>
              ROE Total: {formattedRoe}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default OpenOrdersCard; 