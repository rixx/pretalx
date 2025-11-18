// SPDX-FileCopyrightText: 2025-present Tobias Kunze
// SPDX-License-Identifier: Apache-2.0


const setupPreferenceModal = (form) => {
    const tableName = form.dataset.tableName
    const dialog = form.closest("dialog")
    const availableSelect = form.querySelector(".available-columns")
    const selectedSelect = form.querySelector(".selected-columns")
    const sortingRowsContainer = form.querySelector(".sorting-rows-container")
    const sortingRowTemplate = form.querySelector(".sorting-row-template")
    const addSortRowBtn = form.querySelector(".add-sort-row")

    const moveOptions = (from, to, selected = false) => {
      const options = Array.from(from.selectedOptions)
      if (options.length === 0) return

      options.forEach((option) => {
        const newOption = option.cloneNode(true)
        newOption.selected = selected
        to.appendChild(newOption)
        option.remove()
      })

      if (!to.classList.contains("selected-columns")) {
        sortSelectOptions(to)
      }
    }

    const sortSelectOptions = (select) => {
      const options = Array.from(select.options)
      options.sort((a, b) => a.text.localeCompare(b.text))
      select.innerHTML = ""
      options.forEach((option) => select.appendChild(option))
    }

    const moveOption = (select, direction) => {
      const options = Array.from(select.selectedOptions)
      if (options.length === 0) return

      if (direction === "up") {
        options.forEach((option) => {
          const prev = option.previousElementSibling
          if (prev) {
            select.insertBefore(option, prev)
          }
        })
      } else {
        options.reverse().forEach((option) => {
          const next = option.nextElementSibling
          if (next) {
            select.insertBefore(next, option)
          }
        })
      }
    }

    const getSortRowLabels = () => ["Primary", "Secondary", "Tertiary", "Quaternary", "Quinary"]

    const updateSortRowLabels = () => {
      const rows = sortingRowsContainer.querySelectorAll(".sorting-row")
      const labels = getSortRowLabels()
      rows.forEach((row, index) => {
        const label = row.querySelector(".sort-label")
        if (label) {
          label.textContent = `${labels[index] || `Sort ${index + 1}`}:`
        }
      })
    }

    const createSortRow = (field = "", direction = "") => {
      const clone = sortingRowTemplate.cloneNode(true)
      clone.classList.remove("d-none")
      const row = clone.querySelector(".sorting-row")

      const fieldSelect = row.querySelector(".sort-field")
      const directionSelect = row.querySelector(".sort-direction")

      if (field) {
        if (field.startsWith("-")) {
          fieldSelect.value = field.substring(1)
          directionSelect.value = "-"
        } else {
          fieldSelect.value = field
          directionSelect.value = ""
        }
      }

      row.querySelector(".remove-sort-row")?.addEventListener("click", () => {
        row.parentElement.remove()
        updateSortRowLabels()
      })

      sortingRowsContainer.appendChild(clone)
      updateSortRowLabels()
      return row
    }

    const initializeSortRows = () => {
      const currentOrderingEl = document.getElementById(`current-ordering-${tableName}`)
      let currentOrdering = []

      if (currentOrderingEl) {
        try {
          currentOrdering = JSON.parse(currentOrderingEl.textContent)
        } catch (e) {
          console.error("Failed to parse current ordering:", e)
        }
      }

      if (currentOrdering && currentOrdering.length > 0) {
        currentOrdering.forEach((field) => createSortRow(field))
      } else {
        createSortRow()
      }
    }

    const collectOrdering = () => {
      const rows = sortingRowsContainer.querySelectorAll(".sorting-row")
      const ordering = []

      rows.forEach((row) => {
        const field = row.querySelector(".sort-field").value
        const direction = row.querySelector(".sort-direction").value

        if (field) {
          ordering.push(direction + field)
        }
      })

      return ordering
    }

    form.querySelector(".add-columns")?.addEventListener("click", () => {
      moveOptions(availableSelect, selectedSelect, true)
    })
    form.querySelector(".remove-columns")?.addEventListener("click", () => {
      moveOptions(selectedSelect, availableSelect)
    })
    form.querySelector(".move-up")?.addEventListener("click", () => {
      moveOption(selectedSelect, "up")
    })
    form.querySelector(".move-down")?.addEventListener("click", () => {
      moveOption(selectedSelect, "down")
    })
    availableSelect?.addEventListener("dblclick", (e) => {
      if (e.target.tagName === "OPTION") {
        e.target.selected = true
        moveOptions(availableSelect, selectedSelect, true)
      }
    })
    selectedSelect?.addEventListener("dblclick", (e) => {
      if (e.target.tagName === "OPTION") {
        e.target.selected = true
        moveOptions(selectedSelect, availableSelect)
      }
    })

    addSortRowBtn?.addEventListener("click", () => {
      createSortRow()
    })

    const getEventSlug = () => {
      const pathParts = window.location.pathname.split("/")
      const eventIndex = pathParts.indexOf("event")
      if (eventIndex !== -1 && pathParts.length > eventIndex + 1) {
        return pathParts[eventIndex + 1]
      }
      return null
    }

    form.querySelector(".save-preferences")?.addEventListener("click", async () => {
      Array.from(selectedSelect.options).forEach((option) => {
        option.selected = true
      })

      const columns = Array.from(selectedSelect.options).map((opt) => opt.value)
      const ordering = collectOrdering()

      try {
        const eventSlug = getEventSlug()
        if (!eventSlug) {
          console.error("Could not determine event slug from URL")
          alert("An error occurred. Please try again.")
          return
        }
        const response = await fetch(`/orga/event/${eventSlug}/preferences/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("pretalx_csrftoken"),
          },
          body: JSON.stringify({
            table_name: tableName,
            columns: columns,
            ordering: ordering,
          }),
        })

        if (response.ok) {
          window.location.reload()
        } else {
          console.error("Failed to save table preferences")
          alert("Failed to save preferences. Please try again.")
        }
      } catch (error) {
        console.error("Error saving table preferences:", error)
        alert("An error occurred. Please try again.")
      }
    })

    form.querySelector(".reset-preferences")?.addEventListener("click", async () => {
      if (!confirm("Reset table columns to defaults?")) {
        return
      }

      try {
        const eventSlug = getEventSlug()
        if (!eventSlug) {
          console.error("Could not determine event slug from URL")
          alert("An error occurred. Please try again.")
          return
        }
        const response = await fetch(`/orga/event/${eventSlug}/preferences/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie('pretalx_csrftoken'),
          },
          body: JSON.stringify({
            table_name: tableName,
            reset: true,
          }),
        })

        if (response.ok) {
          window.location.reload()
        } else {
          console.error("Failed to reset table preferences")
          alert("Failed to reset preferences. Please try again.")
        }
      } catch (error) {
        console.error("Error resetting table preferences:", error)
        alert("An error occurred. Please try again.")
      }
    })

    if (sortingRowsContainer) {
      initializeSortRows()
    }
}

const handleTablePreferences = () => {
  document.querySelectorAll(".table-preferences-form").forEach((form) => setupPreferenceModal(form))
}

onReady(handleTablePreferences)
