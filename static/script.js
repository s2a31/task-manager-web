// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Variable to store the currently dragged item
    let dragged;

    // Function to update placeholder display in task categories
    function updateAllPlaceholders() {
        // Define task categories
        const categories = ['pending-tasks', 'in-progress-tasks', 'completed-tasks'];
        // Placeholder messages for each category
        const placeholderMessages = {
            'pending-tasks': 'No Pending Tasks - Drop or Add tasks here',
            'in-progress-tasks': 'No In Progress Tasks - Drop or Add tasks here',
            'completed-tasks': 'No Completed Tasks - Drop or Add tasks here'
        };
        
        categories.forEach(categoryId => {
            const taskCategory = document.getElementById(categoryId);
            if (!taskCategory) return; // Skip if the category element is not found

            let placeholder = taskCategory.querySelector('.placeholder');
            const tasks = taskCategory.querySelectorAll('.task-item');

            if (!placeholder) {
                placeholder = document.createElement('div');
                placeholder.className = 'placeholder';
                taskCategory.appendChild(placeholder);
            }

            placeholder.innerText = placeholderMessages[categoryId];
            placeholder.style.display = tasks.length === 0 ? 'block' : 'none';
        });
    }

    // Initialize placeholders when the page is loaded
    const pendingTasks = document.getElementById('pending-tasks');
    if (pendingTasks) {
        updateAllPlaceholders();
    }

    // Drag and drop functionality for task items
    document.querySelectorAll('.task-item').forEach(function (item) {
        item.addEventListener('dragstart', function (event) {
            dragged = event.target;
        });
    });

    document.querySelectorAll('.task-category').forEach(function (category) {
        category.addEventListener('dragover', function (event) {
            event.preventDefault(); // Necessary to allow dropping
        });

        category.addEventListener('drop', async function (event) {
            event.preventDefault();
            let dropTarget = event.target.closest('.task-category');

            if (dropTarget) {
                let newStatus;
                switch (dropTarget.id) {
                    case 'pending-tasks': newStatus = 'Pending'; break;
                    case 'in-progress-tasks': newStatus = 'In Progress'; break;
                    case 'completed-tasks': newStatus = 'Completed'; break;
                }

                const taskId = dragged.id.split('-')[1];
                try {
                    const response = await fetch('/update_task_status', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: taskId, status: newStatus }),
                    });

                    if (response.ok) {
                        dragged.querySelector('.task-status').textContent = newStatus;
                        dropTarget.appendChild(dragged);
                        updateAllPlaceholders();
                    }
                } catch (error) {
                    console.error('Error updating task status:', error);
                }
            }
        });
    });

    // Delete task functionality
    document.querySelectorAll('.task-delete').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const taskId = this.action.split('/').pop();

            fetch('/delete/' + taskId, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('task-' + taskId).remove();
                    updateAllPlaceholders();
                } else {
                    console.error('Error:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Collapse the navbar when clicking outside of it
    document.addEventListener('click', function (event) {
        let navbarToggler = document.querySelector('.navbar-toggler');
        let isNavbarExpanded = navbarToggler.getAttribute('aria-expanded') === 'true';
        let clickedInsideNavbar = navbarToggler.contains(event.target) || document.querySelector('#navbarSupportedContent').contains(event.target);

        if (isNavbarExpanded && !clickedInsideNavbar) {
            navbarToggler.click();
        }
    });

    // Delete all tasks functionality
    const deleteAllTasksBtn = document.getElementById('delete-all-tasks-btn');
    if (deleteAllTasksBtn) {
        deleteAllTasksBtn.addEventListener('click', async function () {
            if (confirm('Are you sure you want to delete all tasks?')) {
                try {
                    const response = await fetch('/delete_all_tasks', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                    });

                    if (response.ok) {
                        document.querySelectorAll('.task-item').forEach((item) => item.remove());
                        updateAllPlaceholders();
                    }
                } catch (error) {
                    console.error('Error deleting all tasks:', error);
                }
            }
        });
    }

    // Delete account functionality
    const deleteAccountBtn = document.getElementById('delete-account-btn');
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', async function () {
            if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                try {
                    const response = await fetch('/delete_account', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                    });

                    if (response.ok) {
                        window.location.href = '/logout';
                    }
                } catch (error) {
                    console.error('Error deleting account:', error);
                }
            }
        });
    }

    // Password visibility toggle
    const togglePasswordButton = document.getElementById('togglePassword');
    if (togglePasswordButton) {
        togglePasswordButton.addEventListener('click', function (e) {
            const password = document.getElementById('password');
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    // Function to remove flash messages after a delay
    function removeFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(function (msg) {
            msg.remove();
        });
    }
    setTimeout(removeFlashMessages, 5000); // Remove flash messages after 5 seconds

    // Password strength checker
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('password-strength-bar');
    const strengthText = document.getElementById('password-strength-text');
    const strengthContainer = document.getElementById('password-check');

    if (passwordInput && strengthContainer) {
        passwordInput.addEventListener('input', function () {
            const password = passwordInput.value;
            let strength = 0;

            if (password.match(/[0-9]+/)) strength++;
            if (password.match(/[a-z]+/)) strength++;
            if (password.match(/[A-Z]+/)) strength++;
            if (password.match(/[^a-zA-Z0-9]+/)) strength++;

            switch (strength) {
                case 0: strengthBar.style.width = '0%'; strengthText.textContent = ''; break;
                case 1: strengthBar.style.width = '25%'; strengthBar.className = 'progress-bar bg-danger'; strengthText.textContent = 'Weak'; break;
                case 2: strengthBar.style.width = '50%'; strengthBar.className = 'progress-bar bg-warning'; strengthText.textContent = 'Moderate'; break;
                case 3: strengthBar.style.width = '75%'; strengthBar.className = 'progress-bar bg-info'; strengthText.textContent = 'Strong'; break;
                case 4: strengthBar.style.width = '100%'; strengthBar.className = 'progress-bar bg-success'; strengthText.textContent = 'Very Strong'; break;
            }
            strengthContainer.style.display = password ? 'block' : 'none';
        });
    }
});
