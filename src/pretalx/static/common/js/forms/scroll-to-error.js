// SPDX-FileCopyrightText: 2025-present Tobias Kunze
// SPDX-License-Identifier: Apache-2.0

const scrollToFormError = () => {
    const alerts = document.querySelectorAll('.alert-danger')
    if (!alerts.length) return

    alerts.forEach(alert => {
        const errorFields = []

        // Find all form fields with errors
        const form = alert.closest('form')
        if (!form) return

        form.querySelectorAll('.invalid-feedback').forEach(feedback => {
            const formGroup = feedback.closest('.form-group')
            if (!formGroup) return

            const field = formGroup.querySelector('input, select, textarea')
            if (!field) return

            const label = formGroup.querySelector('label')
            const labelText = label ? label.textContent.trim() : field.name

            errorFields.push({
                field: field,
                label: labelText,
                error: feedback.textContent.trim(),
                formGroup: formGroup
            })
        })

        // If there are field errors, create clickable links in the alert
        if (errorFields.length > 0) {
            const existingList = alert.querySelector('.error-links')
            if (existingList) return // Already processed

            const ul = document.createElement('ul')
            ul.className = 'error-links'

            errorFields.forEach(({field, label, error, formGroup}) => {
                // Ensure the field has an ID
                if (!field.id) {
                    field.id = `error-field-${Math.random().toString(36).substr(2, 9)}`
                }

                const li = document.createElement('li')
                const a = document.createElement('a')
                a.href = `#${field.id}`
                a.textContent = `${label} – ${error}`
                a.style.color = 'inherit'
                a.style.textDecoration = 'underline'

                a.addEventListener('click', (e) => {
                    e.preventDefault()

                    // Find if this field is inside a tab panel
                    const tabPanel = field.closest('[role="tabpanel"]')
                    if (tabPanel) {
                        const tabPanelId = tabPanel.id
                        // Find the corresponding tab input
                        const tab = document.querySelector(`input[role="tab"][aria-controls="${tabPanelId}"]`)
                        if (tab && !tab.checked) {
                            tab.checked = true
                            // Trigger the tab change event to update UI
                            tab.dispatchEvent(new Event('change'))
                        }
                    }

                    // Scroll to the field
                    formGroup.scrollIntoView({ behavior: 'smooth', block: 'center' })

                    // Focus the field after scrolling
                    setTimeout(() => {
                        field.focus()
                    }, 300)
                })

                li.appendChild(a)
                ul.appendChild(li)
            })

            // Insert the list into the alert
            const alertContent = alert.querySelector('div')
            if (alertContent) {
                alertContent.appendChild(ul)
            }
        }
    })

    // Scroll to the first error on page load
    const firstErrorField = document.querySelector('.invalid-feedback')
    if (firstErrorField) {
        const formGroup = firstErrorField.closest('.form-group')
        const field = formGroup ? formGroup.querySelector('input, select, textarea') : null

        if (field) {
            // Check if the field is in a tab panel and activate it
            const tabPanel = field.closest('[role="tabpanel"]')
            if (tabPanel) {
                const tabPanelId = tabPanel.id
                const tab = document.querySelector(`input[role="tab"][aria-controls="${tabPanelId}"]`)
                if (tab && !tab.checked) {
                    tab.checked = true
                    tab.dispatchEvent(new Event('change'))
                }
            }

            // Scroll to the first error
            setTimeout(() => {
                formGroup.scrollIntoView({ behavior: 'smooth', block: 'center' })
            }, 100)
        }
    }
}

onReady(() => {
    scrollToFormError()
})
