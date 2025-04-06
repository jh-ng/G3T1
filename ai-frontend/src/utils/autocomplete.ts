interface AutocompleteOptions {
  placeholder?: string;
  apiKey: string;
}

interface GeoJSONFeature {
  properties: {
    formatted: string;
  };
}

export function addressAutocomplete(
  containerElement: HTMLElement,
  callback: (data: GeoJSONFeature | null) => void,
  options: AutocompleteOptions
) {
  // Clear any existing content in the container
  while (containerElement.firstChild) {
    containerElement.removeChild(containerElement.firstChild);
  }

  // Create input element
  const inputElement = document.createElement("input");
  inputElement.setAttribute("type", "text");
  inputElement.setAttribute("placeholder", options.placeholder || "Enter a location");
  inputElement.setAttribute("required", "true");
  inputElement.classList.add("form-input");
  containerElement.appendChild(inputElement);

  let currentItems: GeoJSONFeature[] = [];
  let currentPromiseReject: ((reason: any) => void) | null = null;
  let focusedItemIndex = -1;

  const handleInput = function(e: Event) {
    const currentValue = (e.target as HTMLInputElement).value;

    closeDropDownList();

    if (currentPromiseReject) {
      currentPromiseReject({
        canceled: true
      });
    }

    if (!currentValue) {
      return false;
    }

    const promise = new Promise((resolve, reject) => {
      currentPromiseReject = reject;

      const url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(currentValue)}&limit=5&apiKey=${options.apiKey}`;

      fetch(url)
        .then(response => {
          if (response.ok) {
            response.json().then(data => resolve(data));
          } else {
            response.json().then(data => reject(data));
          }
        });
    });

    promise.then((data: any) => {
      currentItems = data.features;

      const autocompleteItemsElement = document.createElement("div");
      autocompleteItemsElement.setAttribute("class", "autocomplete-items");
      containerElement.appendChild(autocompleteItemsElement);

      data.features.forEach((feature: GeoJSONFeature, index: number) => {
        const itemElement = document.createElement("DIV");
        itemElement.innerHTML = feature.properties.formatted;

        itemElement.addEventListener("click", function() {
          inputElement.value = currentItems[index].properties.formatted;
          callback(currentItems[index]);
          closeDropDownList();
        });

        autocompleteItemsElement.appendChild(itemElement);
      });
    }, (err) => {
      if (!err.canceled) {
        console.log(err);
      }
    });
  };

  const handleKeyDown = function(e: KeyboardEvent) {
    const autocompleteItemsElement = containerElement.querySelector(".autocomplete-items");
    if (autocompleteItemsElement) {
      const itemElements = autocompleteItemsElement.getElementsByTagName("div");
      if (e.keyCode === 40) {
        e.preventDefault();
        focusedItemIndex = focusedItemIndex !== itemElements.length - 1 ? focusedItemIndex + 1 : 0;
        setActive(itemElements, focusedItemIndex);
      } else if (e.keyCode === 38) {
        e.preventDefault();
        focusedItemIndex = focusedItemIndex !== 0 ? focusedItemIndex - 1 : itemElements.length - 1;
        setActive(itemElements, focusedItemIndex);
      } else if (e.keyCode === 13) {
        e.preventDefault();
        if (focusedItemIndex > -1) {
          closeDropDownList();
        }
      }
    } else {
      if (e.keyCode === 40) {
        const event = document.createEvent('Event');
        event.initEvent('input', true, true);
        inputElement.dispatchEvent(event);
      }
    }
  };

  const handleDocumentClick = function(e: Event) {
    if (e.target !== inputElement) {
      closeDropDownList();
    } else if (!containerElement.querySelector(".autocomplete-items")) {
      const event = document.createEvent('Event');
      event.initEvent('input', true, true);
      inputElement.dispatchEvent(event);
    }
  };

  // Add event listeners
  inputElement.addEventListener("input", handleInput);
  inputElement.addEventListener("keydown", handleKeyDown);
  document.addEventListener("click", handleDocumentClick);

  function setActive(items: HTMLCollectionOf<Element>, index: number) {
    if (!items || !items.length) return false;

    for (let i = 0; i < items.length; i++) {
      items[i].classList.remove("autocomplete-active");
    }

    items[index].classList.add("autocomplete-active");
    inputElement.value = currentItems[index].properties.formatted;
    callback(currentItems[index]);
  }

  function closeDropDownList() {
    const autocompleteItemsElement = containerElement.querySelector(".autocomplete-items");
    if (autocompleteItemsElement) {
      containerElement.removeChild(autocompleteItemsElement);
    }
    focusedItemIndex = -1;
  }

  // Return a cleanup function
  return () => {
    inputElement.removeEventListener("input", handleInput);
    inputElement.removeEventListener("keydown", handleKeyDown);
    document.removeEventListener("click", handleDocumentClick);
    while (containerElement.firstChild) {
      containerElement.removeChild(containerElement.firstChild);
    }
  };
} 