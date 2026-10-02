document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('convert-form');
    const fileInput = document.getElementById('file-upload');
    const fileNameDisplay = document.getElementById('file-name');
    const dropZone = document.getElementById('drop-zone');
    const submitBtn = document.getElementById('submit-btn');
    const spinner = document.getElementById('spinner');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = `Selected: ${e.target.files[0].name} (${(e.target.files[0].size / 1024 / 1024).toFixed(2)} MB)`;
            fileNameDisplay.classList.add('text-indigo-600', 'font-semibold');
        } else {
            fileNameDisplay.textContent = 'Any supported format up to 50MB';
            fileNameDisplay.classList.remove('text-indigo-600', 'font-semibold');
        }
    });

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        
        // Trigger change event manually
        const event = new Event('change');
        fileInput.dispatchEvent(event);
    }, false);

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (fileInput.files.length === 0) {
            showError('Please select a file to convert.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        const selectedType = document.querySelector('input[name="conversion_type"]:checked').value;
        formData.append('conversion_type', selectedType);

        hideError();
        setLoading(true);

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Conversion failed. Please try again.');
            }

            // Get filename from Content-Disposition header if possible
            const disposition = response.headers.get('Content-Disposition');
            let filename = 'converted_file';
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) { 
                    filename = matches[1].replace(/['"]/g, '');
                }
            } else {
                // Determine extension based on type
                if(selectedType.includes('word')) filename += '.docx';
                else if(selectedType.includes('excel')) filename += '.xlsx';
                else if(selectedType.includes('ppt')) filename += '.pptx';
                else if(selectedType.includes('pdf')) filename += '.pdf';
            }

            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            // Reset form optionally
            // form.reset();
            // fileNameDisplay.textContent = 'Any supported format up to 50MB';

        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
            spinner.classList.remove('hidden');
            spinner.classList.add('inline-flex');
        } else {
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
            spinner.classList.add('hidden');
            spinner.classList.remove('inline-flex');
        }
    }

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }
});
