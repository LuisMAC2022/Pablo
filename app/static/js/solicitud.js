(() => {
  const areaSelect = document.querySelector('#area_solicitante');
  const areaSections = document.querySelectorAll('[data-area-section]');
  const selectionModeInputs = document.querySelectorAll('[data-selection-mode-input]');
  const selectionModeHelp = document.querySelector('[data-selection-mode-help]');
  const validSelectionModes = new Set(['radio', 'checkbox']);

  if (
    !areaSelect
    || areaSections.length === 0
    || selectionModeInputs.length === 0
  ) {
    return;
  }

  function setFieldsetState(fieldset, isActive) {
    fieldset.hidden = !isActive;
    fieldset.disabled = !isActive;
  }

  function getServiceOptions(fieldset) {
    return Array.from(fieldset.querySelectorAll('[data-service-option]'));
  }

  function updateCheckboxRequirement(fieldset) {
    const options = getServiceOptions(fieldset);
    const hasSelection = options.some((option) => option.checked);

    options.forEach((option, index) => {
      option.required = option.type === 'radio' || (index === 0 && !hasSelection);
    });
  }

  function getSelectionMode() {
    const selectedMode = Array.from(selectionModeInputs)
      .find((input) => input.checked)?.value;

    return validSelectionModes.has(selectedMode) ? selectedMode : 'radio';
  }

  function setServiceOptionsMode(fieldset, mode) {
    if (!fieldset || fieldset.disabled || !validSelectionModes.has(mode)) {
      return;
    }

    const options = getServiceOptions(fieldset);

    if (mode === 'radio') {
      const selectedOptions = options.filter((option) => option.checked);
      selectedOptions.slice(1).forEach((option) => {
        option.checked = false;
      });
    }

    options.forEach((option) => {
      option.type = mode;
    });

    updateCheckboxRequirement(fieldset);
  }

  function updateSelectionModeControl(mode) {
    if (selectionModeHelp) {
      selectionModeHelp.textContent = mode === 'checkbox'
        ? 'Puede seleccionar una o varias opciones.'
        : 'Debe seleccionar exactamente una opción.';
    }
  }

  function getActiveOptionsFieldset() {
    return Array.from(document.querySelectorAll('[data-subcategory-options]'))
      .find((fieldset) => !fieldset.hidden && !fieldset.disabled);
  }

  function updateSubcategoryOptions(areaSection) {
    const subcategorySelect = areaSection.querySelector('[data-subcategory-select]');
    const selectedSubcategory = subcategorySelect.value;
    const optionFieldsets = areaSection.querySelectorAll('[data-subcategory-options]');

    optionFieldsets.forEach((fieldset) => {
      const isActive = !areaSection.disabled
        && fieldset.dataset.subcategoryOptions === selectedSubcategory;

      setFieldsetState(fieldset, isActive);
      if (isActive) {
        setServiceOptionsMode(fieldset, getSelectionMode());
      }
    });
  }

  function updateAreaSections() {
    const selectedArea = areaSelect.value;

    areaSections.forEach((section) => {
      const isActive = section.dataset.areaSection === selectedArea;
      const subcategorySelect = section.querySelector('[data-subcategory-select]');

      setFieldsetState(section, isActive);
      subcategorySelect.disabled = !isActive;
      subcategorySelect.required = isActive;

      if (!isActive) {
        subcategorySelect.value = '';
      }

      updateSubcategoryOptions(section);
    });
  }

  areaSelect.addEventListener('change', updateAreaSections);

  selectionModeInputs.forEach((input) => {
    input.addEventListener('change', () => {
      if (!input.checked || !validSelectionModes.has(input.value)) {
        return;
      }

      setServiceOptionsMode(getActiveOptionsFieldset(), input.value);
      updateSelectionModeControl(input.value);
    });
  });

  areaSections.forEach((section) => {
    const subcategorySelect = section.querySelector('[data-subcategory-select]');
    subcategorySelect.addEventListener('change', () => updateSubcategoryOptions(section));

    section.querySelectorAll('[data-service-option]').forEach((option) => {
      option.addEventListener('change', () => {
        const fieldset = option.closest('[data-subcategory-options]');
        if (fieldset && !fieldset.disabled && option.type === 'checkbox') {
          updateCheckboxRequirement(fieldset);
        }
      });
    });
  });

  const initialMode = getSelectionMode();
  updateSelectionModeControl(initialMode);
  updateAreaSections();
})();
