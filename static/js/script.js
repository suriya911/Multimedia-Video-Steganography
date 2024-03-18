// Function to remove the upload files
    var fileInput = document.querySelector('.file-input');
    fileInput.addEventListener('change', handleFileSelect, false);

    function handleFileSelect(event) {
        const files = event.target.files;

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const reader = new FileReader();

            reader.onload = function (e) {
                const listItem = document.createElement('li');
                listItem.className = 'file-item';

                const link = document.createElement('a');
                link.href = e.target.result;
                link.textContent = file.name;
                listItem.appendChild(link);

                const removeButton = document.createElement('span');
                removeButton.textContent = '❌';
                removeButton.style.cursor = 'pointer';
                removeButton.addEventListener('click', function() {
                    listItem.remove();
                    // Send a request to the server to remove the file
                    fetch('/remove_file', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ filename: file.name }),
                    })
                    .then(response => response.text())
                    .then(data => console.log(data))
                    .catch(error => console.error('Error:', error));
                });
                listItem.appendChild(removeButton);

                document.getElementById('file-list').appendChild(listItem);
            };

            reader.readAsDataURL(file);
        }
    }

// Function to download the file and redirect to home page after download completes
function downloadFileAndRedirect() {
    var zipUrl = '/downloads'; // URL for the Flask route that serves the zip file
    var redirectUrl = '/home'; // URL to redirect after download completes

    var link = document.createElement('a');
    link.href = zipUrl;
    link.download = 'folder.zip';  // Set the desired file name
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // When the download is complete, redirect to home page
    setTimeout(function() {
        window.location.href = redirectUrl;
    }, 1000); // Increase the timeout duration (e.g., 5000 milliseconds)
}

function downloadKeyAndRedirect() {
    var zipUrl = '/downloadkey'; // URL for the Flask route that serves the zip file
    var redirectUrl = '/home'; // URL to redirect after download completes

    var link = document.createElement('a');
    link.href = zipUrl;
    link.download = 'RSA_private.pem';  // Set the desired file name
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // When the download is complete, redirect to home page
    setTimeout(function() {
        window.location.href = redirectUrl;
    }, 1000); // Increase the timeout duration (e.g., 5000 milliseconds)
}
