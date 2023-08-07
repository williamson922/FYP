import React, { createContext, useState, useEffect } from "react";
import axios from "axios";
import Echo from 'laravel-echo';
import io from 'socket.io-client';

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
    
    useEffect(() => {
      Pusher.logToConsole =true;

    var pusher = new Pusher(import.meta.env.VITE_PUSHER_APP_KEY, {
      cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER,
      forceTLS: true,
    });

    var channel = pusher.subscribe('public-channel');
    channel.bind('event_apidata', function(data) {
      setPredictedData(data.data.predicted_data);
      setActualData(data.data.actual_data);
      setIsLoading(false);
    });
    },[]);
    
    const calculateTotalEnergy = () => {
      let total = 0;
      for (let entry of actualData) {
        total += entry['Total Power'];
      }
      setTotalEnergy((total/1000).toFixed(2));
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


