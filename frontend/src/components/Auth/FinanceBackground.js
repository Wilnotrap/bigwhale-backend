import React from 'react';
import './FinanceBackground.css';

const symbols = ['₿', '€', '$', '¥', '£', '₮', '📈', '📉', '💹', '🔄'];

const FinanceBackground = () => {
  return (
    <div className="finance-background">
      {[...Array(50)].map((_, i) => (
        <span
          key={i}
          className="floating-symbol"
          style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 10}s`
          }}
        >
          {symbols[Math.floor(Math.random() * symbols.length)]}
        </span>
      ))}
    </div>
  );
};

export default FinanceBackground; 