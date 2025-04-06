<template>
  <div class="autocomplete-container" ref="container"></div>
</template>

<script>
export default {
  name: "AddressAutocomplete",
  props: {
    placeholder: {
      type: String,
      default: "Enter an address here"
    },
    modelValue: {
      type: String,
      default: ""
    }
  },
  emits: ['update:modelValue', 'place-selected'],
  mounted() {
    // The addressAutocomplete function initializes the autocomplete field.
    function addressAutocomplete(containerElement, callback, options) {
      // Create input element
      const inputElement = document.createElement("input");
      inputElement.setAttribute("type", "text");
      inputElement.setAttribute("placeholder", options.placeholder);
      inputElement.value = options.initialValue || "";
      containerElement.appendChild(inputElement);

      // Add clear button to the input field
      const clearButton = document.createElement("div");
      clearButton.classList.add("clear-button");
      addIcon(clearButton);
      clearButton.addEventListener("click", (e) => {
        e.stopPropagation();
        inputElement.value = "";
        callback(null);
        clearButton.classList.remove("visible");
        closeDropDownList();
      });
      containerElement.appendChild(clearButton);

      // Variables to store current state
      let currentItems;
      let currentPromiseReject;
      let focusedItemIndex;

      // Listen for user input
      inputElement.addEventListener("input", function () {
        const currentValue = this.value;
        closeDropDownList();

        // Cancel any ongoing requests
        if (currentPromiseReject) {
          currentPromiseReject({ canceled: true });
        }

        if (!currentValue) {
          clearButton.classList.remove("visible");
          return false;
        }

        clearButton.classList.add("visible");

        // Fetch autocomplete suggestions
        const promise = new Promise((resolve, reject) => {
          currentPromiseReject = reject;
          const apiKey = import.meta.env.VITE_APP_GEOAPIFY_API_KEY;
          let url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(
            currentValue
          )}&limit=5&apiKey=${apiKey}`;

          if (options.type) {
            url += `&type=${options.type}`;
          }

          fetch(url).then((response) => {
            if (response.ok) {
              response.json().then((data) => resolve(data));
            } else {
              response.json().then((data) => reject(data));
            }
          });
        });

        promise.then(
          (data) => {
            currentItems = data.features;
            const autocompleteItemsElement = document.createElement("div");
            autocompleteItemsElement.setAttribute("class", "autocomplete-items");
            containerElement.appendChild(autocompleteItemsElement);

            // Create an item for each suggestion
            data.features.forEach((feature, index) => {
              const itemElement = document.createElement("div");
              itemElement.innerHTML = feature.properties.formatted;
              itemElement.addEventListener("click", function () {
                inputElement.value = currentItems[index].properties.formatted;
                callback(currentItems[index]);
                closeDropDownList();
              });
              autocompleteItemsElement.appendChild(itemElement);
            });
          },
          (err) => {
            if (!err.canceled) {
              console.error(err);
            }
          }
        );
      });

      // Keyboard navigation for the autocomplete list
      inputElement.addEventListener("keydown", function (e) {
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
            const event = document.createEvent("Event");
            event.initEvent("input", true, true);
            inputElement.dispatchEvent(event);
          }
        }
      });

      // Set the active suggestion in the list
      function setActive(items, index) {
        if (!items || !items.length) return;
        for (let i = 0; i < items.length; i++) {
          items[i].classList.remove("autocomplete-active");
        }
        items[index].classList.add("autocomplete-active");
        inputElement.value = currentItems[index].properties.formatted;
        callback(currentItems[index]);
      }

      // Close the autocomplete dropdown list
      function closeDropDownList() {
        const autocompleteItemsElement = containerElement.querySelector(".autocomplete-items");
        if (autocompleteItemsElement) {
          containerElement.removeChild(autocompleteItemsElement);
        }
        focusedItemIndex = -1;
      }

      // Add an SVG icon to the clear button
      function addIcon(buttonElement) {
        const svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svgElement.setAttribute("viewBox", "0 0 24 24");
        svgElement.setAttribute("height", "24");
        const iconElement = document.createElementNS("http://www.w3.org/2000/svg", "path");
        iconElement.setAttribute(
          "d",
          "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
        );
        iconElement.setAttribute("fill", "currentColor");
        svgElement.appendChild(iconElement);
        buttonElement.appendChild(svgElement);
      }

      // Close the dropdown when clicking outside
      document.addEventListener("click", function (e) {
        if (e.target !== inputElement) {
          closeDropDownList();
        } else if (!containerElement.querySelector(".autocomplete-items")) {
          const event = document.createEvent("Event");
          event.initEvent("input", true, true);
          inputElement.dispatchEvent(event);
        }
      });
    }

    // Initialize the autocomplete field on the component's container element.
    addressAutocomplete(
      this.$refs.container,
      (data) => {
        this.$emit('update:modelValue', data ? data.properties.formatted : '');
        this.$emit('place-selected', data);
      },
      {
        placeholder: this.placeholder,
        initialValue: this.modelValue
      }
    );
  }
};
</script>

<style scoped>
.autocomplete-container {
  position: relative;
  width: 100%;
}

.autocomplete-container input {
  width: 100%;
  height: 56px;
  padding: 0 16px;
  padding-right: 40px;
  font-size: 1rem;
  line-height: 1.5;
  color: rgba(var(--v-theme-on-surface), 0.87);
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 12px;
  transition: all 0.2s ease;
  outline: none;
}

.autocomplete-container input:hover {
  border-color: rgba(var(--v-theme-on-surface), 0.86);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.autocomplete-container input:focus {
  border-color: rgb(var(--v-theme-primary));
  border-width: 2px;
  padding-left: 15px;
  padding-right: 39px;
}

.autocomplete-items {
  position: absolute;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 12px;
  box-shadow: 0 4px 25px 0 rgba(0, 0, 0, 0.1);
  z-index: 99;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: rgb(var(--v-theme-surface));
  padding: 6px 0;
  max-height: 300px;
  overflow-y: auto;
}

.autocomplete-items div {
  padding: 12px 16px;
  cursor: pointer;
  color: rgba(var(--v-theme-on-surface), 0.87);
  font-size: 1rem;
  line-height: 1.5;
  min-height: 48px;
  display: flex;
  align-items: center;
  margin: 0 6px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.autocomplete-items div:not(:last-child) {
  border-bottom: 1px solid rgba(var(--v-border-color), 0.08);
}

.autocomplete-items div:hover {
  background-color: rgba(var(--v-theme-primary), 0.08);
}

.autocomplete-items .autocomplete-active {
  background-color: rgba(var(--v-theme-primary), 0.12);
  color: rgb(var(--v-theme-primary));
}

.clear-button {
  color: rgba(var(--v-theme-on-surface), 0.4);
  cursor: pointer;
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  height: 24px;
  width: 24px;
  display: none;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.clear-button.visible {
  display: flex;
}

.clear-button:hover {
  color: rgba(var(--v-theme-on-surface), 0.6);
}
</style> 