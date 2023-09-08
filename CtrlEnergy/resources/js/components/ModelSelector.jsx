import React, { useState, useEffect } from "react";
import axios from "axios";
import "../../css/modelSelector.css";

function ModelSelector() {
    const [modelType, setModelType] = useState("");
    const [versionOptions, setVersionOptions] = useState([]);
    const [selectedVersion, setSelectedVersion] = useState("");
    const [savingChanges, setSavingChanges] = useState(false);

    const handleSaveChanges = () => {
      if (selectedVersion) {
        setSavingChanges(true);
    
        // Send a POST request to the backend to update the selected version
        axios
          .post(`/api/set-model-version`, {
            modelType: modelType,
            selectedVersion: selectedVersion,
          })
          .then((response) => {
            // Handle the response from the backend
            console.log(response.data); 
            alert("Model Version is set properly");
          })
          .catch((error) => {
            console.error("Error setting model version:", error);
            alert("Error setting model version. Please try again.");
          })
          .finally(() => {
            setSavingChanges(false);
          });
      }
    };
    useEffect(() => {
        // Fetch version options based on selected model type
        if (modelType) {
            axios
                .get(`/api/get-model-versions/${modelType}`)
                .then((response) => {
                    console.log("Response:", response.data.versions);
                    // Update the state with the latest version options
                    setVersionOptions(response.data.versions);

                    // Find the selected version from the fetched data
                    const selectedVersionFromData = response.data.versions.find(
                        (version) => version.is_selected === 1
                    );
                    console.log(selectedVersionFromData);
                    if (selectedVersionFromData) {
                        console.log(selectedVersionFromData["version"]);
                        setSelectedVersion(selectedVersionFromData["version"]);
                    }
                })
                .catch((error) => {
                    console.error("Error fetching version options:", error);
                });
        }
    }, [modelType]);

    const handleModelTypeChange = (event) => {
        setModelType(event.target.value);
        setSelectedVersion(""); // Clear selected version when model type changes
    };

    const handleVersionChange = (event) => {
        setSelectedVersion(event.target.value);
    };

    return (
        <div className="container-setting">
            <h2 className="heading-container">Select Model and Version</h2>
            <div className="selectContainer-container">
                <label className="label-container">Model Type:</label>
                <select
                    className="select-container"
                    value={modelType}
                    onChange={handleModelTypeChange}
                >
                    <option value="">Select Model Type</option>
                    <option value="lstm">LSTM Weekday</option>
                    <option value="svr_weekend">SVR Weekend</option>
                    <option value="svr_holiday">SVR Holiday</option>
                </select>
            </div>
            <div className="selectContainer-container">
                <label className="label-container">Version:</label>
                <select
                    className="select-container"
                    value={selectedVersion}
                    onChange={handleVersionChange}
                >
                    <option value="">Select Version</option>
                    {versionOptions.map((model) => (
                        <option key={model.id} value={model.version}>
                            {model.version}
                        </option>
                    ))}
                </select>
            </div>
            <button
                className="save-button"
                onClick={handleSaveChanges}
                disabled={!selectedVersion || savingChanges}
            >
                {savingChanges ? "Saving..." : "Save Changes"}
            </button>
        </div>
    );
}

export default ModelSelector;
