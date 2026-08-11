(() => {
  const areaSelect = document.querySelector('#area_solicitante');
  const areaSections = document.querySelectorAll('[data-area-section]');

  if (!areaSelect || areaSections.length === 0) {
    return;
  }

  function setFieldsetState(fieldset, isActive) {
    fieldset.hidden = !isActive;
    fieldset.disabled = !isActive;
  }

  function updateSubcategoryOptions(areaSection) {
    const subcategorySelect = areaSection.querySelector('[data-subcategory-select]');
    const selectedSubcategory = subcategorySelect.value;
    const optionFieldsets = areaSection.querySelectorAll('[data-subcategory-options]');

    optionFieldsets.forEach((fieldset) => {
      setFieldsetState(fieldset, fieldset.dataset.subcategoryOptions === selectedSubcategory);
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

  areaSections.forEach((section) => {
    const subcategorySelect = section.querySelector('[data-subcategory-select]');
    subcategorySelect.addEventListener('change', () => updateSubcategoryOptions(section));
  });

  updateAreaSections();
})();
