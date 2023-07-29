import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const [energyData, setEnergyData] = useState([]);
    const [totalEnergy, setTotalEnergy] = useState(0);
    const [predictedData, setPredictedData] = useState([]);
    const [isLoading, setIsLoading] = useState(true); // Add loading state

    const fetchData = async () => {
        try {
            const response = await axios.post("/api/bms-data");
            console.log(response.data.data);
            setEnergyData(response.data.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    };

    const sendDataToAPI = async () => {
        try {
            console.log("Sending data to API...", energyData);
            const response = await axios.post(
                "http://localhost:5000/api/predict",
                {
                    energyData,
                }
            );
            setPredictedData(response.data);
        } catch (error) {
            console.error("Error sending data:", error);
        }
    };

    const calculateTotalEnergy = () => {
        let total = 0;
        for (let entry of energyData) {
            total += entry.energy;
        }
        setTotalEnergy(total);
    };
    
    useEffect(() => {
        const fetchDataAndSendToAPI = async () => {
            try {
                await fetchData();
                sendDataToAPI();
                calculateTotalEnergy();
                setIsLoading(false);
            } catch (error) {
                console.error("Error in API requests:", error);
            }
        };

        fetchDataAndSendToAPI();
    }, []);

    // Define the context value
    const contextValue = {
        energyData,
        totalEnergy,
        predictedData,
    };
    // Show loading state until data is available
    if (isLoading) {
        return <div>Loading...</div>;
    }
    return (
        <DataContext.Provider value={contextValue}>
            {children}
        </DataContext.Provider>
    );
};

export { DataContext, DataProvider };
