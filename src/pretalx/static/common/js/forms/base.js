// SPDX-FileCopyrightText: 2019-present Tobias Kunze
// SPDX-License-Identifier: Apache-2.0

/* This script will be included on all pages with forms.
 * It adds a form handler warning when a form was modified when a tab is being closed,
 * and deactivates submit button in order to prevent accidental double submits.
 */

const originalData = {}

const handleUnload = (e) => {
    const form = e.target.form
    if (isDirty(form)) {
        e.preventDefault()
    }
}

const isDirty = (form) => {
    if (!!!form) return false
    if (Object.keys(originalData[form.id]).length === 0) return false
    const currentData = {}
    new FormData(form).forEach((value, key) => (currentData[key] = value))
    /* We have to compare all the current form's fields individually, because
     * there may be multiple forms with no/the same ID on the page. */
    for (const key in currentData) {
        if (JSON.stringify(currentData[key]) !== JSON.stringify(originalData[form.id][key])) {
            return true
        }
    }
    return false
}


// Make sure the main form doesn't have unsaved changes before leaving
const initFormChanges = (form) => {
    // Populate original data after a short delay to make sure the form is fully loaded
    // and that any script interactions have run
    setTimeout(() => {
        originalData[form.id] = {}
        new FormData(form).forEach((value, key) => (originalData[form.id][key] = value))
    }, 1000)

    form.addEventListener("submit", () => {
        window.removeEventListener("beforeunload", handleUnload)
    })
    window.addEventListener("beforeunload", handleUnload)
}

const initFormButton = (form) => {
    form.querySelectorAll("button[type=submit]").forEach(submitButton => {
        const submitButtonText = submitButton.textContent
        let lastSubmit = 0
        form.addEventListener("submit", () => {
            // We can't disable the button immediately, because then, the browser will
            // not send the button's value to the server. Instead, we'll just delay the
            // disabling a bit.
            submitButton.innerHTML = `<i class="fa fa-spinner animate-spin pr-0"></i> ${submitButtonText}`
            lastSubmit = Date.now()
            setTimeout(() => {
                submitButton.classList.add("disabled")
            }, 1)
        })

        // If people submit the form, then navigate back with the back button,
        // the button will still be disabled.
        // We can’t fix this on page load, because the browser will not actually load
        // the page again, and we can’t fix it via a single timeout, because that might
        // take place while we’re away from the page.
        // So instead, we’ll check periodically if the button is still disabled, and if
        // it’s been more than 5 seconds since the last submit, we’ll re-enable it.
        const checkButton = () => {
            if (submitButton.classList.contains("disabled")) {
                if (Date.now() - lastSubmit > 5000) {
                    submitButton.classList.remove("disabled")
                    submitButton.innerHTML = submitButtonText
                }
            }
        }
        window.setInterval(checkButton, 1000)
    })
}


const initTextarea = (element, other, limit) => {
    const submitButtons = Array.from(element.form.querySelectorAll("button, input[type=submit]")).filter(button => !button.disabled && button.type === "submit")
    const buttonsWithName = submitButtons.filter(button => button.name.length > 0)
    if (submitButtons.length <= 1 && buttonsWithName.length === 0) {
        // We use classic form submit whenever we can, to be on the safe side
        element.addEventListener("keydown", (ev) => {
            if (ev.key === "Enter" && ev.ctrlKey) {
                ev.preventDefault()
                // We need to remove the "are you sure" dialog that will show now otherwise
                window.removeEventListener("beforeunload", handleUnload)
                element.form.removeEventListener("submit", handleUnload)
                element.form.submit()
            }
        })
    } else {
        // But if there are multiple submit buttons, we click the first one,
        // to make sure the correct name/value is attached to the form data
        element.addEventListener("keydown", (ev) => {
            if (ev.key === "Enter" && ev.ctrlKey) {
                ev.preventDefault()
                submitButtons[0].click()
            }
        })
    }
}

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

/* Register handlers */
onReady(() => {
    document
        .querySelectorAll("form[method=post]")
        .forEach((form) => {
            initFormChanges(form)
            initFormButton(form)
        })
    document.querySelectorAll("form textarea").forEach(element => initTextarea(element))
    scrollToFormError()
})
