import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const [energyData, setEnergyData] = useState([
    {"Date/Time": "12/22/2021 00:00 AM",
    "Voltage Ph-A Avg": 246.91,
    "Voltage Ph-B Avg": 248.37,
    "Voltage Ph-C Avg": 246.88,
    "Current Ph-A Avg": 7.47,
    "Current Ph-B Avg": 4.44,
    "Current Ph-C Avg": 4.53,
    "Power Factor Total": 1}]);
    const [totalEnergy, setTotalEnergy] = useState(0);
    const [predictedData, setPredictedData] = useState([]);
    const [isLoading, setIsLoading] = useState(true); // Add loading state

    const fetchData = async () => {
        try {
          
            await axios.post("/api/bms-data",energyData).then((response)=>{
            setPredictedData(response.data.response)
            console.log(predictedData);
            });
            
        } catch (error) {
            console.error("Error fetching data:", error);
            setIsLoading(false); // Make sure to set isLoading to false even on error
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
                // sendDataToAPI();
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
