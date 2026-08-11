(() => {
  const areaSelect = document.querySelector('#area_solicitante');
  const areaSections = document.querySelectorAll('[data-area-section]');
  const selectionModeControls = document.querySelectorAll('[data-selection-mode] input');
  const selectionModeHelp = document.querySelector('[data-selection-mode-help]');

  if (!areaSelect || areaSections.length === 0 || selectionModeControls.length === 0) {
    return;
  }

  function getSelectionMode() {
    const selectedMode = Array.from(selectionModeControls).find((control) => control.checked);
    return selectedMode?.value === 'checkbox' ? 'checkbox' : 'radio';
  }

  function setFieldsetState(fieldset, isActive) {
    fieldset.hidden = !isActive;
    fieldset.disabled = !isActive;
  }

  function updateSelectionRequirement(fieldset) {
    const inputs = Array.from(fieldset.querySelectorAll('.option input'));

    inputs.forEach((input) => {
      input.required = false;
    });

    if (fieldset.disabled || inputs.length === 0) {
      return;
    }

    if (getSelectionMode() === 'radio') {
      inputs.forEach((input) => {
        input.required = true;
      });
      return;
    }

    if (!inputs.some((input) => input.checked)) {
      inputs[0].required = true;
    }
  }

  function setSelectionMode(fieldset) {
    const mode = getSelectionMode();
    const inputs = Array.from(fieldset.querySelectorAll('.option input'));
    const checkedStates = inputs.map((input) => input.checked);
    const firstCheckedIndex = checkedStates.indexOf(true);

    inputs.forEach((input) => {
      input.type = mode;
    });

    inputs.forEach((input, index) => {
      input.checked = mode === 'checkbox'
        ? checkedStates[index]
        : index === firstCheckedIndex;
    });

    updateSelectionRequirement(fieldset);
  }

  function updateSelectionModeHelp() {
    if (!selectionModeHelp) {
      return;
    }

    selectionModeHelp.textContent = getSelectionMode() === 'checkbox'
      ? 'Selección múltiple: elija una o varias opciones.'
      : 'Selección única: elija exactamente una opción.';
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
        setSelectionMode(fieldset);
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

  selectionModeControls.forEach((control) => {
    control.addEventListener('change', () => {
      document.querySelectorAll('[data-subcategory-options]').forEach((fieldset) => {
        if (!fieldset.disabled) {
          setSelectionMode(fieldset);
        }
      });
      updateSelectionModeHelp();
    });
  });

  areaSelect.addEventListener('change', updateAreaSections);

  areaSections.forEach((section) => {
    const subcategorySelect = section.querySelector('[data-subcategory-select]');
    subcategorySelect.addEventListener('change', () => updateSubcategoryOptions(section));

    section.querySelectorAll('[data-subcategory-options] .option input').forEach((input) => {
      input.addEventListener('change', () => {
        const fieldset = input.closest('[data-subcategory-options]');
        if (fieldset && !fieldset.disabled) {
          updateSelectionRequirement(fieldset);
        }
      });
    });
  });

  updateAreaSections();
  updateSelectionModeHelp();
})();
