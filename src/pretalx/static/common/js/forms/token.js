// SPDX-FileCopyrightText: 2025-present Tobias Kunze
// SPDX-License-Identifier: Apache-2.0

const handleTokenTable = () => {
    const table = document.querySelector('#create-token #permission-endpoints')
    const presetField = document.querySelector('#id_permission_preset')
    table.style.display = (presetField.value === 'custom') ? 'flex' : 'none'
}

const setupPermissionCheckboxes = () => {
    const permissionTable = document.querySelector('#create-token #permission-endpoints table')
    if (!permissionTable) return

    const allPermissionCheckboxes = permissionTable.querySelectorAll('.permission-checkbox')
    const columnCheckboxes = permissionTable.querySelectorAll('.select-all-column')
    const rowCheckboxes = permissionTable.querySelectorAll('.select-all-row')
    const tableCheckbox = permissionTable.querySelector('.select-all-table')

    const updateCheckboxState = (checkbox, relatedCheckboxes) => {
        const allChecked = Array.from(relatedCheckboxes).every(cb => cb.checked)
        const someChecked = Array.from(relatedCheckboxes).some(cb => cb.checked)
        checkbox.checked = allChecked
        checkbox.indeterminate = !allChecked && someChecked
    }

    const updateAllSelectCheckboxes = () => {
        columnCheckboxes.forEach(columnCheckbox => {
            const permission = columnCheckbox.dataset.permission
            const relatedCheckboxes = permissionTable.querySelectorAll(`.permission-checkbox[data-permission="${permission}"]`)
            updateCheckboxState(columnCheckbox, relatedCheckboxes)
        })

        rowCheckboxes.forEach(rowCheckbox => {
            const endpoint = rowCheckbox.dataset.endpoint
            const relatedCheckboxes = permissionTable.querySelectorAll(`.permission-checkbox[data-endpoint="${endpoint}"]`)
            updateCheckboxState(rowCheckbox, relatedCheckboxes)
        })

        if (tableCheckbox) {
            updateCheckboxState(tableCheckbox, allPermissionCheckboxes)
        }
    }

    columnCheckboxes.forEach(columnCheckbox => {
        columnCheckbox.addEventListener('change', (e) => {
            const permission = columnCheckbox.dataset.permission
            const checkboxesToToggle = permissionTable.querySelectorAll(`.permission-checkbox[data-permission="${permission}"]`)
            checkboxesToToggle.forEach(cb => {
                cb.checked = columnCheckbox.checked
            })
            updateAllSelectCheckboxes()
        })
    })

    rowCheckboxes.forEach(rowCheckbox => {
        rowCheckbox.addEventListener('change', (e) => {
            const endpoint = rowCheckbox.dataset.endpoint
            const checkboxesToToggle = permissionTable.querySelectorAll(`.permission-checkbox[data-endpoint="${endpoint}"]`)
            checkboxesToToggle.forEach(cb => {
                cb.checked = rowCheckbox.checked
            })
            updateAllSelectCheckboxes()
        })
    })

    if (tableCheckbox) {
        tableCheckbox.addEventListener('change', (e) => {
            allPermissionCheckboxes.forEach(cb => {
                cb.checked = tableCheckbox.checked
            })
            updateAllSelectCheckboxes()
        })
    }

    allPermissionCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateAllSelectCheckboxes)
    })

    updateAllSelectCheckboxes()
}

const setupTokenTable = () => {
    const presetField = document.querySelector('#id_permission_preset')
    presetField.addEventListener('change', handleTokenTable)
    handleTokenTable()
    setupPermissionCheckboxes()
}

onReady(setupTokenTable)
