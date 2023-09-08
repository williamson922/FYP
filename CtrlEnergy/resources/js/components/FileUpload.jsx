import React, { useState } from 'react';
import axios from 'axios';
import Papa from 'papaparse'; // Import the papaparse library

const FileUpload = () => {
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleFileSubmit = async () => {
        if (selectedFile) {
            try {
                const formData = new FormData();
                const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
                if (fileExtension === 'csv') {
                    console.log(selectedFile)
                    formData.append('file', selectedFile);

                    // Append a dummy value with a key
                    formData.append('dummyKey', 'dummyValue');

                    uploadFile(formData);
                } else {
                    alert('Unsupported file format. Please upload a CSV file.');
                }
            } catch (error) {
                alert('An error occurred during file upload.');
            }
        }
    };

    const uploadFile = async (formData) => {
        // Parse the CSV file
        const requiredColumns = [
            'Date/Time',
            'Voltage Ph-A Avg',
            'Voltage Ph-B Avg',
            'Voltage Ph-C Avg',
            'Current Ph-A Avg',
            'Current Ph-B Avg',
            'Current Ph-C Avg',
            'Power Factor Total',
        ];
        formData.forEach((value, key) => {
            console.log(`${key}: ${value}`);
        });
        
        Papa.parse(formData.get('file'), {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                const columns = results.meta.fields;
                // Check if all required columns are present
                const missingColumns = requiredColumns.filter(
                    (column) => !columns.includes(column)
                );
                    console.log(missingColumns);
                if (missingColumns.length === 0) {
                    // All required columns are present, proceed with upload
                    axios.post('http://localhost:5000/api/file-upload', formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data',
                        },
                    })
                    .then(() => {
                        alert('Upload successful');
                    })
                    .catch((error) => {
                        alert('Upload failed. Please try again later.');
                    });
                } else {
                    // Missing columns, show an alert to the user
                    alert('Missing columns: ' + missingColumns.join(', '));
                }
            },
        });
    };

    return (
        <div className="file-upload">
            <input type="file" onChange={handleFileChange} accept=".csv" />
            <button onClick={handleFileSubmit}>Upload CSV File</button>
        </div>
    );
};

export default FileUpload;