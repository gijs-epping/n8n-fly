import React, { useState, useMemo } from 'react';
import { Search, Plus, Minus, X, Divide, Type } from 'lucide-react';

const FormulaBuilder = () => {
  const attributeCodes = useMemo(() => {
    const baseAttrs = [
      { code: 'price', description: 'Product base price', category: 'pricing' },
      { code: 'sku', description: 'Product SKU', category: 'identification' },
      { code: 'tagline', description: 'Product tagline', category: 'text' },
      { code: 'weight', description: 'Product weight', category: 'physical' },
      { code: 'brand', description: 'Product brand name', category: 'identification' },
      { code: 'stock', description: 'Current stock level', category: 'inventory' },
      { code: 'color', description: 'Product color', category: 'physical' },
      { code: 'size', description: 'Product size', category: 'physical' },
      { code: 'material', description: 'Product material', category: 'physical' },
      { code: 'category', description: 'Product category', category: 'classification' },
    ];

    return [...baseAttrs, ...Array.from({ length: 90 }, (_, i) => ({
      code: `attribute_${i + 1}`,
      description: `Sample attribute ${i + 1}`,
      category: ['pricing', 'physical', 'text'][i % 3]
    }))];
  }, []);

  const [searchTerm, setSearchTerm] = useState('');
  const [formula, setFormula] = useState('');
  const [cursorPosition, setCursorPosition] = useState(0);
  const [recentlyUsed, setRecentlyUsed] = useState([]);

  // Enhanced search with prioritization
  const filteredAttributes = useMemo(() => {
    if (searchTerm.length < 1) return [];
    
    const searchLower = searchTerm.toLowerCase();
    return attributeCodes
      .map(attr => {
        // Calculate relevance score
        let score = 0;
        if (attr.code.toLowerCase().startsWith(searchLower)) score += 10;
        if (attr.code.toLowerCase().includes(searchLower)) score += 5;
        if (attr.description.toLowerCase().includes(searchLower)) score += 3;
        if (recentlyUsed.includes(attr.code)) score += 2;
        return { ...attr, score };
      })
      .filter(attr => attr.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);
  }, [searchTerm, attributeCodes, recentlyUsed]);

  const insertAttribute = (code) => {
    const newFormula = 
      formula.slice(0, cursorPosition) + 
      code + 
      formula.slice(cursorPosition);
    setFormula(newFormula);
    setSearchTerm('');
    // Update recently used
    setRecentlyUsed(prev => [code, ...prev.filter(c => c !== code)].slice(0, 5));
  };

  const insertOperator = (operator) => {
    const newFormula = 
      formula.slice(0, cursorPosition) + 
      ` ${operator} ` + 
      formula.slice(cursorPosition);
    setFormula(newFormula);
  };

  const handleTextareaChange = (e) => {
    setFormula(e.target.value);
    setCursorPosition(e.target.selectionStart);
  };

  const handleTextareaClick = (e) => {
    setCursorPosition(e.target.selectionStart);
  };

  // Basic syntax validation
  const validateFormula = (formula) => {
    try {
      // Check for balanced quotes
      const quotes = formula.split('"').length - 1;
      if (quotes % 2 !== 0) return { isValid: false, error: 'Unmatched quotes' };

      // Check for balanced parentheses
      const parens = formula.split('').reduce((count, char) => {
        if (char === '(') return count + 1;
        if (char === ')') return count - 1;
        return count;
      }, 0);
      if (parens !== 0) return { isValid: false, error: 'Unmatched parentheses' };

      return { isValid: true, error: null };
    } catch (err) {
      return { isValid: false, error: 'Invalid syntax' };
    }
  };

  const validation = validateFormula(formula);

  return (
    <div className="w-full max-w-2xl p-4 border rounded-lg shadow-sm">
      <div className="mb-4">
        <h2 className="text-xl font-bold">Formula Builder</h2>
      </div>
      <div className="space-y-4">
        {/* Search and attribute picker */}
        <div className="border rounded-lg p-4 bg-gray-50">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
            <input
              type="text"
              placeholder="Type to search attributes..."
              className="pl-8 pr-4 py-2 w-full border rounded"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          {searchTerm.length > 0 && (
            <div className="mt-2 border rounded bg-white shadow-sm">
              {filteredAttributes.length > 0 ? (
                filteredAttributes.map((attr) => (
                  <button
                    key={attr.code}
                    onClick={() => insertAttribute(attr.code)}
                    className="w-full text-left px-3 py-2 hover:bg-gray-100 flex justify-between items-center border-b last:border-b-0"
                  >
                    <div>
                      <span className="font-mono text-blue-600">{attr.code}</span>
                      <span className="ml-2 text-xs text-gray-500">{attr.category}</span>
                    </div>
                    <span className="text-sm text-gray-600">{attr.description}</span>
                  </button>
                ))
              ) : (
                <div className="px-3 py-2 text-gray-500">No matching attributes found</div>
              )}
            </div>
          )}
        </div>

        {/* Operators toolbar */}
        <div className="flex gap-2">
          <button onClick={() => insertOperator('+')} className="p-2 border rounded hover:bg-gray-50">
            <Plus className="h-4 w-4" />
          </button>
          <button onClick={() => insertOperator('-')} className="p-2 border rounded hover:bg-gray-50">
            <Minus className="h-4 w-4" />
          </button>
          <button onClick={() => insertOperator('*')} className="p-2 border rounded hover:bg-gray-50">
            <X className="h-4 w-4" />
          </button>
          <button onClick={() => insertOperator('/')} className="p-2 border rounded hover:bg-gray-50">
            <Divide className="h-4 w-4" />
          </button>
          <button onClick={() => insertOperator('"')} className="p-2 border rounded hover:bg-gray-50">
            <Type className="h-4 w-4" />
          </button>
        </div>

        {/* Formula input */}
        <div>
          <textarea
            placeholder="Build your formula here... (e.g. price * 0.85)"
            className={`w-full h-32 p-3 border rounded font-mono ${!validation.isValid ? 'border-red-300' : ''}`}
            value={formula}
            onChange={handleTextareaChange}
            onClick={handleTextareaClick}
          />
          {!validation.isValid && (
            <div className="text-red-500 text-sm mt-1">{validation.error}</div>
          )}
        </div>

        {/* Recently used attributes */}
        {recentlyUsed.length > 0 && (
          <div className="flex gap-2 flex-wrap">
            <span className="text-sm text-gray-500">Recently used:</span>
            {recentlyUsed.map(code => (
              <button
                key={code}
                onClick={() => insertAttribute(code)}
                className="text-sm px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
              >
                {code}
              </button>
            ))}
          </div>
        )}

        {/* Example formulas */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
          <p className="text-sm text-blue-800">
            <strong>Example formulas:</strong>
            <br />
            price * 0.85 (15% discount)
            <br />
            sku + " - " + tagline (combine SKU and tagline)
          </p>
        </div>
      </div>
    </div>
  );
};

export default FormulaBuilder;
