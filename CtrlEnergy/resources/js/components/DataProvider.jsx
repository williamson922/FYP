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
    const [totalEnergy, setTotalEnergy] = useState(0.0);
    const [predictedData, setPredictedData] = useState([]);
    const [actualData, setActualData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null); // Add error state
  
    useEffect(()=>{
      const checkQueueStatus = async() =>{
        try{
          const response = await axios.get('/api/queue/status');
          const hasPendingJobs =response.data.has_pending_jobs;
          if(hasPendingJobs){
            fetchData();
          } else {
            // Queue is empty, handle the case when no data is available
            console.log('Queue is empty')
          }
        } catch (error){
          console.error('Error checking queue status', error);
        }
      }
      const fetchData = async () => {
            try {
              const response = await axios.get("/api/api-data");
              setPredictedData(response.data.predictedData);
              setActualData(response.data.actualData);
            } catch (error) {
              console.error("Error fetching data:", error);
              setError("Error fetching data. Please try again later.");
            } finally {
              setIsLoading(false);
            }
          };
      const interval = setInterval(checkQueueStatus, 5000);

    // Clear the interval when the component unmounts to avoid memory leaks
        return () => clearInterval(interval); 
    // end of useEffect
    });
    
    
  
    const calculateTotalEnergy = () => {
      let total = 0;
      for (let entry of actualData) {
        total += entry['Total Power'].toFixed(2);
      }
      setTotalEnergy(total);
    };
  
  
    // Calculate total energy whenever actualData changes
    useEffect(() => {
      calculateTotalEnergy();
    }, [actualData]);
  
    // Log totalEnergy whenever it changes
    useEffect(() => {
      console.log("Total Energy Updated:", totalEnergy);
    }, [totalEnergy]);
  
    // Show loading state or error message until data is available
    if (isLoading) {
      return <div>Loading...</div>;
    }
  
    if (error) {
      return <div>{error}</div>;
    }
  
    // Define the context value
    const contextValue = {
      energyData,
      totalEnergy,
      predictedData,
      actualData,
    };
  
    return (
      <DataContext.Provider value={contextValue}>
        {children}
      </DataContext.Provider>
    );
  };
  
  export { DataContext, DataProvider };


