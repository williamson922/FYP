import React, { createContext, useState, useEffect } from "react";
import axios from "axios";
import Echo from 'laravel-echo';
import io from 'socket.io-client';
import { format, startOfMinute, addMinutes } from 'date-fns';
import { utcToZonedTime } from 'date-fns-tz';

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const [predictedData, setPredictedData] = useState([]);
    const [actualData, setActualData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null); // Add error state
    
     // Set a timeout to update isLoading to false if no data arrives within 10 seconds
  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsLoading(false);
    }, 5000); // 10 seconds
    
    return () => {
      clearTimeout(timeout); // Clear the timeout when the component unmounts
    };
  }, []);
//for loading the previous data if there is no data incoming at that time
useEffect(() => {
  // const today = new Date("2022-12-02T00:25:00");
  const today = new Date();
  const currentTime = today.getHours() * 60 + today.getMinutes(); // Convert current time to minutes
  const roundedTime = Math.floor(currentTime / 30) * 30; // Round down to nearest 30-minute interval
  console.log(today);
  console.log(currentTime);
  console.log(roundedTime);
  
  const cutoffTimeUTC = startOfMinute(addMinutes(today, -currentTime % 30)); // Subtract the remainder to round down
  console.log(cutoffTimeUTC);
  // Convert the UTC cutoff time to your local timezone
  const localTimeZone = 'Asia/Singapore'; // Replace with your local timezone
  const cutoffTime = utcToZonedTime(cutoffTimeUTC, localTimeZone);  
  console.log(cutoffTime);
  // Format cutoffTime as YYYY-MM-DD HH:MM:SS
  const formattedCutoffTime = format(cutoffTime, "yyyy-MM-dd'T'HH:mm:ss");
  console.log(formattedCutoffTime);

  Promise.all([
    axios.post('/api/get-data/actual', { 'Date/Time': formattedCutoffTime }),
    axios.post('/api/get-data/predict', { 'Date/Time': formattedCutoffTime })
  ])
    .then(([actual_data_response, predicted_data_response]) => {
      setActualData(actual_data_response.data);
      setPredictedData(predicted_data_response.data);
      setIsLoading(false);
    })
    .catch(error => {
      setError("Error fetching data: " + error.message);
      setIsLoading(false);
    });
}, []);

  useEffect(() => {
    Pusher.logToConsole = true;
  
    var pusher = new Pusher(import.meta.env.VITE_PUSHER_APP_KEY, {
      cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER,
      forceTLS: true,
    });
  
    var channel = pusher.subscribe('public-channel');
    channel.bind('event_apidata', async function (data) {
      console.log("Before HTTP actual:", data.data.actual_data);
  
      // Use Promise.all to wait for both API calls to complete
      const [actual_data_response, predicted_data_response] = await Promise.all([
        axios.post('/api/get-data/actual', { 'Date/Time': data.data.actual_data[0]['Date/Time'] }),
        axios.post('/api/get-data/predict', { 'Date/Time': data.data.actual_data[0]['Date/Time'] })
      ]);
  
      console.log("After HTTP actual:", actual_data_response);
      console.log("After HTTP predict:", predicted_data_response);
  
      setActualData(actual_data_response.data);
      setPredictedData(predicted_data_response.data);
      setIsLoading(false);
    });
  }, []);
    
    if(actualData.length>0){
      console.log("Actual:");
      console.log(actualData.map(entry => (entry['Total Power']/1000).toFixed(2)));
      }

      if(predictedData.length>0){
        console.log("Predicted:");
        console.log(predictedData.map(entry => (entry['predicted power']/1000).toFixed(2)));
        }
      
    // Show loading state or error message until data is available
    if (isLoading) {
      return <div>Loading...</div>;
    }
  
    if (error) {
      return <div>{error}</div>;
    }
  
    // Define the context value
    const contextValue = {
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