import React, { useEffect, useRef, useState } from 'react';

export function ReactAutocomplete({ onSelect, placeholder = "Enter an address here" }) {
  const containerRef = useRef(null);
  const inputRef = useRef(null);
  const [items, setItems] = useState([]);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const [showClear, setShowClear] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const timeoutRef = useRef(null);

  useEffect(() => {
    let currentPromiseReject = null;

    const handleInput = async () => {
      const value = inputRef.current.value;
      setInputValue(value);
      
      if (currentPromiseReject) {
        currentPromiseReject({ canceled: true });
      }

      if (!value) {
        setShowClear(false);
        setItems([]);
        return;
      }

      setShowClear(true);

      // Clear any existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Set a new timeout
      timeoutRef.current = setTimeout(async () => {
        try {
          const apiKey = import.meta.env.VITE_APP_GEOAPIFY_API_KEY;
          const url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(value)}&limit=5&apiKey=${apiKey}`;
          
          const response = await fetch(url);
          if (response.ok) {
            const data = await response.json();
            // Only update if the input value hasn't changed
            if (value === inputRef.current.value) {
              setItems(data.features);
            }
          }
        } catch (err) {
          if (!err.canceled) {
            console.error(err);
          }
        }
      }, 300); // 300ms debounce
    };

    const handleKeyDown = (e) => {
      if (!items.length) return;

      if (e.keyCode === 40) { // Down arrow
        e.preventDefault();
        setFocusedIndex(prev => prev < items.length - 1 ? prev + 1 : 0);
      } else if (e.keyCode === 38) { // Up arrow
        e.preventDefault();
        setFocusedIndex(prev => prev > 0 ? prev - 1 : items.length - 1);
      } else if (e.keyCode === 13 && focusedIndex > -1) { // Enter
        e.preventDefault();
        handleSelect(items[focusedIndex]);
      }
    };

    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setItems([]);
        setFocusedIndex(-1);
      }
    };

    const input = inputRef.current;
    input.addEventListener('input', handleInput);
    input.addEventListener('keydown', handleKeyDown);
    document.addEventListener('click', handleClickOutside);

    return () => {
      input.removeEventListener('input', handleInput);
      input.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('click', handleClickOutside);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [items, focusedIndex]);

  const handleSelect = (item) => {
    if (item) {
      inputRef.current.value = item.properties.formatted;
      setInputValue(item.properties.formatted);
      onSelect(item);
    }
    setItems([]);
    setFocusedIndex(-1);
  };

  const handleClear = (e) => {
    e.stopPropagation();
    inputRef.current.value = '';
    setInputValue('');
    onSelect(null);
    setShowClear(false);
    setItems([]);
    setFocusedIndex(-1);
  };

  return (
    <div className="autocomplete-container" ref={containerRef}>
      <input
        ref={inputRef}
        type="text"
        placeholder={placeholder}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
      />
      {showClear && (
        <div className="clear-button visible" onClick={handleClear}>
          <svg viewBox="0 0 24 24" height="24">
            <path
              d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
              fill="currentColor"
            />
          </svg>
        </div>
      )}
      {items.length > 0 && (
        <div className="autocomplete-items">
          {items.map((item, index) => (
            <div
              key={index}
              className={index === focusedIndex ? 'autocomplete-active' : ''}
              onClick={() => handleSelect(item)}
            >
              {item.properties.formatted}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ReactAutocomplete; 